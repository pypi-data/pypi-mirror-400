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
import abc
import inspect
from typing import Type
import numpy as np
import os
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
import cmasher as cmm

from aps.beamline_driver.facade import MethodCallingType
from aps.beamline_driver.beam_management.facade import BeamProperties, Beam, IBeamManager
from aps.common.data_structures import DictionaryWrapper

class AbstractBeamManager(IBeamManager):
    def __init__(self, method_calling_type: MethodCallingType=MethodCallingType.STANDARD, **kwargs):
        self.__input_parameters = DictionaryWrapper(**kwargs)

        self._initial_flux      = None
        self.set_method_calling_type(method_calling_type)

    def method_calling_type(self): return self.__method_calling_type

    def set_method_calling_type(self, value):
        self.__method_calling_type = value

        # DYNAMIC IMPLEMENTATION OF THE INTERFACE FOR BLUESKY/OPHYD
        if self.method_calling_type() == MethodCallingType.STANDARD:
            setattr(self, "_call_set_initial_flux", self.__call_set_initial_flux)
            setattr(self, "_call_get_beam", self.__call_get_beam)

            setattr(self, "set_initial_flux", self.__set_initial_flux)
            setattr(self, "get_beam", self.__get_beam)
        elif self.method_calling_type() == MethodCallingType.GENERATOR:
            setattr(self, "_call_set_initial_flux",  self.__call_set_initial_flux_generator)
            setattr(self, "_call_get_beam",          self.__call_get_beam_generator)

            setattr(self, "set_initial_flux",    self.__set_initial_flux_generator)
            setattr(self, "get_beam",            self.__get_beam_generator)

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------
    # METHOD TYPE DYNAMIC MANAGEMENT -> PRIVATE METHODS
    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------

    def __call_set_initial_flux(self, *args, **kwargs):
        self._set_initial_flux(*args, **kwargs)

    def __call_set_initial_flux_generator(self, *args, **kwargs):
        yield from self._set_initial_flux(*args, **kwargs)

    def __call_get_beam(self, *args, **kwargs):
        return self._get_beam(*args, **kwargs)

    def __call_get_beam_generator(self, *args, **kwargs):
        beam = yield from self._get_beam(*args, **kwargs)
        return beam

    def __set_initial_flux(self, *args, **kwargs):
        self._call_set_initial_flux(*args, **kwargs)

    def __set_initial_flux_generator(self, *args, **kwargs):
        yield from self._call_set_initial_flux(*args, **kwargs)

    def __get_beam(self, *args, **kwargs):
        return self._call_get_beam(*args, **kwargs)

    def __get_beam_generator(self, *args, **kwargs):
        beam = yield from self._call_get_beam(*args, **kwargs)
        return beam

    @abc.abstractmethod
    def _set_initial_flux(self, *args, **kwargs): raise NotImplementedError

    @abc.abstractmethod
    def _get_beam(self, *args, **kwargs) -> Beam: raise NotImplementedError

    def get_beam_manager_id(self): return self.__input_parameters.get_parameter("beam_manager_id", None)

    def _get_input_parameters(self) -> DictionaryWrapper: return self.__input_parameters

    def _plot_beam(self, beam_properties, **kwargs):
        if kwargs.get("save_image", False) or kwargs.get("show_beam", False):
            beam_histogram = beam_properties.get_parameter(self.get_beam_histogram_name())

            if not kwargs.get("flip", False):
                hh = beam_histogram.get_parameter("coordinate_h")
                vv = beam_histogram.get_parameter("coordinate_v")
                data_2D = beam_histogram.get_parameter("histogram")
            else:
                hh = beam_histogram.get_parameter("coordinate_v") # Z is horizontal
                vv = beam_histogram.get_parameter("coordinate_h") # X is horizontal
                data_2D = beam_histogram.get_parameter("histogram").T

            xrange = kwargs.get("xrange", None)
            yrange = kwargs.get("yrange", None)

            if xrange is None: xrange = [np.min(hh), np.max(hh)]
            if yrange is None: yrange = [np.min(vv), np.max(vv)]

            # Define a custom formatter function
            def custom_formatter(x, pos): return f'{x:.2f}'

            plt = kwargs.get("plt", None)

            if plt is None: fig = Figure(figsize=[9, 8], constrained_layout=True)
            else:           fig = plt.figure(figsize=[9, 8], constrained_layout=True)
            ax = fig.gca()

            image = fig.gca().pcolormesh(hh, vv, data_2D.T, cmap=cmm.sunburst_r, rasterized=True)
            fig.gca().set_xlim(xrange[0], xrange[1])
            fig.gca().set_ylim(yrange[0], yrange[1])

            # Generate 10 equally spaced ticks within the specified range
            x_ticks = np.linspace(xrange[0], xrange[1], 11)
            y_ticks = np.linspace(yrange[0], yrange[1], 11)

            # Set the ticks on the axes
            fig.gca().set_xticks(x_ticks)
            fig.gca().set_yticks(y_ticks)

            # Apply the custom formatter to the axes
            fig.gca().xaxis.set_major_formatter(FuncFormatter(custom_formatter))
            fig.gca().yaxis.set_major_formatter(FuncFormatter(custom_formatter))

            fig.gca().axhline(0, color="gray", ls="--", linewidth=1, alpha=0.7)
            fig.gca().axvline(0, color="gray", ls="--", linewidth=1, alpha=0.7)
            fig.gca().set_xlabel("Horizontal ($\mu$m)")
            fig.gca().set_ylabel("Vertical ($\mu$m)")

            cbar = fig.colorbar(mappable=image, pad=0.01, aspect=30, shrink=0.6)

            ax.set_aspect("equal")

            labels = self.get_labels()

            text = (rf"{'fwhm(H)':<6}  = {beam_properties.get_parameter(labels[0]) : 3.1f} $\mu$m" + "\n" +
                    rf"{'fwhm(V)':<6}  = {beam_properties.get_parameter(labels[1]) : 3.1f} $\mu$m" + "\n" +
                    rf"{'sigma(H)':<6} = {beam_properties.get_parameter(labels[2]) : 3.1f} $\mu$m" + "\n" +                                                                                                                                                                                                                                                                       
                    rf"{'sigma(V)':<6} = {beam_properties.get_parameter(labels[3]) : 3.1f} $\mu$m" + "\n" +
                    rf"{'peak(H)':<6}  = {beam_properties.get_parameter(labels[4]) : 3.1f} $\mu$m" + "\n" +
                    rf"{'peak(V)':<6}  = {beam_properties.get_parameter(labels[5]) : 3.1f} $\mu$m" + "\n" +
                    rf"{'pI':<10}      = {beam_properties.get_parameter(labels[6]) : 1.3e} ph")
            ax.text(0.75, 0.7, text, color="black", alpha=0.9, fontsize=9, bbox=dict(facecolor="white", edgecolor="gray", alpha=0.7), transform=ax.transAxes)

            trial_num = kwargs.get("trial_num", None)
            if not trial_num is None: fig.gca().text(0.02, 0.95, f"Trial #{trial_num}", fontsize=10, color="blue", transform=ax.transAxes)

            cbar.ax.text(0.5, 1.05, "pI", transform=cbar.ax.transAxes, ha="center", va="bottom", fontsize=10, color="black")

            if kwargs.get("save_image", False):
                file_name = kwargs.get("file_name", None)
                if not file_name is None:
                    fig.savefig(os.path.join(kwargs.get("directory_name", os.path.abspath(os.curdir)), file_name))
                    fig.canvas.draw_idle()

            if kwargs.get("show_beam", False):
                plt = kwargs.get("plt", fig)
                plt.show()

    @classmethod
    @abc.abstractmethod
    def get_beam_histogram_name(cls):  raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def get_labels(cls): raise  NotImplementedError


