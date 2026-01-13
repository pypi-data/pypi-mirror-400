import os
import math
import tempfile
import shutil
import nibabel as nib
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt
from totalsegmentator.python_api import totalsegmentator
from mosamatic2.core.tasks.task import Task
from mosamatic2.core.managers.logmanager import LogManager
from mosamatic2.core.utils import load_dicom

LOG = LogManager()

TOTAL_SEGMENTATOR_OUTPUT_DIR = os.path.join(tempfile.gettempdir(), 'total_segmentator_output')
TOTAL_SEGMENTATOR_TASK = 'total'
Z_DELTA_OFFSETS = {
    'vertebrae_L3': 0.333,
    'vertebrae_T4': 0.5,
}


class SelectSliceFromScansTask(Task):
    INPUTS = ['scans']
    PARAMS = ['vertebra']

    def __init__(self, inputs, params, output, overwrite):
        super(SelectSliceFromScansTask, self).__init__(inputs, params, output, overwrite)
        self._error_dir = os.path.split(self.output())[0]
        self._error_dir = os.path.join(self._error_dir, 'selectslicefromscanstask_errors')
        os.makedirs(self._error_dir, exist_ok=True)
        self._error_file = os.path.join(self._error_dir, 'errors.txt')
        with open(self._error_file, 'w') as f:
            f.write('Errors:\n\n')
        LOG.info(f'Error directory: {self._error_dir}')

    def write_error(self, message):
        LOG.error(message)
        with open(self._error_file, 'a') as f:
            f.write(message + '\n')

    def load_scan_dirs(self):
        scan_dirs = []
        for d in os.listdir(self.input('scans')):
            scan_dir = os.path.join(self.input('scans'), d)
            if os.path.isdir(scan_dir):
                scan_dirs.append(scan_dir)
        return scan_dirs
    
    def read_ct_series_sitk(self, scan_dir):
        reader = sitk.ImageSeriesReader()
        series_ids = reader.GetGDCMSeriesIDs(scan_dir)
        if not series_ids:
            raise ValueError(f'No DICOM series found in {scan_dir}')
        file_names = reader.GetGDCMSeriesFileNames(scan_dir, series_ids[0])
        reader.SetFileNames(file_names)
        img = reader.Execute()
        return img
    
    def resample_to_reference(self, moving: sitk.Image, reference: sitk.Image, is_label: bool) -> sitk.Image:
        interp = sitk.sitkNearestNeighbor if is_label else sitk.sitkLinear
        return sitk.Resample(
            moving,
            reference,
            sitk.Transform(),
            interp,
            0,  # default value
            moving.GetPixelID()
        )
    
    def centroid_x_index_from_mask(self, mask_ref: sitk.Image) -> int:
        # mask_ref must already be on the CT grid
        arr = sitk.GetArrayFromImage(mask_ref)  # shape: [z, y, x]
        idx = np.argwhere(arr > 0)
        if idx.size == 0:
            # fallback to true mid-sagittal
            size_x = mask_ref.GetSize()[0]
            return size_x // 2
        x_mean = int(round(idx[:, 2].mean()))
        return x_mean
    
    def z_index_from_physical_z(self, ct_img: sitk.Image, z_phys: float, x_index: int) -> int:
        # pick a y roughly mid (or better: y centroid of mask if you want)
        size = ct_img.GetSize()  # (x, y, z)
        y_index = size[1] // 2

        # Convert chosen (x_index, y_index, any z_index) -> physical, then replace z
        p = ct_img.TransformIndexToPhysicalPoint((x_index, y_index, size[2] // 2))
        phys_point = (p[0], p[1], z_phys)

        try:
            ix, iy, iz = ct_img.TransformPhysicalPointToIndex(phys_point)
        except RuntimeError:
            # if z_phys is slightly out of range, clamp later
            iz = None

        if iz is None:
            # clamp using physical bounds
            # safest crude clamp: convert all slice centers to physical z and find closest
            z_centers = []
            for k in range(size[2]):
                pk = ct_img.TransformIndexToPhysicalPoint((x_index, y_index, k))
                z_centers.append(pk[2])
            z_centers = np.array(z_centers)
            iz = int(np.argmin(np.abs(z_centers - z_phys)))

        iz = int(np.clip(iz, 0, size[2]-1))
        return iz
    
    def plot_sagittal_with_vertebra_overlay(self, scan_dir, mask_file, z_vert_phys_mm, out_png):
        ct = self.read_ct_series_sitk(scan_dir)
        vert_mask = sitk.ReadImage(mask_file)
        vert_mask_ref = self.resample_to_reference(vert_mask, ct, is_label=True)
        x_idx = self.centroid_x_index_from_mask(vert_mask_ref)
        z_idx = self.z_index_from_physical_z(ct, z_vert_phys_mm, x_idx)
        ct_arr = sitk.GetArrayFromImage(ct).astype(np.float32)
        mk_arr = sitk.GetArrayFromImage(vert_mask_ref).astype(np.uint8)
        sag_ct = ct_arr[:, :, x_idx]
        sag_mk = mk_arr[:, :, x_idx]
        vmin, vmax = np.percentile(sag_ct, (1, 99))
        sy = ct.GetSpacing()[1]  # y spacing (mm)
        sz = ct.GetSpacing()[2]  # z spacing (mm)
        aspect = sz / sy
        plt.figure(figsize=(7, 9))
        plt.imshow(sag_ct, cmap="gray", vmin=vmin, vmax=vmax, origin="lower", aspect=aspect)
        plt.imshow(sag_mk, alpha=0.35, origin="lower", aspect=aspect)
        plt.axhline(z_idx, linewidth=2)  # line across the vertebra axial slice position
        plt.title("Sagittal view with vertebral mask overlay + selected vertebra axial slice")
        plt.axis("off")
        plt.savefig(out_png, bbox_inches="tight", dpi=200)

    def extract_masks(self, scan_dir):
        os.makedirs(TOTAL_SEGMENTATOR_OUTPUT_DIR, exist_ok=True)
        totalsegmentator(input=scan_dir, output=TOTAL_SEGMENTATOR_OUTPUT_DIR, fast=True)
        if not os.path.isfile(os.path.join(TOTAL_SEGMENTATOR_OUTPUT_DIR, 'vertebrae_L3.nii.gz')):
            raise Exception(f'{scan_dir}: vertebrae_L3.nii.gz does not exist')
        # os.system(f'TotalSegmentator -i {scan_dir} -o {TOTAL_SEGMENTATOR_OUTPUT_DIR} --fast')

    def delete_total_segmentator_output(self):
        if os.path.exists(TOTAL_SEGMENTATOR_OUTPUT_DIR):
            shutil.rmtree(TOTAL_SEGMENTATOR_OUTPUT_DIR)

    def get_z_delta_offset_for_mask(self, mask_name):
        if mask_name not in Z_DELTA_OFFSETS.keys():
            return None
        return Z_DELTA_OFFSETS[mask_name]

    def find_slice(self, scan_dir, vertebra):
        if vertebra == 'L3':
            vertebral_level = 'vertebrae_L3'
        elif vertebra == 'T4':
            vertebral_level = 'vertebrae_T4'
        else:
            self.write_error(f'{scan_dir}: Unknown vertbra {vertebra}. Options are "L3" and "T4"')
            return None
        # Find Z-positions DICOM images
        z_positions = {}
        for f in os.listdir(scan_dir):
            f_path = os.path.join(scan_dir, f)
            try:
                p = load_dicom(f_path, stop_before_pixels=True)
                if p is not None and hasattr(p, "ImagePositionPatient"):
                    z_positions[p.ImagePositionPatient[2]] = f_path
            except Exception as e:
                self.write_error(f"{scan_dir}: Failed to load DICOM {f_path}: {e}")
                break
        if not z_positions:
            self.write_error(f"{scan_dir}: No valid DICOM z-positions found.")
            return None
        # Find Z-position vertebral image
        mask_file = os.path.join(TOTAL_SEGMENTATOR_OUTPUT_DIR, f'{vertebral_level}.nii.gz')
        if not os.path.exists(mask_file):
            self.write_error(f"{scan_dir}: Mask file not found: {mask_file}")
            return None
        try:
            mask_obj = nib.load(mask_file)
            mask = mask_obj.get_fdata()
            affine_transform = mask_obj.affine
        except Exception as e:
            self.write_error(f"{scan_dir}: Failed to load mask {mask_file}: {e}")
            return None
        indexes = np.array(np.where(mask == 1))
        if indexes.size == 0:
            self.write_error(f"{scan_dir}: No voxels found in mask {mask_file} for {vertebral_level}")
            return None        
        try:
            index_min = indexes.min(axis=1)
            index_max = indexes.max(axis=1)
        except ValueError as e:
            self.write_error(f"{scan_dir}: Invalid indexes array for {vertebral_level}: {e}")
            return None
        world_min = nib.affines.apply_affine(affine_transform, index_min)
        world_max = nib.affines.apply_affine(affine_transform, index_max)
        z_direction = affine_transform[:3, 2][2]
        if z_direction == 0:
            self.write_error(f"{scan_dir}: Affine z-direction is zero.")
            return None
        z_sign = math.copysign(1, z_direction)
        z_delta_offset = self.get_z_delta_offset_for_mask(vertebral_level)
        if z_delta_offset is None:
            return None
        z_delta = 0.333 * abs(world_max[2] - world_min[2]) # This needs to be vertebra-specific perhaps
        z_l3 = world_max[2] - z_sign * z_delta
        # Find closest L3 image in DICOM set
        positions = sorted(z_positions.keys())
        closest_file = None
        for z1, z2 in zip(positions[:-1], positions[1:]):
            if min(z1, z2) <= z_l3 <= max(z1, z2):
                closest_z = min(z_positions.keys(), key=lambda z: abs(z - z_l3))
                closest_file = z_positions[closest_z]
                LOG.info(f'Closest image: {closest_file}')
                break
        if closest_file is None:
            self.write_error(f"{scan_dir}: No matching slice found.")
        return closest_file, z_l3
    
    def run(self):
        scan_dirs = self.load_scan_dirs()
        vertebra = self.param('vertebra')
        nr_steps = len(scan_dirs)
        for step in range(nr_steps):
            scan_dir = scan_dirs[step]
            scan_name = os.path.split(scan_dir)[1]
            errors = False
            LOG.info(f'Processing {scan_dir}...')
            try:
                self.extract_masks(scan_dir)
            except Exception as e:
                self.write_error(f'{scan_dir}: Could not extract masks [{str(e)}]. Skipping scan...')
                errors = True
            if not errors:
                file_path, z_vert = self.find_slice(scan_dir, vertebra)
                if file_path is not None:
                    extension = '' if file_path.endswith('.dcm') else '.dcm'
                    target_file_path = os.path.join(self.output(), vertebra + '_' + scan_name + extension)
                    shutil.copyfile(file_path, target_file_path)
                    mask_file = os.path.join(TOTAL_SEGMENTATOR_OUTPUT_DIR, f'vertebrae_{vertebra}.nii.gz')
                    output_png = os.path.join(self.output(), f"{vertebra}_{scan_name}_sagittal.png")
                    self.plot_sagittal_with_vertebra_overlay(scan_dir, mask_file, z_vert, output_png)
                else:
                    self.write_error(f'{scan_dir}: Could not find slice for vertebral level: {vertebra}')
                    errors = True
                self.delete_total_segmentator_output()
            if errors:
                LOG.info(f'Copying problematic scan {scan_dir} to error directory: {self._error_dir}')
                scan_error_dir = os.path.join(self._error_dir, scan_name)
                shutil.copytree(scan_dir, scan_error_dir)
            self.set_progress(step, nr_steps)