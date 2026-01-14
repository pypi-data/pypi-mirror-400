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

from aps.beamline_driver.beam_management.control_systems.common import Directions, ScanParameters
from aps.beamline_driver.beam_management.facade import Beam, BeamProperties, MethodCallingType
from aps.beamline_driver.beam_management.abstract_beam_manager import DirectBeamImageBeamManager, DirectBeamImageProperties

from aps.common.plot.image import get_average, get_peak_location, get_fwhm, get_sigma

from epics import PV

from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

import time

class EpicsScanPVs:
    def __init__(self, pv_names : dict):
        self.__counts       = PV(pv_names["counts"])
        self.__acquire      = PV(pv_names["acquire"])
        self.__acquire_time = PV(pv_names["acquire_time"])
        self.__motor_h      = PV(pv_names["motor_h"])
        self.__motor_v      = PV(pv_names["motor_v"])
        self.__motor_h_moving      = PV(pv_names["motor_h_moving"])
        self.__motor_v_moving      = PV(pv_names["motor_v_moving"])
        self.__autocount    = PV(pv_names["autocount"])

    @property
    def counts(self): return self.__counts
    @property
    def acquire(self): return self.__acquire
    @property
    def acquire_time(self): return self.__acquire_time
    @property
    def motor_h(self): return self.__motor_h
    @property
    def motor_v(self): return self.__motor_v
    @property
    def motor_h_moving(self): return self.__motor_h_moving
    @property
    def motor_v_moving(self): return self.__motor_v_moving
    @property
    def autocount(self): return self.__autocount

MOTOR_WAIT_TIME = 0.1
ACQUIRE_WAIT_TIME = 0.1

