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
import numpy as np

from aps.beamline_driver.beam_management.facade import BeamProperties, Beam, MethodCallingType
from aps.beamline_driver.beam_management.abstract_beam_manager import DirectBeamImageBeamManager
from aps.beamline_driver.common.utility import generate_noise, calculate_projections_over_noise
from scipy.ndimage import gaussian_filter, uniform_filter

from hybrid_methods.coherence.hybrid_screen import StdIOHybridListener

try:    import bluesky.plan_stubs as bps
except: print("bluesky not installed")

EXPERIMENTAL_NOISE_TO_SIGNAL_RATIO = (100 / 5e4)
NOISE_DEFAULT_VALUE = 70 * EXPERIMENTAL_NOISE_TO_SIGNAL_RATIO

class NullHybridListener(StdIOHybridListener):
    def status_message(self, message : str): pass
    def set_progress_value(self, percentage : int): pass

class S4BeamManager(DirectBeamImageBeamManager):
    def __init__(self, method_calling_type=MethodCallingType.STANDARD, **kwargs):
        super(S4BeamManager, self).__init__(method_calling_type=method_calling_type, **kwargs)

        self._to_micron              = kwargs.get("to_micron", True)
        self._nbins_h                = kwargs.get("nbins_h", 201)
        self._nbins_v                = kwargs.get("nbins_v", 201)
        self._xrange                 = kwargs.get("xrange", None)
        self._yrange                 = kwargs.get("yrange", None)
        self._add_noise              = kwargs.get("add_noise", False)
        self._noise                  = kwargs.get("noise", NOISE_DEFAULT_VALUE if self._add_noise else None)
        self._percentage_fluctuation = kwargs.get("percentage_fluctuation", 10.0) * 1e-2
        self._calculate_over_noise   = kwargs.get("calculate_over_noise", False)
        self._noise_threshold        = kwargs.get("noise_threshold", 1.5)

        if not self._xrange is None: self._xrange = (np.array(self._xrange) * (1e-6 if self._to_micron else 1.0)).tolist()
        if not self._yrange is None: self._yrange = (np.array(self._yrange) * (1e-6 if self._to_micron else 1.0)).tolist()

    def set_method_calling_type(self, value):
        super(S4BeamManager, self).set_method_calling_type(value)

        if self.method_calling_type() == MethodCallingType.GENERATOR:
            setattr(self, "_set_initial_flux",  self.__set_initial_flux_generator)
            setattr(self, "_get_beam",          self.__get_beam_generator)
        else:
            setattr(self, "_set_initial_flux",  self.__set_initial_flux)
            setattr(self, "_get_beam",          self.__get_beam)

    def __set_initial_flux_generator(self, *args, **kwargs): yield from bps.null()

    def __set_initial_flux(self, *args, **kwargs): pass

    def __get_beam_generator(self, *args, **kwargs) -> Beam:
        yield from bps.null()
        return Beam(self._get_simulated_beam(**kwargs))

    def __get_beam(self, *args, **kwargs) -> Beam:
        return Beam(self._get_simulated_beam(**kwargs))

    @abc.abstractmethod
    def _get_simulated_beam(self) -> Beam: raise NotImplementedError

    def _get_beam_histogram(self, beam : Beam, **kwargs) -> BeamProperties:
        s4_beam = beam.data

        ticket = s4_beam.histo2(col_h=1,
                                col_v=3,
                                nbins_h=self._nbins_h,
                                nbins_v=self._nbins_v,
                                nolost=1,
                                xrange=self._xrange,
                                yrange=self._yrange)

        if not kwargs.get("blur_image", False):  histogram = ticket["histogram"]
        else:
            filter = kwargs.get("filter", "gaussian")
            if   filter == "gaussian": histogram = gaussian_filter(ticket["histogram"], sigma=kwargs.get("sigma", 2))
            elif filter == "uniform":  histogram = uniform_filter(ticket["histogram"],  size=kwargs.get("sigma", 5))

        coordinate_h = ticket['bin_h_center'] * (1e6 if self._to_micron else 1.0)
        coordinate_v = ticket['bin_v_center'] * (1e6 if self._to_micron else 1.0)

        if self._add_noise:
            histogram = generate_noise(histogram, self._noise, self._percentage_fluctuation)

            if self._calculate_over_noise:
                _, histogram_h, histogram_v = calculate_projections_over_noise(histogram, self._noise_threshold)
            else:
                histogram_h = histogram.sum(axis=1)
                histogram_v = histogram.sum(axis=0)
        else:
            histogram_h = ticket['histogram_h']
            histogram_v = ticket['histogram_v']

        return BeamProperties(histogram=histogram,
                              coordinate_h=coordinate_h,
                              coordinate_v=coordinate_v,
                              histogram_h=histogram_h,
                              histogram_v=histogram_v)
