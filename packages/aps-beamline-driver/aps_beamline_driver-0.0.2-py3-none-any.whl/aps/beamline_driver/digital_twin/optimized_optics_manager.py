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

from aps.beamline_driver.motion_management.facade import Movement, MotorsInfo
from aps.beamline_driver.beam_management.facade import Beam

from aps.common.data_structures import DictionaryWrapper

from aps.beamline_driver.beam_management.facade import IBeamManager
from aps.beamline_driver.motion_management.facade import IMotionManager, MethodCallingType

class AbstractOptimizedOpticsManager(IBeamManager, IMotionManager):

    def __init__(self, digital_twin_init_parameters: DictionaryWrapper, method_calling_type=MethodCallingType.STANDARD):
        self._digital_twin_init_parameters = digital_twin_init_parameters
        self._beam_manager: IBeamManager     = None
        self._motion_manager: IMotionManager = None
        self._initialize_digital_twin()

        self.set_method_calling_type(method_calling_type)

    def method_calling_type(self) -> MethodCallingType: return self.__method_calling_type

    def set_method_calling_type(self, value: MethodCallingType):
        self.__method_calling_type = value

        self._motion_manager.set_method_calling_type(self.__method_calling_type)
        self._beam_manager.set_method_calling_type(self.__method_calling_type)

        # DYNAMIC IMPLEMENTATION OF THE INTERFACE FOR BLUESKY/OPHYD
        if self.method_calling_type() == MethodCallingType.GENERATOR:
            # motion manager
            setattr(self, "move_motor",          self.__move_motor_generator)
            setattr(self, "get_motor_position",  self.__get_motor_position_generator)
            setattr(self, "move_motors",         self.__move_motors_generator)
            setattr(self, "get_motor_positions", self.__get_motor_positions_generator)
            # beam manager
            setattr(self, "set_initial_flux",    self.__set_initial_flux_generator)
            setattr(self, "get_beam",            self.__get_beam_generator)
        else:
            # motion manager
            setattr(self, "move_motor",          self.__move_motor)
            setattr(self, "get_motor_position",  self.__get_motor_position)
            setattr(self, "move_motors",         self.__move_motors)
            setattr(self, "get_motor_positions", self.__get_motor_positions)
            # beam manager
            setattr(self, "set_initial_flux",    self.__set_initial_flux)
            setattr(self, "get_beam",            self.__get_beam)

    @abc.abstractmethod
    def _initialize_digital_twin(self): raise NotImplementedError("here initialize self._beam_manager and self._motion_manager")

    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------
    # MOTION MANAGER
    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------

    def __move_motor_generator(self, motor_id: str, position: float, movement=Movement.ABSOLUTE):
        yield from self._motion_manager.move_motor(motor_id, position, movement=movement)

    def __get_motor_position_generator(self, motor_id: str) -> float:
        position = yield from self._motion_manager.get_motor_position(motor_id)
        return position

    def __move_motors_generator(self, motor_positions: dict, movement=Movement.ABSOLUTE):
        yield from self._motion_manager.move_motors(motor_positions, movement=movement)

    def __get_motor_positions_generator(self, motor_ids: list = None) -> dict:
        position = yield from self._motion_manager.get_motor_positions(motor_ids)
        return position

    def __move_motor(self, motor_id: str, position: float, movement=Movement.ABSOLUTE):
        self._motion_manager.move_motor(motor_id, position, movement=movement)

    def __get_motor_position(self, motor_id: str) -> float:
        return self._motion_manager.get_motor_position(motor_id)

    def __move_motors(self, motor_positions: dict, movement=Movement.ABSOLUTE):
        self._motion_manager.move_motors(motor_positions, movement=movement)

    def __get_motor_positions(self, motor_ids: list = None) -> dict:
        return self._motion_manager.get_motor_positions(motor_ids)

    def get_motors_info(self) -> MotorsInfo:
        return self._motion_manager.get_motors_info()

    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------
    # BEAM MANAGER
    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------

    def __set_initial_flux_generator(self, *args, **kwargs):
        yield from self._beam_manager.set_initial_flux(*args, **kwargs)

    def __set_initial_flux(self, *args, **kwargs):
        self._beam_manager.set_initial_flux(*args, **kwargs)

    def __get_beam_generator(self, *args, **kwargs) -> Beam:
        beam = yield from self._beam_manager.get_beam(*args, **kwargs)
        return beam

    def __get_beam(self, *args, **kwargs) -> Beam:
        return self._beam_manager.get_beam(*args, **kwargs)

    def get_beam_manager_id(self): return self._beam_manager.get_beam_manager_id()

    def get_beam_properties_type(self): return self._beam_manager.get_beam_properties_type()

    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------
    # COMMON
    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------

    def to_json(self, *args, **kwargs): self._motion_manager.to_json(*args, **kwargs)
    @classmethod
    def from_json(cls, file_name, *args, **kwargs): raise NotImplementedError("To be implemented")



