"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import skimage.morphology as sm
import skimage.measure as sme
import scipy.ndimage as ndimage
import scipy.stats as stats

import keras
import numpy
import torch

from pyjamas.rimage.rimml.classifier_types import classifier_types
from pyjamas.rimage.rimutils import rimutils

from pyjamas.rimage.rimml.rimrescunet import ReSCUNet


class QuickieNet(ReSCUNet):
    CLASSIFIER_TYPE = classifier_types.QUICKIENET.value
    def predict(self, image: numpy.ndarray, prev_mask: numpy.ndarray) -> (numpy.ndarray, numpy.ndarray):
        if image is None or image is False:
            return False
        if prev_mask is None or prev_mask is False:
            return False

        if image.ndim == 3:
            image = image[0, :, :]
        if prev_mask.ndim == 3:
            prev_mask = prev_mask[0, :, :]

        if prev_mask.dtype == bool:
            prev_labels = sme.label(prev_mask, connectivity=2)
        else:
            prev_labels = prev_mask.copy()
            prev_mask = prev_mask > 0
        prev_ids = numpy.unique(prev_labels[prev_mask])

        testImage = image / self.scaler

        image_input = self.classifier.input[0]
        prev_mask_input = self.classifier.input[2]
        softmax_output = self.classifier.get_layer('unet-activation').output
        predictor = keras.Model(inputs=[image_input, prev_mask_input], outputs=softmax_output)

        with torch.no_grad():  # no gradient tracking (faster inference).
            # Keep these on GPU as PyTorch tensors for faster computation
            device = 'cpu'
            if torch.mps.is_available():
                device = torch.device("mps")
            elif torch.cuda.is_available():
                device = torch.device("cuda")

            testLabel = torch.zeros(testImage.shape, dtype=torch.bool, device=device)
            testProb = torch.zeros(testImage.shape, dtype=torch.float32, device=device)

            half_width = int(self.train_image_size[1] / 2)
            half_height = int(self.train_image_size[0] / 2)

            for animage, therow, thecol in rimutils.generate_subimages(testImage, self.train_image_size[0:2],
                                                                       self.step_sz, True):
                prev_mask_subimage = prev_mask[(therow - half_height):(therow + half_height),
                                               (thecol - half_width):(thecol + half_width)]

                if numpy.sum(prev_mask_subimage) == 0:  # empty prev mask in this subimage, skip area
                    continue

                yhat = predictor([numpy.expand_dims(animage, axis=0), numpy.expand_dims(prev_mask_subimage, axis=0)], training=False)
                yhat_class = torch.argmax(yhat[0], dim=-1)
                p = torch.amax(yhat[0], dim=-1)

                testLabel[(therow - half_height):(therow + half_height), (thecol - half_width):(thecol + half_width)] \
                    = torch.logical_or(testLabel[(therow - half_height):(therow + half_height),
                                       (thecol - half_width):(thecol + half_width)], yhat_class)
                testProb[(therow - half_height):(therow + half_height), (thecol - half_width):(thecol + half_width)] = p

            # Only convert to NumPy and leave the GPU at the very end
            testLabel = testLabel.cpu().numpy()
            testProb = testProb.cpu().numpy()

        testLabel = ndimage.binary_fill_holes(testLabel)
        labelled_mask = sme.label(testLabel, connectivity=2)
        region_ids = numpy.unique(labelled_mask[labelled_mask > 0])

        if len(region_ids) > 1:
            self.object_array = numpy.empty(prev_ids.shape, dtype=object)

            for index, this_id in enumerate(prev_ids):
                this_region_before = prev_labels == this_id
                # Find the mode of the prev_labels images masked with the current label object, this_region
                best_id = stats.mode(labelled_mask[this_region_before]).mode

                testLabel_singleobject = numpy.zeros(testLabel.shape, dtype=numpy.bool)
                testLabel_singleobject[labelled_mask==best_id] = True

                thecontour = []

                if self.erosion_width is not None and self.erosion_width != 0:
                    thecontour = rimutils.extract_contours(
                        sm.dilation(sm.label(sm.binary_erosion(testLabel_singleobject, sm.footprint_rectangle((self.erosion_width, self.erosion_width))), connectivity=2),
                                    sm.footprint_rectangle((self.erosion_width, self.erosion_width))), fully_connected='high')
                else:
                    thecontour = rimutils.extract_contours(testLabel_singleobject, fully_connected='high')

                if len(thecontour) == 1:  # switch this to > 0 to allow returning more than one contour.
                    self.object_array[index] = numpy.squeeze(numpy.asarray(thecontour, dtype=object))
                else:
                    print(f"Error extracting a contour for polyline id {this_id}. Try re-prompting or smoothing the contour?")
                    return numpy.empty(0), numpy.empty(0)
        self.prob_array = testProb

        return self.object_array, self.prob_array