class DirectBeamImageProperties:
    CENTROID_H         = "centroid-h"
    CENTROID_V         = "centroid-v"
    PEAK_LOCATION_H    = "peak-distance-h"
    PEAK_LOCATION_V    = "peak-distance-v"
    FWHM_H             = "fwhm-h"
    FWHM_V             = "fwhm-v"
    SIGMA_H            = "sigma-h"
    SIGMA_V            = "sigma-v"
    PEAK_INTENSITY     = "peak-intensity"
    INTEGRAL_INTENSITY = "integral-intensity"

    __list = [CENTROID_H, CENTROID_V, PEAK_LOCATION_H, PEAK_LOCATION_V, FWHM_H, FWHM_V, SIGMA_H, SIGMA_V, PEAK_INTENSITY, INTEGRAL_INTENSITY]

    @classmethod
    def to_list(cls): return cls.__list

class WavefrontAnalysisProperties:
    INTENSITY_CENTROID_H             = "intensity-centroid-h"
    INTENSITY_CENTROID_V             = "intensity-centroid-v"
    INTENSITY_FWHM_H                 = "intensity-fwhm-h"
    INTENSITY_FWHM_V                 = "intensity-fwhm-v"
    INTENSITY_SIGMA_H                = "intensity-sigma-h"
    INTENSITY_SIGMA_V                = "intensity-sigma-v"
    INTENSITY_MAXIMUM                = "intensity-max"
    INTENSITY_INTEGRAL               = "intensity-integral"
    FOCUS_Z_POSITION_H               = "focus-z-position-h"
    FOCUS_Z_POSITION_V               = "focus-z-position-v"

    __list = [INTENSITY_CENTROID_H,
              INTENSITY_CENTROID_V,
              INTENSITY_FWHM_H,
              INTENSITY_FWHM_V,
              INTENSITY_SIGMA_H,
              INTENSITY_SIGMA_V,
              INTENSITY_MAXIMUM,
              INTENSITY_INTEGRAL,
              FOCUS_Z_POSITION_H,
              FOCUS_Z_POSITION_V]

    @classmethod
    def to_list(cls): return cls.__list

