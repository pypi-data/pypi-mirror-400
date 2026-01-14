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

import numpy as np
from aps.beamline_driver.beam_management.facade import BeamProperties, Beam, MethodCallingType
from aps.beamline_driver.beam_management.abstract_beam_manager import WavefrontAnalysisBeamManager

class SRWBeamManager(WavefrontAnalysisBeamManager):
    def __init__(self, method_calling_type=MethodCallingType.STANDARD, **kwargs):
        super(SRWBeamManager, self).__init__(method_calling_type=method_calling_type, **kwargs)

        self._to_micron = kwargs.get("to_micron", True)
        self._xrange    = kwargs.get("xrange", None)
        self._yrange    = kwargs.get("yrange", None)
        if not self._xrange is None: self._xrange = (np.array(self._xrange) * (1e-6 if self._to_micron else 1.0)).tolist()
        if not self._yrange is None: self._yrange = (np.array(self._yrange) * (1e-6 if self._to_micron else 1.0)).tolist()

    def _get_wavefront_histogram(self, beam : Beam, **kwargs) -> BeamProperties:
        srw_wavefront = beam.data

        intensity_histogram = self._get_wavefront_intensity(srw_wavefront, self._xrange, self._yrange, self._to_micron)

        # ------------------------------------------------------
        # FOR FUTURE APPLICATIONS
        #
        # e, h, v, p = self.output_wavefront.get_phase()
        # ticket_p              = self._get_ticket_2D(h, v, p[int(e.size / 2)])
        # ticket_p['histogram'] = unwrap(ticket_p['histogram'])
        # ------------------------------------------------------

        phase_histogram = BeamProperties(phase_avg_radius_h=srw_wavefront.Rx, phase_avg_radius_v=srw_wavefront.Ry)

        return intensity_histogram, phase_histogram

    @classmethod
    def _get_wavefront_intensity(cls, srw_wavefront, xrange, yrange, to_micron):
        e, h, v, i = srw_wavefront.get_intensity(multi_electron=False) # Single Electron -> provides the wavefront

        ticket_i = cls._get_ticket_2D(h, v, i[int(e.size / 2)])

        coordinate_h = ticket_i['bin_h']
        coordinate_v = ticket_i['bin_v']

        if not xrange is None: range_x = np.where(np.logical_and(coordinate_h >= xrange[0], coordinate_h <= xrange[1]))
        else:                  range_x = np.where(np.logical_and(coordinate_h >= np.min(coordinate_h), coordinate_h <= np.max(coordinate_h)))
        if not yrange is None: range_y = np.where(np.logical_and(coordinate_v >= yrange[0], coordinate_v <= yrange[1]))
        else:                  range_y = np.where(np.logical_and(coordinate_v >= np.min(coordinate_v), coordinate_v <= np.max(coordinate_v)))

        coordinate_h = ticket_i['bin_h'][range_x] * (1e6 if to_micron else 1.0)
        coordinate_v = ticket_i['bin_v'][range_y] * (1e6 if to_micron else 1.0)

        nbins_h = len(coordinate_h)
        nbins_v = len(coordinate_v)

        histogram = np.zeros((nbins_h, nbins_v))
        for row, i in zip(ticket_i['histogram'][range_x], range(nbins_h)): histogram[i, :] = row[range_y]

        histogram_h = np.sum(histogram, axis=1)
        histogram_v = np.sum(histogram, axis=0)

        return BeamProperties(histogram=histogram,
                              coordinate_h=coordinate_h,
                              coordinate_v=coordinate_v,
                              histogram_h=histogram_h,
                              histogram_v=histogram_v)

    @classmethod
    def _get_ticket_2D(cls, x_array, y_array, z_array):
        ticket = {'error':0}
        ticket['nbins_h'] = len(x_array)
        ticket['nbins_v'] = len(y_array)

        xrange = [x_array.min(), x_array.max() ]
        yrange = [y_array.min(), y_array.max() ]

        hh = z_array
        hh_h = hh.sum(axis=1)
        hh_v = hh.sum(axis=0)
        xx = x_array
        yy = y_array

        ticket['xrange'] = xrange
        ticket['yrange'] = yrange
        ticket['bin_h'] = xx
        ticket['bin_v'] = yy
        ticket['histogram'] = hh
        ticket['histogram_h'] = hh_h
        ticket['histogram_v'] = hh_v

        return ticket