class EpicsScanDirectBeamManager(DirectBeamImageBeamManager):
    def __init__(self, pvs: EpicsScanPVs, **kwargs):
        super(EpicsScanDirectBeamManager, self).__init__(method_calling_type=MethodCallingType.STANDARD, **kwargs)

        self.__pvs = pvs

    def get_beam(self, *args, **kwargs) -> Beam:
        self.__pvs.autocount.put(1)

        direction         = kwargs.get("direction", Directions.BOTH)
        parameters        = kwargs.get("parameters", [ScanParameters(), ScanParameters()])

        beam_data = {}

        def get_profile(coord, scan):
            derivative    = np.gradient(scan, coord)
            # the sign of the derivative depends on how the scan is made,
            # the scan could be descending or ascending,changing the sign of the derivative
            if (abs(np.min(derivative)) > abs(np.max(derivative))): derivative *= -1.0

            normalization = np.max(scan) / np.max(derivative)
            profile       = derivative * normalization

            profile[np.where(profile < 0.0)]     = 0.0
            profile[np.where(np.isnan(profile))] = 0.0

            return profile

        if direction == Directions.HORIZONTAL:
            data = self.__scan(self.__pvs.motor_h, self.__pvs.motor_h_moving, parameters)
            beam_data["coordinate_h"] = data[:, 0]
            beam_data["profile_h"]    = get_profile(data[:, 0], data[:, 1])
        elif direction == Directions.VERTICAL:
            data = self.__scan(self.__pvs.motor_v, self.__pvs.motor_v_moving, parameters)
            beam_data["coordinate_v"] = data[:, 0]
            beam_data["profile_v"]    = get_profile(data[:, 0], data[:, 1])
        elif direction == Directions.BOTH:
            self.__move_motor(self.__pvs.motor_v, self.__pvs.motor_v_moving, parameters[1].shift_position)
            data_h = self.__scan(self.__pvs.motor_h, self.__pvs.motor_h_moving, parameters[0])

            self.__move_motor(self.__pvs.motor_h, self.__pvs.motor_h_moving, parameters[0].shift_position)
            data_v = self.__scan(self.__pvs.motor_v, self.__pvs.motor_v_moving, parameters[1])

            beam_data["coordinate_h"] = data_h[:, 0]
            beam_data["scan_h"]       = data_h[:, 1]
            beam_data["profile_h"]    = get_profile(data_h[:, 0], data_h[:, 1])
            beam_data["coordinate_v"] = data_v[:, 0]
            beam_data["scan_v"]       = data_v[:, 1]
            beam_data["profile_v"]    = get_profile(data_v[:, 0], data_v[:, 1])

        return Beam(beam_data=beam_data)

    def __scan(self, motor, motor_moving, scan_parameters : ScanParameters):
        positions = scan_parameters.coordinates

        data       = np.zeros((scan_parameters.steps, 2), float)
        data[:, 0] = positions

        print(f"set acquire time to {scan_parameters.acquire_time}")
        self.__pvs.acquire_time.put(scan_parameters.acquire_time)

        for i in range(scan_parameters.steps):
            print(f"motor {motor.pvname}: {positions[i]}" )
            self.__move_motor(motor, motor_moving, positions[i])
            print("start counting:")
            self.__pvs.acquire.put("Count")
            time.sleep(ACQUIRE_WAIT_TIME)
            while self.__pvs.acquire.get() != 0: time.sleep(0.1)
            data[i, 1] = self.__pvs.counts.get()
            print(f"collected {data[i, 1]} counts")
        # put the motor on the peak!
        if scan_parameters.set_motor_on_peak:
            self.__move_motor(motor, motor_moving, data[np.argmax(data[:, 1]), 0])

        return data

    def __move_motor(self, motor, motor_moving, position):
        motor.put(position)

        moving = 0
        while (moving != 1):
            time.sleep(MOTOR_WAIT_TIME)
            moving = motor_moving.get()

    def get_beam_properties(self, beam : Beam, **kwargs) -> BeamProperties:
        beam_data : dict = beam.data

        beam_properties = BeamProperties()

        integral_intensity_h = 0
        peak_intensity_h     = 0
        integral_intensity_v = 0
        peak_intensity_v     = 0

        if "coordinate_h" in beam_data:
            centroid_h            = get_average(beam_data["profile_h"], beam_data["coordinate_h"])
            peak_distance_h       = get_peak_location(beam_data["profile_h"], beam_data["coordinate_h"])
            fwhm_h, _, _          = get_fwhm(beam_data["profile_h"], beam_data["coordinate_h"])
            sigma_h               = get_sigma(beam_data["profile_h"], beam_data["coordinate_h"])
            peak_intensity_h      = np.max(beam_data["profile_h"])
            integral_intensity_h  = np.sum(beam_data["profile_h"])

            beam_properties.set_parameter(DirectBeamImageProperties.CENTROID_H, centroid_h)
            beam_properties.set_parameter(DirectBeamImageProperties.PEAK_LOCATION_H, peak_distance_h)
            beam_properties.set_parameter(DirectBeamImageProperties.FWHM_H, fwhm_h)
            beam_properties.set_parameter(DirectBeamImageProperties.SIGMA_H, sigma_h)
            beam_properties.set_parameter("coordinate_h", beam_data["coordinate_h"])
            beam_properties.set_parameter(self.get_beam_histogram_name() + "_h", beam_data["profile_h"])

        if "coordinate_v" in beam_data:
            centroid_v            = get_average(beam_data["profile_v"], beam_data["coordinate_v"])
            peak_distance_v       = get_peak_location(beam_data["profile_v"], beam_data["coordinate_v"])
            fwhm_v, _, _          = get_fwhm(beam_data["profile_v"], beam_data["coordinate_v"])
            sigma_v               = get_sigma(beam_data["profile_v"], beam_data["coordinate_v"])
            peak_intensity_v      = np.max(beam_data["profile_v"])
            integral_intensity_v  = np.sum(beam_data["profile_v"])

            beam_properties.set_parameter(DirectBeamImageProperties.CENTROID_V, centroid_v)
            beam_properties.set_parameter(DirectBeamImageProperties.PEAK_LOCATION_V, peak_distance_v)
            beam_properties.set_parameter(DirectBeamImageProperties.FWHM_V, fwhm_v)
            beam_properties.set_parameter(DirectBeamImageProperties.SIGMA_V, sigma_v)
            beam_properties.set_parameter("coordinate_v", beam_data["coordinate_v"])
            beam_properties.set_parameter(self.get_beam_histogram_name() + "_v", beam_data["profile_v"])

        peak_intensity     = max(peak_intensity_h, peak_intensity_v)
        integral_intensity = max(integral_intensity_h, integral_intensity_v)

        beam_properties.set_parameter(DirectBeamImageProperties.PEAK_INTENSITY, peak_intensity)
        beam_properties.set_parameter(DirectBeamImageProperties.INTEGRAL_INTENSITY, integral_intensity)

        beam_properties.set_parameter("is_empty_beam", integral_intensity <= self._get_input_parameters().get_parameter("empty_beam_threshold", 0.0))

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

            text = (rf"{'fwhm(H)':<6}  = {beam_properties.get_parameter(labels[0]) : 3.1f} $\mu$m" + "\n" +
                    rf"{'fwhm(V)':<6}  = {beam_properties.get_parameter(labels[1]) : 3.1f} $\mu$m" + "\n" +
                    rf"{'sigma(H)':<6} = {beam_properties.get_parameter(labels[2]) : 3.1f} $\mu$m" + "\n" +
                    rf"{'sigma(V)':<6} = {beam_properties.get_parameter(labels[3]) : 3.1f} $\mu$m" + "\n" +
                    rf"{'peak(H)':<6}  = {beam_properties.get_parameter(labels[4]) : 3.1f} $\mu$m" + "\n" +
                    rf"{'peak(V)':<6}  = {beam_properties.get_parameter(labels[5]) : 3.1f} $\mu$m" + "\n" +
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

