#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------- #
# Copyright (c) 2025, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2025. UChicago Argonne, LLC. This software was produced       #
# under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
# Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
# U.S. Department of Energy. The U.S. Government has rights to use,       #
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
# UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
# modified to produce derivative works, such modified software should     #
# be clearly marked, so as not to confuse it with the version available   #
# from ANL.                                                               #
#                                                                         #
# Additionally, redistribution and use in source and binary forms, with   #
# or without modification, are permitted provided that the following      #
# conditions are met:                                                     #
#                                                                         #
#     * Redistributions of source code must retain the above copyright    #
#       notice, this list of conditions and the following disclaimer.     #
#                                                                         #
#     * Redistributions in binary form must reproduce the above copyright #
#       notice, this list of conditions and the following disclaimer in   #
#       the documentation and/or other materials provided with the        #
#       distribution.                                                     #
#                                                                         #
#     * Neither the name of UChicago Argonne, LLC, Argonne National       #
#       Laboratory, ANL, the U.S. Government, nor the names of its        #
#       contributors may be used to endorse or promote products derived   #
#       from this software without specific prior written permission.     #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# ----------------------------------------------------------------------- #
import os
import numpy as np
from scipy.ndimage.measurements import center_of_mass

from aps.beamline_driver.beam_management.facade import Beam, BeamProperties, MethodCallingType
from aps.beamline_driver.beam_management.abstract_beam_manager import (DirectBeamImageBeamManager,
                                                                                   DirectBeamImageProperties)
from aps.beamline_driver.common.utility import calculate_projections_over_noise

from aps.common.driver.beamline.generic_camera import GenericCamera, CameraInitializationFile

class EpicsCameraDirectBeamManager(DirectBeamImageBeamManager):
    def __init__(self, camera : GenericCamera = None, measurement_directory=None, **kwargs):
        super(EpicsCameraDirectBeamManager, self).__init__(method_calling_type=MethodCallingType.STANDARD, **kwargs)

        if not camera is None:
            self.__camera = camera
        else:
            if not CameraInitializationFile.is_initialized():
                CameraInitializationFile.initialize()
                CameraInitializationFile.store()

            self.__camera = GenericCamera(measurement_directory=(measurement_directory if not measurement_directory is None else os.path.abspath(os.curdir)))

    def get_beam(self, *args, **kwargs) -> Beam:
        try:    self.__camera.save_status() # collect beamline original setups
        except: pass

        image_index  = kwargs.get("image_index", 1)
        index_digits = kwargs.get("index_digits", 4)
        units        = kwargs.get("units", "mm")
        use_stream   = kwargs.get("use_stream", False)

        try:
            self.__camera.collect_single_shot_image(index=image_index)

            if use_stream: image, coordinate_h, coordinate_v = self.__camera.get_image_stream_data(units=units)
            else:          image, coordinate_h, coordinate_v = self.__camera.get_image_data(image_index=image_index, index_digits=index_digits, units=units)

            beam_data = {}
            beam_data["coordinate_h"] = coordinate_h
            beam_data["coordinate_v"] = coordinate_v
            beam_data["image"]        = image

            try:    self.__camera.end_collection()
            except: pass
            try:    self.__camera.restore_status() # restore beamline original setups
            except: pass

            return Beam(beam_data=beam_data)
        except Exception as e:
            try:    self.__camera.end_collection()
            except: pass
            try:    self.__camera.restore_status() # restore beamline original setups
            except: pass

            raise e

    def get_hardware_device(self): return self.__camera

    def get_beam_properties(self, beam : Beam, **kwargs) -> BeamProperties:
        auto_crop_defocused_image        = kwargs.get("auto_crop_defocused_image", False)

        if not auto_crop_defocused_image:
            return super(EpicsCameraDirectBeamManager, self).get_beam_properties(beam=beam, **kwargs)
        else:
            crop_strip_width = kwargs.get("crop_strip_width", 50)
            crop_threshold   = kwargs.get("crop_threshold", None)

            coordinate_h = beam.data["coordinate_h"]
            coordinate_v = beam.data["coordinate_v"]
            image        = beam.data["image"]

            if crop_threshold is None: crop_threshold = np.average(image)

            footprint = np.ones(image.shape) * (image > crop_threshold)

            center = center_of_mass(footprint)
            center_x, center_y = int(center[0]), int(center[1])

            # find the boundary
            n_width = crop_strip_width
            strip_x = np.array(np.sum(footprint[:, center_y - n_width: center_y + n_width], axis=1))
            strip_y = np.flip(np.array(np.sum(footprint[center_x - n_width: center_x + n_width, :], axis=0)))
            threshold_x = 0.5 * np.max(strip_x)
            threshold_y = 0.5 * np.max(strip_y)

            left_x = np.amin(np.where(strip_x > threshold_x))
            right_x = np.amax(np.where(strip_x > threshold_x))
            up_y = np.amin(np.where(strip_y > threshold_y))
            down_y = np.amax(np.where(strip_y > threshold_y))

            center_x = coordinate_h[center_x]
            center_y = coordinate_v[self.__camera.get_configuration_file().IMAGE_SIZE_PIXEL_V - center_y]  # image is flipped vertically
            width_x = (right_x - left_x) * self.__camera.get_configuration_file().PIXEL_SIZE * 1e3
            width_y = (down_y - up_y) * self.__camera.get_configuration_file().PIXEL_SIZE * 1e3

            print("Crop Region: Center (HxV) =", round(center_x, 4), round(center_y, 4),
                  "mm, Dimension (HxV) =", round(width_x, 4), round(width_y, 4), "mm")

            kwargs["calculate_projections_over_noise"] = False
            beam_properties = super(EpicsCameraDirectBeamManager, self).get_beam_properties(beam=beam, **kwargs)

            beam_properties.set_parameter(DirectBeamImageProperties.CENTROID_H, center_x)
            beam_properties.set_parameter(DirectBeamImageProperties.CENTROID_V, center_y)
            beam_properties.set_parameter(DirectBeamImageProperties.FWHM_H,     width_x)
            beam_properties.set_parameter(DirectBeamImageProperties.FWHM_V,     width_y)

            return beam_properties

    def _get_beam_histogram(self, beam : Beam, **kwargs) -> BeamProperties:
        coordinate_h = beam.data["coordinate_h"]
        coordinate_v = beam.data["coordinate_v"]
        histogram    = beam.data["image"]

        if kwargs.get("denoise", False):
            denoise_algorithm = kwargs.get("denoise_algorithm", "simple")

            if denoise_algorithm == "simple":
                noise_mask      = kwargs.get("noise_mask", [0, 10, 0, 10])
                noise_threshold = kwargs.get("noise_threshold", 1.0)
                bad_pixels      = kwargs.get("bad_pixels", [])

                histogram, histogram_h, histogram_v = calculate_projections_over_noise(histogram=histogram,
                                                                                       noise_mask=noise_mask,
                                                                                       noise_threshold=noise_threshold,
                                                                                       bad_pixels=bad_pixels)
            else:
                raise ValueError("Denoise algorithm not recognized")
        else:
            histogram_h = histogram.sum(axis=1)
            histogram_v = histogram.sum(axis=0)

        return BeamProperties(histogram=histogram,
                              coordinate_h=coordinate_h,
                              coordinate_v=coordinate_v,
                              histogram_h=histogram_h,
                              histogram_v=histogram_v)
