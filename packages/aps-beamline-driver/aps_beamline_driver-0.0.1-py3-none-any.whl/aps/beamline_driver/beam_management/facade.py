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
from typing import Type
import pickle

from aps.common.data_structures import DictionaryWrapper
from aps.beamline_driver.facade import MethodCallingType

class Beam(object):
    def __init__(self, beam_data : object):
        self.__beam_data = beam_data

    @property
    def data(self): return self.__beam_data

    def serialize(self) -> str: return pickle.dumps(self).hex()
    @classmethod
    def deserialize(cls, hex_string: str): return pickle.loads(bytes.fromhex(hex_string))

class BeamProperties(DictionaryWrapper):
    def __init__(self, **kwargs):
        super(BeamProperties, self).__init__(**kwargs)

class IBeamManager():
    @abc.abstractmethod
    def method_calling_type(self) -> MethodCallingType: raise NotImplementedError
    @abc.abstractmethod
    def set_method_calling_type(self, value: MethodCallingType): raise NotImplementedError
    @abc.abstractmethod
    def get_beam_manager_id(self): raise NotImplementedError
    @abc.abstractmethod
    def set_initial_flux(self, *args, **kwargs): raise NotImplementedError
    @abc.abstractmethod
    def get_beam(self, *args, **kwargs) -> Beam: raise NotImplementedError
    @abc.abstractmethod
    def get_beam_properties(self, beam : Beam, *args, **kwargs) -> BeamProperties: raise NotImplementedError
    @abc.abstractmethod
    def get_beam_properties_type(self) -> Type: raise NotImplementedError
    @abc.abstractmethod
    def to_json(self, *args, **kwargs): raise NotImplementedError
    @classmethod
    @abc.abstractmethod
    def from_json(cls, file_name, *args, **kwargs): raise NotImplementedError

if __name__=="__main__":
    import numpy
    from shadow4.beam.s4_beam import S4Beam

    coor      = 20 * numpy.ones(100)
    val       = 11.02 * numpy.ones(100)
    beam_data = coor, val

    beam = Beam(beam_data=beam_data)
    print(beam.data)
    hex_s = beam.serialize()
    new_beam = Beam.deserialize(hex_s)
    print(new_beam.__data)

    beam_data = S4Beam(N=1000)
    beam_data.rays[500, 9] = 1

    beam = Beam(beam_data=beam_data)
    print(beam.data.rays[500, 9])
    hex_s = beam.serialize()
    new_beam = Beam.deserialize(hex_s)
    print(new_beam.__data.rays[500, 9])