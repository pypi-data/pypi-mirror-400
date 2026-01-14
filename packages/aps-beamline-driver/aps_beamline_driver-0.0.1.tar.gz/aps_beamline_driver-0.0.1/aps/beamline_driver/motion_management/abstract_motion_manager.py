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
import json
import warnings
import inspect

import numpy
from aps.beamline_driver.common.legacy_keys import Keys
from aps.beamline_driver.facade import MethodCallingType
from aps.beamline_driver.motion_management.facade import IMotionManager, MotorsInfo, Movement, Units, MotorType, MotorInfo

class AbstractMotionManager(IMotionManager):
    def __init__(self, motors_info: MotorsInfo=None, json_file: str=None, method_calling_type: MethodCallingType=MethodCallingType.STANDARD, platform=Keys.Platforms.DigitalTwin):
        if not motors_info is None:
            self.__motors_info = motors_info
        elif not json_file is None:
            self.__motors_info=self._load_motors_info_from_json(json_file)
            print(f"Motion Manager initialized from JSON file {json_file}")
        else:
            raise ValueError("Motion Manager cannot be initialized without motors info")

        self.set_method_calling_type(method_calling_type)
        self.__platform = platform

    def platform(self):
        return self.__platform

    def method_calling_type(self) -> MethodCallingType: return self.__method_calling_type

    def set_method_calling_type(self, value : MethodCallingType):
        self.__method_calling_type = value

        if self.method_calling_type() == MethodCallingType.GENERATOR:
            setattr(self, "_call_get_motor_position",  self.__call_get_motor_position_generator)
            setattr(self, "_call_move_motor",          self.__call_move_motor_generator)

            setattr(self, "move_motor",          self.__move_motor_generator)
            setattr(self, "get_motor_position",  self.__get_motor_position_generator)
            setattr(self, "move_motors",         self.__move_motors_generator)
            setattr(self, "get_motor_positions", self.__get_motor_positions_generator)
        else:

            setattr(self, "_call_get_motor_position",  self.__call_get_motor_position)
            setattr(self, "_call_move_motor",          self.__call_move_motor)

            setattr(self, "move_motor",          self.__move_motor)
            setattr(self, "get_motor_position",  self.__get_motor_position)
            setattr(self, "move_motors",         self.__move_motors)
            setattr(self, "get_motor_positions", self.__get_motor_positions)

    def _get_native_position(self, position: float, units: Units, motor_info: MotorInfo):
        native_position = position

        if not units is None and (units != motor_info.units):
            if motor_info.type == MotorType.TRANSLATIONAL:
                if   units == Units.MICRON      and motor_info.units == Units.MILLIMETERS: native_position = position*1e-3
                elif units == Units.MILLIMETERS and motor_info.units == Units.MICRON:      native_position = position*1e3
            elif motor_info.type == MotorType.ROTATIONAL:
                if units == Units.DEGREES:
                    if motor_info.units   == Units.RADIANS:      native_position = numpy.radians(position)
                    elif motor_info.units == Units.MILLIRADIANS: native_position = numpy.radians(position)*1e3
                elif units.RADIANS:
                    if motor_info.units   == Units.DEGREES:      native_position = numpy.degrees(position)
                    elif motor_info.units == Units.MILLIRADIANS: native_position = position*1e3
                elif units.MILLIRADIANS:
                    if motor_info.units   == Units.RADIANS:      native_position = position*1e-3
                    elif motor_info.units == Units.DEGREES:      native_position = numpy.degrees(position*1e-3)
            else:
                warnings.warn(f"Requested units {units} are different from configured {motor_info.units} and no conversion is possible for this motor type {motor_info.type}")

        return motor_info.apply_resolution(native_position)

    def _check_absolute_position(self, native_position: float, current_position: float, movement : Movement, motor_info: MotorInfo):
        absolute_position = native_position if movement == Movement.ABSOLUTE else native_position + current_position

        boundaries  = motor_info.boundaries_by_key(self.platform())
        if absolute_position < boundaries[0] or absolute_position > boundaries[1]:
            raise ValueError("Requested position (" + str(native_position) + " is outside the boundaries (" + str(boundaries) + ")")

    def _convert_native_position(self, native_position: float, units: Units, motor_info: MotorInfo):
        native_position = motor_info.apply_resolution(native_position)
        position        = native_position

        if not units is None and (units != motor_info.units):
            if motor_info.type == MotorType.TRANSLATIONAL:
                if   units == Units.MICRON      and motor_info.units == Units.MILLIMETERS: position = native_position*1e3
                elif units == Units.MILLIMETERS and motor_info.units == Units.MICRON:      position = native_position*1e-3
            elif motor_info.type == MotorType.ROTATIONAL:
                if units == Units.DEGREES:
                    if motor_info.units   == Units.RADIANS:      position = numpy.degrees(native_position)
                    elif motor_info.units == Units.MILLIRADIANS: position = numpy.degrees(native_position*1e-3)
                elif units.RADIANS:
                    if motor_info.units   == Units.DEGREES:      position = numpy.radians(native_position)
                    elif motor_info.units == Units.MILLIRADIANS: position = native_position*1e-3
                elif units.MILLIRADIANS:
                    if motor_info.units   == Units.RADIANS:      position = native_position*1e3
                    elif motor_info.units == Units.DEGREES:      position = numpy.radians(native_position)*1e3
            else:
                warnings.warn(f"Requested units {units} are different from configured {motor_info.units} and no conversion is possible for this motor type {motor_info.type}")

        return position

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------
    # METHOD TYPE DYNAMIC MANAGEMENT -> PRIVATE METHODS
    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------

    def __call_get_motor_position(self, motor_id: str, units : Units = None, *args, **kwargs):
        return self._get_motor_position(motor_id, units=units, *args, **kwargs)

    def __call_get_motor_position_generator(self, motor_id: str, units : Units = None, *args, **kwargs):
        current_position = yield from self._get_motor_position(motor_id, units=units, *args, **kwargs)
        return current_position

    def __call_move_motor(self, motor_id: str, position: float, movement : Movement, units : Units = None, *args, **kwargs):
        self._move_motor(motor_id, position, movement, units, *args, **kwargs)

    def __call_move_motor_generator(self, motor_id: str, position: float, movement : Movement, units : Units = None, *args, **kwargs):
        yield from self._move_motor(motor_id, position, movement, units, *args, **kwargs)

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------

    def __move_motor(self, motor_id: str, position: float, movement : Movement, units : Units = None, *args, **kwargs):
        motor_info = self.__motors_info.get_motor_info(motor_id)

        current_position = self._call_get_motor_position(motor_id, units=motor_info.units, *args, **kwargs)
        native_position  = self._get_native_position(position, units, motor_info)

        self._check_absolute_position(native_position, current_position, movement, motor_info)

        self._call_move_motor(motor_id, native_position, movement, units=motor_info.units, *args, **kwargs)

    # -----------------------------------------------------------------------

    def __get_motor_position(self, motor_id: str, units : Units = None, *args, **kwargs) -> float:
        motor_info      = self.__motors_info.get_motor_info(motor_id)

        native_position = self._call_get_motor_position(motor_id, units=motor_info.units, *args, **kwargs)

        return self._convert_native_position(native_position, units, motor_info)

    # -----------------------------------------------------------------------

    def __move_motor_generator(self, motor_id: str, position: float, movement : Movement, units : Units = None, *args, **kwargs):
        motor_info = self.__motors_info.get_motor_info(motor_id)

        current_position = yield from self._call_get_motor_position(motor_id, units=motor_info.units, *args, **kwargs)
        native_position  = self._get_native_position(position, units, motor_info)

        self._check_absolute_position(native_position, current_position, movement, motor_info)

        yield from self._call_move_motor(motor_id, native_position, movement, units=motor_info.units, *args, **kwargs)

    # -----------------------------------------------------------------------

    def __get_motor_position_generator(self, motor_id: str, units : Units = None, *args, **kwargs) -> float:
        motor_info      = self.__motors_info.get_motor_info(motor_id)

        native_position = yield from self._call_get_motor_position(motor_id, units=motor_info.units, *args, **kwargs)

        return self._convert_native_position(native_position, units, motor_info)

    # -----------------------------------------------------------------------

    def __move_motors_generator(self, motor_positions : dict, movement : Movement, units: dict=None, *args, **kwargs):
        for motor_id in motor_positions:
            yield from self.move_motor(motor_id, motor_positions[motor_id], movement, units.get(motor_id, None) if units is not None else None, *args, **kwargs)

    # -----------------------------------------------------------------------

    def __get_motor_positions_generator(self, motor_ids : list = None, units: dict=None, *args, **kwargs) -> dict:
        positions = {}
        for motor_id in (self.get_motors_info().get_motor_ids() if motor_ids is None else motor_ids):
            positions[motor_id] = yield from self.get_motor_position(motor_id, units.get(motor_id, None) if units is not None else None, *args, **kwargs)

        return positions

    # -----------------------------------------------------------------------

    def __move_motors(self, motor_positions : dict, movement : Movement, units: dict=None, *args, **kwargs):
        for motor_id in motor_positions: self.move_motor(motor_id, motor_positions[motor_id], movement, units.get(motor_id, None) if units is not None else None, *args, **kwargs)

    # -----------------------------------------------------------------------

    def __get_motor_positions(self, motor_ids : list = None, units: dict=None, *args, **kwargs) -> dict:
        return {motor_id : self.get_motor_position(motor_id, units.get(motor_id, None) if units is not None else None, *args, **kwargs) for motor_id in (self.get_motors_info().get_motor_ids() if motor_ids is None else motor_ids)}

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------

    def get_motors_info(self) -> MotorsInfo: return self.__motors_info

    def to_json(self, file_name, *args, **kwargs):
        with open(file_name, "w") as file: json.dump(self.__motors_info.to_dictionary(), file, indent=4)
        print(f"Motion Manager saved to JSON file {file_name}")

    @classmethod
    def from_json(cls, file_name, *args, **kwargs): return cls(motors_info=cls._load_motors_info_from_json(file_name))

    @staticmethod
    def _load_motors_info_from_json(file_name):
        with open(file_name, "r") as file: return MotorsInfo.from_dictionary(json.load(file))

    # -----------------------------------------------------------------------

    @abc.abstractmethod
    def _move_motor(self, motor_id: str, position: float, movement : Movement, units : Units = None, *args, **kwargs): raise NotImplementedError
    @abc.abstractmethod
    def _get_motor_position(self, motor_id: str, units : Units = None, *args, **kwargs) -> float: raise NotImplementedError