class SpeckleAnalysisProperties:
    FWHM_H          = "fwhm-h"
    FWHM_V          = "fwhm-v"
    SPECKLE_SIZE_H  = "speckle-size-h"
    SPECKLE_SIZE_V  = "speckle-size-v"

    __list = [FWHM_H, FWHM_V, SPECKLE_SIZE_H, SPECKLE_SIZE_V]

    @classmethod
    def to_list(cls): return cls.__list


class DirectBeamImageBeamManager(AbstractBeamManager):
    def __init__(self, method_calling_type: MethodCallingType=MethodCallingType.STANDARD, **kwargs):
        super(DirectBeamImageBeamManager, self).__init__(method_calling_type=method_calling_type, **kwargs)

    def get_beam_properties_type(self) -> Type: return DirectBeamImageProperties

    def get_beam_properties(self, beam : Beam, **kwargs) -> BeamProperties:
        beam_histogram = self._get_beam_histogram(beam, **kwargs)

        centroid_h, centroid_v                 = _get_centroids(beam_histogram)
        peak_distance_h, peak_distance_v, _, _ = _get_peak_coordinates(beam_histogram)
        fwhm_h, fwhm_v                         = _get_fwhms(beam_histogram)
        sigma_h, sigma_v                       = _get_sigmas(beam_histogram)

        beam_properties = BeamProperties()
        beam_properties.set_parameter(DirectBeamImageProperties.CENTROID_H, centroid_h)
        beam_properties.set_parameter(DirectBeamImageProperties.CENTROID_V, centroid_v)
        beam_properties.set_parameter(DirectBeamImageProperties.PEAK_LOCATION_H, peak_distance_h)
        beam_properties.set_parameter(DirectBeamImageProperties.PEAK_LOCATION_V, peak_distance_v)
        beam_properties.set_parameter(DirectBeamImageProperties.FWHM_H, fwhm_h)
        beam_properties.set_parameter(DirectBeamImageProperties.FWHM_V, fwhm_v)
        beam_properties.set_parameter(DirectBeamImageProperties.SIGMA_H, sigma_h)
        beam_properties.set_parameter(DirectBeamImageProperties.SIGMA_V, sigma_v)
        beam_properties.set_parameter(DirectBeamImageProperties.PEAK_INTENSITY, _get_peak_intensity(beam_histogram))

        integral_instensity = _get_integral_intensity(beam_histogram)

        beam_properties.set_parameter(DirectBeamImageProperties.INTEGRAL_INTENSITY, integral_instensity)
        beam_properties.set_parameter("is_empty_beam", integral_instensity <= self._get_input_parameters().get_parameter("empty_beam_threshold", 0.0))
        beam_properties.set_parameter(self.get_beam_histogram_name(), beam_histogram)

        self._plot_beam(beam_properties, **kwargs)

        return beam_properties

    @abc.abstractmethod
    def _get_beam_histogram(self, beam : Beam, **kwargs) -> BeamProperties: raise NotImplementedError

    @classmethod
    def get_beam_histogram_name(cls): return "beam_histogram"

    @classmethod
    def get_labels(cls): return [DirectBeamImageProperties.FWHM_H,
                                 DirectBeamImageProperties.FWHM_V,
                                 DirectBeamImageProperties.SIGMA_H,
                                 DirectBeamImageProperties.SIGMA_V,
                                 DirectBeamImageProperties.PEAK_LOCATION_H,
                                 DirectBeamImageProperties.PEAK_LOCATION_V,
                                 DirectBeamImageProperties.PEAK_INTENSITY]

