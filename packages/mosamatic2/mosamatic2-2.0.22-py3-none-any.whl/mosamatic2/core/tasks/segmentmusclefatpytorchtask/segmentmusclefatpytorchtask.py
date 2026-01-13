import os
import torch
import numpy as np
import matplotlib.pyplot as plt

import models

from mosamatic2.core.tasks.task import Task
from mosamatic2.core.utils import (
    normalize_between,
    get_pixels_from_dicom_object,
    convert_labels_to_157,
)
from mosamatic2.core.data.multidicomimage import MultiDicomImage
from mosamatic2.core.data.dicomimage import DicomImage
from mosamatic2.core.tasks.segmentmusclefatpytorchtask.paramloader import ParamLoader

DEVICE = 'cpu'


class SegmentMuscleFatPyTorchTask(Task):
    INPUTS = [
        'images', 
        'model_files'
    ]
    PARAMS = ['model_version']

    def __init__(self, inputs, params, output, overwrite=True):
        super(SegmentMuscleFatPyTorchTask, self).__init__(inputs, params, output, overwrite)

    def load_images(self):        
        image_data = MultiDicomImage()
        image_data.set_path(self.input('images'))
        if image_data.load():
            return image_data
        raise RuntimeError('Could not load images')

    def load_model_files(self):
        model_files = []
        for f in os.listdir(self.input('model_files')):
            f_path = os.path.join(self.input('model_files'), f)
            if f_path.endswith('.pt') or f_path.endswith('.json'):
                model_files.append(f_path)
        if len(model_files) != 3:
            raise RuntimeError(f'Found {len(model_files)} model files. This should be 3!')
        return model_files

    def load_models_and_params(self, model_files, model_version):
        # First load params.json because it is needed to instantiate the models
        params = None
        for f_path in model_files:
            f_name = os.path.split(f_path)[1]
            if f_name == f'params-{str(model_version)}.json':
                params = ParamLoader(f_path)
                break
        if params is None:
            raise RuntimeError('Could not load parameters')
        # Next, load models
        model, contour_model = None, None
        for f_path in model_files:
            f_name = os.path.split(f_path)[1]
            if f_name == f'model-{str(model_version)}.pt':
                # model = models.AttentionUNet(params, 4).to(device=DEVICE)
                model = models.UNet(params, 4).to(device=DEVICE)
                model.load_state_dict(torch.load(f_path, weights_only=False, map_location=torch.device(DEVICE)))
                model.eval()
            elif f_name == f'contour_model-{str(model_version)}.pt':
                contour_model = models.UNet(params, 2).to(device=DEVICE)
                contour_model.load_state_dict(torch.load(f_path, weights_only=False, map_location=torch.device(DEVICE)))
                contour_model.eval()
            else:
                pass
        return model, contour_model, params
    
    def extract_contour(self, image, contour_model):
        with torch.no_grad():
            # Create 4D Tensor input
            input = np.expand_dims(image, 0)
            input = np.expand_dims(input, 0)
            input = torch.Tensor(input)
            input = input.to(DEVICE, dtype=torch.float)
            # Predict
            prediction = contour_model(input)
            prediction = torch.argmax(prediction, axis=1)
            prediction = prediction.squeeze()
            prediction = prediction.detach().cpu().numpy()
            result = image * prediction
        return result
    
    def show_result(self, result):
        fig = plt.figure()
        plt.imshow(result, cmap='gray')
        plt.savefig("/Users/ralph/result.png")
    
    def segment_muscle_and_fat(self, image, model):
        input = np.expand_dims(image, 0)
        input = np.expand_dims(input, 0)
        input = torch.Tensor(input)
        input = input.to(DEVICE, dtype=torch.float)
        segmentation = model(input)
        segmentation = torch.argmax(segmentation, axis=1)
        segmentation = segmentation.squeeze()
        segmentation = segmentation.detach().cpu().numpy()
        return segmentation
    
    def process_file(self, image, output_dir, model, contour_model, params):
        assert isinstance(image, DicomImage)
        pixels = get_pixels_from_dicom_object(image.object(), normalize=True)
        if contour_model:
            pixels = normalize_between(pixels, params.dict['lower_bound'], params.dict['upper_bound'])
            pixels = self.extract_contour(pixels, contour_model)
        pixels = pixels.astype(np.float32)
        segmentation = self.segment_muscle_and_fat(pixels, model)
        segmentation = convert_labels_to_157(segmentation)
        segmentation_file_name = os.path.split(image.path())[1]
        segmentation_file_path = os.path.join(output_dir, f'{segmentation_file_name}.seg.npy')
        np.save(segmentation_file_path, segmentation)

    def run(self):
        image_data = self.load_images()
        model_files = self.load_model_files()
        model_version = self.param('model_version')
        model, contour_model, params = self.load_models_and_params(model_files, model_version)
        images = image_data.images()
        nr_steps = len(images)
        for step in range(nr_steps):
            self.process_file(images[step], self.output(), model, contour_model, params)
            self.set_progress(step, nr_steps)