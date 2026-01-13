import os
from mosamatic2.core.tasks.task import Task
from mosamatic2.core.managers.logmanager import LogManager
from mosamatic2.core.data.multidicomimage import MultiDicomImage
from mosamatic2.core.utils import (
    convert_numpy_array_to_png_image, 
    convert_muscle_mask_to_myosteatosis_map,
    get_pixels_from_dicom_object,
    AlbertaColorMap, 
    load_numpy_array,
)

LOG = LogManager()


class CreatePngsFromSegmentationsTask(Task):
    INPUTS = ['images', 'segmentations']
    PARAMS = [
        'fig_width', 
        'fig_height'
    ]

    def __init__(self, inputs, params, output, overwrite=True):
        super(CreatePngsFromSegmentationsTask, self).__init__(inputs, params, output, overwrite)

    def load_images(self):
        image_data = MultiDicomImage()
        image_data.set_path(self.input('images'))
        if image_data.load():
            return image_data
        raise RuntimeError('Could not load images')

    def load_segmentations(self):
        segmentations = []
        for f in os.listdir(self.input('segmentations')):
            f_path = os.path.join(self.input('segmentations'), f)
            if f.endswith('.seg.npy'):
                segmentations.append(f_path)
        if len(segmentations) == 0:
            raise RuntimeError('Input directory has no segmentation files')
        return segmentations
    
    def collect_img_seg_pairs(self, images, segmentations, file_type='npy'):
        file_type = '.tag' if file_type == 'tag' else '.seg.npy'
        img_seg_pairs = []
        for image in images:
            f_img_path = image.path()
            f_img_name = os.path.split(f_img_path)[1]
            for f_seg_path in segmentations:
                f_seg_name = os.path.split(f_seg_path)[1]
                if file_type == '.seg.npy':
                    f_seg_name = f_seg_name.removesuffix(file_type)
                    if f_seg_name == f_img_name:
                        img_seg_pairs.append((image, f_seg_path))
                elif file_type == '.tag':
                    f_seg_name = f_seg_name.removesuffix(file_type).removesuffix('.dcm')
                    f_img_name = f_img_name.removesuffix('.dcm')
                    if f_seg_name == f_img_name:
                        img_seg_pairs.append((image, f_seg_path))
                else:
                    raise RuntimeError('Unknown file type')
        return img_seg_pairs

    def run(self):
        images = self.load_images()
        segmentations = self.load_segmentations()
        img_seg_pairs = self.collect_img_seg_pairs(images.images(), segmentations, 'npy')
        # nr_steps = len(segmentations)
        nr_steps = len(img_seg_pairs)
        for step in range(nr_steps):
            segmentation = img_seg_pairs[step][1]
            segmentation_name = os.path.split(segmentation)[1]
            segmentation_image = load_numpy_array(segmentation)
            if segmentation_image is not None:
                png_file_name = segmentation_name + '.png'
                convert_numpy_array_to_png_image(
                    segmentation_image, 
                    self.output(),
                    AlbertaColorMap(), 
                    png_file_name,
                    fig_width=int(self.param('fig_width')),
                    fig_height=int(self.param('fig_height')),
                )
                image = img_seg_pairs[step][0]
                image = get_pixels_from_dicom_object(image.object(), normalize=True)
                png_file_name = segmentation_name + '_myosteatosis.png'
                convert_muscle_mask_to_myosteatosis_map(
                    image,
                    segmentation_image,
                    self.output(),
                    png_file_name,
                )
            else:
                LOG.warning(f'File {segmentation} is not a valid NumPy array file')
            self.set_progress(step, nr_steps)
