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

from aps.common.plot.image import get_average, get_peak_location, apply_transformations

from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from aps.beamline_driver.beam_management.facade import Beam, BeamProperties, MethodCallingType
from aps.beamline_driver.beam_management.abstract_beam_manager import WavefrontAnalysisBeamManager, WavefrontAnalysisProperties

from aps.wavefront_analysis.absolute_phase.factory import create_absolute_phase_analyzer
from aps.wavefront_analysis.driver.factory import create_wavefront_sensor


class EpicsWavefrontAnalyzerBeamManager(WavefrontAnalysisBeamManager):
    def __init__(self,
                 measurement_directory=None,
                 energy = 20000,
                 **kwargs):
        super(EpicsWavefrontAnalyzerBeamManager, self).__init__(method_calling_type=MethodCallingType.STANDARD, **kwargs)

        measurement_directory = measurement_directory if measurement_directory is not None else os.path.abspath(os.path.join(os.curdir, "wf_images"))

        self.__wavefront_sensor = create_wavefront_sensor(measurement_directory=measurement_directory,
                                                          file_name_prefix=kwargs.get("file_name_prefix", None),
                                                          detector_delay=kwargs.get("detector_delay", None))
        self.__wavefront_analyzer = create_absolute_phase_analyzer(data_collection_directory=measurement_directory,
                                                                   file_name_prefix=kwargs.get("file_name_prefix", None),
                                                                   energy=energy)

    def _get_beam(self, *args, **kwargs) -> Beam:
        units       = kwargs.get("units", "mm")
        verbose     = kwargs.get("verbose", True)
        save_images = kwargs.get("save_images", False)

        try:    self.__wavefront_sensor.restore_status()
        except: pass

        try:
            self.__wavefront_sensor.collect_single_shot_image(index=1)

            if self.__wavefront_sensor.get_configuration_file().IS_STREAM_AVAILABLE:
                image, _, _ = self.__wavefront_sensor.get_image_stream_data(units=units)
                self.__wavefront_analyzer.process_image(image_index=1, image_data=image, save_images=save_images, verbose=verbose)
            else:
                self.__wavefront_analyzer.process_image(image_index=1, image_data=None, save_images=save_images, verbose=verbose)

            wavefront_data = self.__wavefront_analyzer.back_propagate_wavefront(image_index=1,
                                                                                show_figure=False,
                                                                                save_result=False,
                                                                                verbose=verbose)
            try:    self.__wavefront_sensor.save_status()
            except: pass
            try:    self.__wavefront_sensor.end_collection()
            except: pass
        except Exception as e:
            try:    self.__wavefront_sensor.save_status()
            except: pass
            try:    self.__wavefront_sensor.end_collection()
            except: pass

            raise e

        return Beam(beam_data=wavefront_data)

    def get_hardware_device(self): return self.__wavefront_sensor

    def get_beam_properties(self, beam : Beam, **kwargs) -> BeamProperties:
        wavefront_data  = beam.data
        beam_properties = BeamProperties()

        beam_properties.set_parameter(WavefrontAnalysisProperties.INTENSITY_SIGMA_H, wavefront_data["sigma_x"]*1e6)
        beam_properties.set_parameter(WavefrontAnalysisProperties.INTENSITY_SIGMA_V, wavefront_data["sigma_y"]*1e6)
        beam_properties.set_parameter(WavefrontAnalysisProperties.INTENSITY_FWHM_H, wavefront_data["fwhm_x"]*1e6)
        beam_properties.set_parameter(WavefrontAnalysisProperties.INTENSITY_FWHM_V, wavefront_data["fwhm_y"]*1e6)
        beam_properties.set_parameter(WavefrontAnalysisProperties.INTENSITY_CENTROID_H, wavefront_data["wf_position_x"]*1e6)
        beam_properties.set_parameter(WavefrontAnalysisProperties.INTENSITY_CENTROID_V, wavefront_data["wf_position_y"]*1e6)
        beam_properties.set_parameter(WavefrontAnalysisProperties.FOCUS_Z_POSITION_H, wavefront_data["focus_z_position_x"]*1e3)
        beam_properties.set_parameter(WavefrontAnalysisProperties.FOCUS_Z_POSITION_V, wavefront_data["focus_z_position_y"]*1e3)

        coordinates_h = wavefront_data["coordinates_x"]*1e6
        coordinates_v = wavefront_data["coordinates_y"]*1e6

        beam_properties.set_parameter("coordinate_h", coordinates_h)
        beam_properties.set_parameter("coordinate_v", coordinates_v)

        # -------------------------------------------------------------------------------------------

        if wavefront_data["kind"] == "1D":
            intensity_h = wavefront_data["intensity_x"]
            intensity_v = wavefront_data["intensity_y"]
            beam_properties.set_parameter(WavefrontAnalysisProperties.INTENSITY_MAXIMUM,  np.average(np.max(intensity_h), np.max(intensity_v)))
            beam_properties.set_parameter(WavefrontAnalysisProperties.INTENSITY_INTEGRAL, np.average(np.sum(intensity_h), np.sum(intensity_v)))
        elif wavefront_data["kind"] == "2D":
            intensity_h = wavefront_data["integrated_intensity_x"]
            intensity_v = wavefront_data["integrated_intensity_y"]
            intensity   = wavefront_data["intensity"]
            beam_properties.set_parameter(self.get_beam_histogram_name(), intensity)
            beam_properties.set_parameter(WavefrontAnalysisProperties.INTENSITY_MAXIMUM,  np.max(intensity))
            beam_properties.set_parameter(WavefrontAnalysisProperties.INTENSITY_INTEGRAL, np.sum(intensity))
        else:
            raise ValueError("Kind not recognized")

        beam_properties.set_parameter(self.get_beam_histogram_name() + "_h", intensity_h)
        beam_properties.set_parameter(self.get_beam_histogram_name() + "_v", intensity_v)
        beam_properties.set_parameter("is_empty_beam",
                                      beam_properties.get_parameter(WavefrontAnalysisProperties.INTENSITY_INTEGRAL) <= \
                                      self._get_input_parameters().get_parameter("empty_beam_threshold", 0.0))

        self._plot_beam(beam_properties, **kwargs)

        return beam_properties

    def _plot_beam(self, beam_properties, **kwargs):
        if kwargs.get("save_image", False) or kwargs.get("show_beam", False):
            hh     = beam_properties.get_parameter("coordinate_h")
            vv     = beam_properties.get_parameter("coordinate_v")
            data_h = beam_properties.get_parameter(self.get_beam_histogram_name() + "_h")
            data_v = beam_properties.get_parameter(self.get_beam_histogram_name() + "_v")

            xrange = kwargs.get("xrange", None)
            yrange = kwargs.get("yrange", None)

            if xrange is None: xrange = [np.min(hh), np.max(hh)]
            if yrange is None: yrange = [np.min(vv), np.max(vv)]

            # Define a custom formatter function
            def custom_formatter(x, pos): return f'{x:.2f}'

            plt = kwargs.get("plt", None)

            if plt is None: fig = Figure(figsize=[10, 8])
            else:           fig = plt.figure(figsize=[10, 8])

            ax1, ax2, ax3 = fig.subplots(1, 3, gridspec_kw={'width_ratios': [2.5, 2.5, 1.0]}, sharey=True)
            ax3.set_axis_off()

            ax1.set_xlim(xrange[0], xrange[1])
            ax1.set_xticks(np.linspace(xrange[0], xrange[1], 6, endpoint=True))
            ax1.xaxis.set_major_formatter(FuncFormatter(custom_formatter))
            ax1.axvline(0, color="gray", ls="--", linewidth=1, alpha=0.7)
            ax1.set_xlabel("Horizontal ($\\mu$m)")
            ax1.set_ylabel("Intensity")
            ax1.plot(hh, data_h)

            ax2.set_xlim(yrange[0], yrange[1])
            ax2.set_xticks(np.linspace(yrange[0], yrange[1], 6, endpoint=True))
            ax2.xaxis.set_major_formatter(FuncFormatter(custom_formatter))
            ax2.axvline(0, color="gray", ls="--", linewidth=1, alpha=0.7)
            ax2.set_xlabel("Vertical ($\\mu$m)")
            ax2.plot(vv, data_v)

            labels = self.get_labels()

            text = (rf"{'fwhm(H)':<6}  = {beam_properties.get_parameter(labels[0]) : 3.1f} $\\mu$m" + "\n" +
                    rf"{'fwhm(V)':<6}  = {beam_properties.get_parameter(labels[1]) : 3.1f} $\\mu$m" + "\n" +
                    rf"{'sigma(H)':<6} = {beam_properties.get_parameter(labels[2]) : 3.1f} $\\mu$m" + "\n" +
                    rf"{'sigma(V)':<6} = {beam_properties.get_parameter(labels[3]) : 3.1f} $\\mu$m" + "\n" +
                    rf"{'z pos(H)':<6} = {beam_properties.get_parameter(labels[4]) : 6.3f} mm" + "\n" +
                    rf"{'z pos(V)':<6} = {beam_properties.get_parameter(labels[5]) : 6.3f} mm" + "\n" +
                    rf"{'pI':<10}      = {beam_properties.get_parameter(labels[6]) : 1.3e} ph")

            ax3.text(0.01, 0.7, text, color="black", alpha=0.9, fontsize=9,
                     bbox=dict(facecolor="white", edgecolor="gray", alpha=0.7), transform=ax3.transAxes)

            trial_num = kwargs.get("trial_num", None)
            if not trial_num is None: fig.gca().text(0.02, 0.95, str(trial_num), fontsize=10, color="blue", transform=ax1.transAxes)

            if kwargs.get("save_image", False):
                file_name = kwargs.get("file_name", None)
                if not file_name is None:
                    fig.savefig(os.path.join(kwargs.get("directory_name", os.path.abspath(os.curdir)), file_name))
                    fig.canvas.draw_idle()

            if kwargs.get("show_beam", False):
                plt = kwargs.get("plt", fig)
                plt.show()