class WavefrontAnalysisBeamManager(AbstractBeamManager):
    def __init__(self, method_calling_type: MethodCallingType = MethodCallingType.STANDARD, **kwargs):
        super(WavefrontAnalysisBeamManager, self).__init__(method_calling_type=method_calling_type, **kwargs)

    def get_beam_properties_type(self) -> Type: return WavefrontAnalysisProperties

    def get_beam_properties(self, beam : Beam, **kwargs) -> BeamProperties:
        intensity_histogram, phase_histogram = self._get_wavefront_histogram(beam, **kwargs)

        centroid_h, centroid_v                 = _get_centroids(intensity_histogram)
        peak_distance_h, peak_distance_v, _, _ = _get_peak_coordinates(intensity_histogram)
        fwhm_h, fwhm_v                         = _get_fwhms(intensity_histogram)
        sigma_h, sigma_v                       = _get_sigmas(intensity_histogram)

        beam_properties = BeamProperties()
        beam_properties.set_parameter(WavefrontAnalysisProperties.INTENSITY_CENTROID_H, centroid_h)
        beam_properties.set_parameter(WavefrontAnalysisProperties.INTENSITY_CENTROID_V, centroid_v)
        beam_properties.set_parameter(WavefrontAnalysisProperties.INTENSITY_FWHM_H, fwhm_h)
        beam_properties.set_parameter(WavefrontAnalysisProperties.INTENSITY_FWHM_V, fwhm_v)
        beam_properties.set_parameter(WavefrontAnalysisProperties.INTENSITY_SIGMA_H, sigma_h)
        beam_properties.set_parameter(WavefrontAnalysisProperties.INTENSITY_SIGMA_V, sigma_v)
        beam_properties.set_parameter(WavefrontAnalysisProperties.INTENSITY_MAXIMUM, _get_peak_intensity(intensity_histogram))

        integral_intensity = _get_integral_intensity(intensity_histogram)

        beam_properties.set_parameter(WavefrontAnalysisProperties.INTENSITY_INTEGRAL, integral_intensity)
        beam_properties.set_parameter("is_empty_beam", integral_intensity <= self._get_input_parameters().get_parameter("empty_beam_threshold", 0.0))
        beam_properties.set_parameter(self.get_beam_histogram_name(), intensity_histogram)

        beam_properties.set_parameter(WavefrontAnalysisProperties.FOCUS_Z_POSITION_H, phase_histogram.get_parameter("focus_z_position_h"))
        beam_properties.set_parameter(WavefrontAnalysisProperties.FOCUS_Z_POSITION_V, phase_histogram.get_parameter("focus_z_position_v"))

        self._plot_beam(beam_properties, **kwargs)

        return beam_properties

    @abc.abstractmethod
    def _get_wavefront_histogram(self, beam : Beam, **kwargs) -> BeamProperties: raise NotImplementedError

    @classmethod
    def get_beam_histogram_name(cls): return "intensity_histogram"

    @classmethod
    def get_labels(cls): return [WavefrontAnalysisProperties.INTENSITY_FWHM_H,
                                 WavefrontAnalysisProperties.INTENSITY_FWHM_V,
                                 WavefrontAnalysisProperties.INTENSITY_SIGMA_H,
                                 WavefrontAnalysisProperties.INTENSITY_SIGMA_V,
                                 WavefrontAnalysisProperties.FOCUS_Z_POSITION_H,
                                 WavefrontAnalysisProperties.FOCUS_Z_POSITION_V,
                                 WavefrontAnalysisProperties.INTENSITY_MAXIMUM]


