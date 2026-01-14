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
import traceback

import numpy as np
from ophyd import Component
from ophyd import Device, Kind, Signal
from ophyd_async.core import Device as AsyncDevice
from ophyd.sim import NullStatus

from aps.beamline_driver.beam_management.facade import IBeamManager

class _AbstractDetector(Device):
    def __init__(self,
                 prefix: str = "",
                 name: str = "beam_manager",
                 kind: Kind = Kind.normal,
                 beam_manager: IBeamManager = None,
                 verbose: bool = False):
        super(_AbstractDetector, self).__init__(prefix=prefix, name=name, kind=kind)
        self._beam_manager = beam_manager
        self._verbose      = verbose

    def _set_properties(self, beam_string, beam_properties):
        attributes = {}

        for beam_property in self._beam_manager.get_beam_properties_type().to_list():
            value = beam_properties.get_parameter(beam_property)
            getattr(self, beam_property.replace("-", "_")).put(value)
            attributes[beam_property] = value
        getattr(self, "beam").put(beam_string)
        attributes["beam"] = beam_string

        return attributes

    def _set_error(self, error_message):
        attributes = {}
        for beam_property in self._beam_manager.get_beam_properties_type().to_list():
            getattr(self, beam_property.replace("-", "_")).put(np.NaN)
            attributes[beam_property] = np.NaN

        if self._verbose: print("Error while retrieving beam properties: ", error_message)

        return attributes

    def trigger(self, *args, **kwargs):
        try:
            beam            = self._beam_manager.get_beam()
            beam_properties = self._beam_manager.get_beam_properties(beam)

            if beam_properties.get_parameter("is_empty_beam"): attributes = self._set_error("Beam is Empty")
            else:                                              attributes = self._set_properties(beam_string=beam.serialize(),
                                                                                                 beam_properties=beam_properties)
        except Exception:
            attributes = self._set_error(traceback.format_exc())

        if self._verbose: print("called Beam manager!", attributes)

        super().trigger(*args, **kwargs)

        return NullStatus()


class DirectBeamImageDetector(_AbstractDetector):
    centroid_h         = Component(Signal, kind="normal")
    centroid_v         = Component(Signal, kind="normal")
    peak_distance_h    = Component(Signal, kind="normal")
    peak_distance_v    = Component(Signal, kind="normal")
    fwhm_h             = Component(Signal, kind="normal")
    fwhm_v             = Component(Signal, kind="normal")
    sigma_h            = Component(Signal, kind="normal")
    sigma_v            = Component(Signal, kind="normal")
    peak_intensity     = Component(Signal, kind="normal")
    integral_intensity = Component(Signal, kind="normal")
    beam               = Component(Signal, kind="normal")

    def __init__(self,
                 prefix: str = "",
                 name: str = "beam_manager",
                 kind: Kind = Kind.normal,
                 beam_manager: IBeamManager = None,
                 verbose: bool = False):
        super(DirectBeamImageDetector, self).__init__(prefix=prefix,
                                                      name=name,
                                                      kind=kind,
                                                      beam_manager=beam_manager,
                                                      verbose=verbose)

class WavefrontAnalysisDetector(_AbstractDetector):
    intensity_centroid_h             = Component(Signal, kind="normal")
    intensity_centroid_v             = Component(Signal, kind="normal")
    intensity_peak_distance_h        = Component(Signal, kind="normal")
    intensity_peak_distance_v        = Component(Signal, kind="normal")
    intensity_fwhm_h                 = Component(Signal, kind="normal")
    intensity_fwhm_v                 = Component(Signal, kind="normal")
    intensity_sigma_h                = Component(Signal, kind="normal")
    intensity_sigma_v                = Component(Signal, kind="normal")
    intensity_maximum                = Component(Signal, kind="normal")
    intensity_integral               = Component(Signal, kind="normal")
    phase_average_curvature_radius_h = Component(Signal, kind="normal")
    phase_average_curvature_radius_v = Component(Signal, kind="normal")
    beam                             = Component(Signal, kind="normal")

    def __init__(self,
                 prefix: str = "",
                 name: str = "beam_manager",
                 kind: Kind = Kind.normal,
                 beam_manager: IBeamManager = None,
                 verbose: bool = False):
        super(WavefrontAnalysisDetector, self).__init__(prefix=prefix,
                                                        name=name,
                                                        kind=kind,
                                                        beam_manager=beam_manager,
                                                        verbose=verbose)
