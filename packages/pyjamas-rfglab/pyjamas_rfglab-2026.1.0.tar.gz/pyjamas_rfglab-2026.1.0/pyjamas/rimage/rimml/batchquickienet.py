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

from typing import Optional

import numpy
from PyQt6 import QtGui, QtCore

from pyjamas.pjsthreads import ThreadSignals
from pyjamas.rimage.rimml.batchrecurrentneuralnet import BatchRecurrentNeuralNet
from pyjamas.rimage.rimutils import rimutils


class BatchQuickieNet(BatchRecurrentNeuralNet):
    def predict(self, slices: numpy.ndarray, indices: numpy.ndarray, progress_signal: Optional[ThreadSignals] = None,
                annotations: Optional[numpy.ndarray] = None, ids: Optional[list] = None) -> bool:

        # Make sure that the slices are in a 1D numpy array.
        indices = numpy.atleast_1d(indices)
        num_slices = len(indices)

        # For every slice ...
        for i, index in enumerate(indices):
            if slices.ndim > 2:
                theimage = slices[index].copy()
            elif slices.ndim == 2 and index == 0:
                theimage = slices.copy()

            if annotations is not None:
                print(f"Slice index {index}, slice number {i}")
                if index == 0:  # No previous mask to input
                    thepolygons = []
                    theids = []
                elif i == 0:  # Use polyline annotation made by user
                    thepolygons = annotations[index - 1]
                    theids = ids[index - 1]
                else:  # Use the previous classifier output
                    thepolygons = []
                    theids = []
                    for apoly, thisid in zip(self.object_arrays[index - 1], self.object_ids[index - 1]):
                        thispolygon = QtGui.QPolygonF()
                        for thepoint in apoly:
                            thispolygon.append(QtCore.QPointF(thepoint[0], thepoint[1]))
                        thepolygons.append(thispolygon)
                        theids.append(thisid)

                self.object_ids[index] = []
                self.object_arrays[index] = []
                self.prob_arrays[index] = []

                this_mask = rimutils.mask_from_polylines(imsize=theimage.shape, polylines=thepolygons, brushsz=0, labeled=True)

                this_object_array, this_prob_array = self.image_classifier.predict(theimage, this_mask)
                if len(this_object_array) > 0 and len(this_object_array) == len(theids):  # the second condition ensure the same number of objects in each frame. We should be able to remove that.
                    self.object_arrays[index] = this_object_array
                    self.prob_arrays[index] = this_prob_array
                    self.object_ids[index] = theids
                else:
                    print(f"The number of objects in slice {index} is {len(this_object_array)}, which is different from the number of objects in the previous slice ({len(theids)}).")
                    break

            else:
                return False

            if progress_signal is not None:
                progress_signal.emit(int((100 * (i + 1)) / num_slices))
        return True