class SpeckleAnalysisBeamManager(AbstractBeamManager):
    def __init__(self, method_calling_type: MethodCallingType=MethodCallingType.STANDARD, **kwargs):
        super(SpeckleAnalysisBeamManager, self).__init__(method_calling_type=method_calling_type, **kwargs)

    def get_beam_properties_type(self) -> Type: return SpeckleAnalysisProperties

    def get_beam_properties(self, beam : Beam, **kwargs) -> BeamProperties:
        speckle_data = self._extract_speckle_data(beam, **kwargs)

        beam_properties = BeamProperties()
        beam_properties.set_parameter("raw_data", speckle_data["raw_data"])
        beam_properties.set_parameter(SpeckleAnalysisProperties.FWHM_H, speckle_data[SpeckleAnalysisProperties.FWHM_H])
        beam_properties.set_parameter(SpeckleAnalysisProperties.FWHM_V, speckle_data[SpeckleAnalysisProperties.FWHM_V])
        beam_properties.set_parameter(SpeckleAnalysisProperties.SPECKLE_SIZE_H, speckle_data[SpeckleAnalysisProperties.SPECKLE_SIZE_H])
        beam_properties.set_parameter(SpeckleAnalysisProperties.SPECKLE_SIZE_V, speckle_data[SpeckleAnalysisProperties.SPECKLE_SIZE_V])
        beam_properties.set_parameter(self.get_beam_histogram_name() + "_h", speckle_data[self.get_beam_histogram_name() + "_h"])
        beam_properties.set_parameter(self.get_beam_histogram_name() + "_v", speckle_data[self.get_beam_histogram_name() + "_v"])

        beam_properties.set_parameter("coordinate_h", speckle_data["coordinate_h"])
        beam_properties.set_parameter("coordinate_v", speckle_data["coordinate_v"])

        self._plot_beam(beam_properties, **kwargs)

        return beam_properties

    @abc.abstractmethod
    def _extract_speckle_data(self, beam : Beam, **kwargs) -> dict: raise NotImplementedError

    @classmethod
    def  get_beam_histogram_name(cls): return "speckle_data"

    @classmethod
    def get_labels(cls): return SpeckleAnalysisProperties.to_list()



from aps.common.plot.image import get_average, get_peak_location_2D, get_fwhm, get_sigma

def _get_centroids(beam_histogram: BeamProperties):
    return get_average(beam_histogram.get_parameter("histogram_h"), beam_histogram.get_parameter("coordinate_h")), \
           get_average(beam_histogram.get_parameter("histogram_v"), beam_histogram.get_parameter("coordinate_v"))

def _get_peak_coordinates(beam_histogram: BeamProperties):
    return get_peak_location_2D(beam_histogram.get_parameter("coordinate_h"),
                                beam_histogram.get_parameter("coordinate_v"),
                                beam_histogram.get_parameter("histogram"))

def _get_fwhms(beam_histogram: BeamProperties):
    fwhm_h, _, _ = get_fwhm(beam_histogram.get_parameter("histogram_h"), beam_histogram.get_parameter("coordinate_h"))
    fwhm_v, _, _ = get_fwhm(beam_histogram.get_parameter("histogram_v"), beam_histogram.get_parameter("coordinate_v"))

    return fwhm_h, fwhm_v

def _get_sigmas(beam_histogram: BeamProperties):
    return get_sigma(beam_histogram.get_parameter("histogram_h"), beam_histogram.get_parameter("coordinate_h")), \
           get_sigma(beam_histogram.get_parameter("histogram_v"), beam_histogram.get_parameter("coordinate_v"))

def _get_peak_intensity(beam_histogram: BeamProperties) -> float:
    _, _, i, j = _get_peak_coordinates(beam_histogram)
    histogram   = beam_histogram.get_parameter("histogram")
    shape       = histogram.shape

    return np.average(histogram[max(0, i-1): min(shape[0], i+1), max(0, j-1) : min(shape[1], j+1)])

def _get_integral_intensity(beam_histogram: BeamProperties) -> float:
    return beam_histogram.get_parameter("histogram").sum()


