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
import random

try:    import bluesky.plan_stubs as bps
except: print("Bluesky not installed")

import asyncio
import numpy as np
import abc

from aps.beamline_driver.motion_management.facade import Movement, MotorsInfo, Units, MethodCallingType
from aps.beamline_driver.motion_management.abstract_motion_manager import AbstractMotionManager, Keys

try:
    from shadow4.beamline.s4_beamline_element_movements import S4BeamlineElementMovements
    from shadow4.beamline.s4_beamline_element import S4BeamlineElement
except: print("Shadow4 not installed")

class S4MotionManager(AbstractMotionManager):
    class MotorFunction:
        PITCH  = 0
        ROLL   = 1
        YAW    = 2
        NORMAL = 3
        TANGENTIAL = 4
        SAGITTAL = 5
        BENDER = 6

    class BenderPosition:
        UPSTREAM   = 0
        DOWNSTREAM = 1

    def __init__(self,
                 motors_info: MotorsInfo=None,
                 json_file=None):
        if motors_info is None and json_file is None: motors_info = self.get_default_motors_info()

        super(S4MotionManager, self).__init__(motors_info=motors_info,
                                              json_file=json_file,
                                              method_calling_type=MethodCallingType.STANDARD,
                                              platform=Keys.Platforms.DigitalTwin)

        self._movements_registry = {oe_key : {"N" : [0.0, 0.0], "T" : [0.0, 0.0]} for oe_key in self._get_oe_keys()}

    def set_method_calling_type(self, value):
        super(S4MotionManager, self).set_method_calling_type(value)

        if self.method_calling_type() == MethodCallingType.GENERATOR:
            setattr(self, "_move_motor",         self.__move_motor_generator)
            setattr(self, "_get_motor_position", self.__get_motor_position_generator)
        else:
            setattr(self, "_move_motor",         self.__move_motor)
            setattr(self, "_get_motor_position", self.__get_motor_position)

    @abc.abstractmethod
    def get_default_motors_info(self) -> MotorsInfo: raise NotImplementedError
    @abc.abstractmethod
    def _get_motor_function(self, motor_id) -> int: raise NotImplementedError
    @abc.abstractmethod
    def _get_s4_beamline_element(self, motor_id) -> S4BeamlineElement: raise NotImplementedError
    @abc.abstractmethod
    def _get_bender_position(self, motor_id) -> int: raise NotImplementedError
    @abc.abstractmethod
    def _get_oe_keys(self) -> list: raise NotImplementedError
    @abc.abstractmethod
    def _get_oe_key(self, motor_id) -> str: raise NotImplementedError

    def _move_motor_common(self, motor_id : str, position: float, movement : Movement = Movement.ABSOLUTE, units : Units = None):
        if not movement==Movement.ABSOLUTE: raise ValueError("this motion manager does not supports relative movements")
        if units is not None and units != self.get_motors_info().get_motor_info(motor_id).units:
            raise ValueError("this motion manager does not supports units, it will use default ones")

        motor_info         = self.get_motors_info().get_motor_info(motor_id)
        motor_function     = self._get_motor_function(motor_id)
        s4_optical_element = self._get_s4_beamline_element(motor_id)

        repeatibility      = motor_info.repeatability
        coordinates        = s4_optical_element.get_coordinates()
        movements          = s4_optical_element.get_movements()
        movements_registry = self._movements_registry[self._get_oe_key(motor_id)]
        
        if repeatibility > 0.0: position += random.uniform(-repeatibility, repeatibility)

        if motor_function == S4MotionManager.MotorFunction.PITCH:
            self._set_motor_pitch(pitch=position, coordinates=coordinates, movements=movements, motor_info=motor_info)
        elif motor_function == S4MotionManager.MotorFunction.ROLL:
            self._set_motor_roll(roll=position, movements=movements, motor_info=motor_info)
        elif motor_function == S4MotionManager.MotorFunction.YAW:
            self._set_motor_yaw(yaw=position, movements=movements, motor_info=motor_info)
        elif motor_function == S4MotionManager.MotorFunction.NORMAL:
            self._set_motor_normal(translation=position, coordinates=coordinates, movements=movements, motor_info=motor_info, movements_registry=movements_registry)
        elif motor_function == S4MotionManager.MotorFunction.TANGENTIAL:
            self._set_motor_tangential(translation=position, coordinates=coordinates, movements=movements, motor_info=motor_info, movements_registry=movements_registry)
        elif motor_function == S4MotionManager.MotorFunction.SAGITTAL:
            self._set_motor_sagittal(translation=position, coordinates=coordinates, movements=movements, motor_info=motor_info)
        elif motor_function == S4MotionManager.MotorFunction.BENDER:
            bender_movement = s4_optical_element.get_optical_element().bender_movement
            bender_position = self._get_bender_position(motor_id)

            position_upstream   = position if bender_position == S4MotionManager.BenderPosition.UPSTREAM else None
            position_downstream = position if bender_position == S4MotionManager.BenderPosition.DOWNSTREAM else None

            self._set_motor_bender(bender=s4_optical_element,
                                   position_upstream=position_upstream,
                                   position_downstream=position_downstream,
                                   bender_movement=bender_movement,
                                   motor_info=motor_info)

    def _get_motor_position_common(self, motor_id : str, units : Units = None) -> float:
        if units is not None and units != self.get_motors_info().get_motor_info(motor_id).units:
            raise ValueError("this motion manager does not supports units, it will use default ones")

        motor_info         = self.get_motors_info().get_motor_info(motor_id)
        motor_function     = self._get_motor_function(motor_id)
        s4_optical_element = self._get_s4_beamline_element(motor_id)

        coordinates        = s4_optical_element.get_coordinates()
        movements          = s4_optical_element.get_movements()
        movements_registry = movements_registry = self._movements_registry[self._get_oe_key(motor_id)]

        if motor_function == S4MotionManager.MotorFunction.PITCH:
            position = motor_info.apply_resolution(self._get_motor_pitch(coordinates, movements, motor_info))
        elif motor_function == S4MotionManager.MotorFunction.ROLL:
            position = motor_info.apply_resolution(self._get_motor_roll(movements, motor_info))
        elif motor_function == S4MotionManager.MotorFunction.YAW:
            position = motor_info.apply_resolution(self._get_motor_yaw(movements, motor_info))
        elif motor_function == S4MotionManager.MotorFunction.NORMAL:
            position = motor_info.apply_resolution(self._get_motor_normal(coordinates, movements, motor_info, movements_registry))
        elif motor_function == S4MotionManager.MotorFunction.TANGENTIAL:
            position = motor_info.apply_resolution(self._get_motor_tangential(coordinates, movements, motor_info, movements_registry))
        elif motor_function == S4MotionManager.MotorFunction.SAGITTAL:
            position = motor_info.apply_resolution(self._get_motor_sagittal(movements, motor_info))
        elif motor_function == S4MotionManager.MotorFunction.BENDER:
            bender_movement = s4_optical_element.get_optical_element().bender_movement
            bender_position = self._get_bender_position(motor_id)

            if   bender_position == S4MotionManager.BenderPosition.UPSTREAM:   position = motor_info.apply_resolution(bender_movement.position_upstream)
            elif bender_position == S4MotionManager.BenderPosition.DOWNSTREAM: position = motor_info.apply_resolution(bender_movement.position_downstream)
        else:
            raise ValueError("Motor Function not recognized")

        return position

    def __move_motor_generator(self, motor_id : str, position: float, movement : Movement = Movement.ABSOLUTE, units : Units = None):
        self._move_motor_common(motor_id, position, movement, units)
        yield from bps.null() # this call to make this method a bluesky plan

    async def __move_motor_coroutine(self, motor_id : str, position: float, movement : Movement = Movement.ABSOLUTE, units : Units = None):
        self._move_motor_common(motor_id, position, movement, units)
        await asyncio.sleep(0.001)

    def __move_motor(self, motor_id : str, position: float, movement : Movement = Movement.ABSOLUTE, units : Units = None):
        self._move_motor_common(motor_id, position, movement, units)

    def __get_motor_position_generator(self, motor_id : str, units : Units = None) -> float:
        yield from bps.null()
        return self._get_motor_position_common(motor_id, units)

    async def __get_motor_position_coroutine(self, motor_id : str, units : Units = None) -> float:
        await asyncio.sleep(0.001)
        return self._get_motor_position_common(motor_id, units)

    def __get_motor_position(self, motor_id : str, units : Units = None) -> float:
        return self._get_motor_position_common(motor_id, units)

    def _set_motor_bender(self, bender, position_upstream, position_downstream, bender_movement, motor_info):
        if not position_upstream is None:   bender_movement.position_upstream   = motor_info.apply_resolution(position_upstream)
        if not position_downstream is None: bender_movement.position_downstream = motor_info.apply_resolution(position_downstream)

        bender.get_optical_element().move_bender(bender_movement)

    def _set_motor_pitch(self, pitch, coordinates, movements, motor_info):
        movements.rotation_x = self.__to_s4_angle(pitch, motor_info) -  (0.5*np.pi - coordinates.angle_radial())

    def _set_motor_roll(self, roll, movements, motor_info):
        movements.rotation_y = self.__to_s4_angle(roll, motor_info)

    def _set_motor_yaw(self, yaw, movements, motor_info):
        movements.rotation_z = self.__to_s4_angle(yaw, motor_info)

    def _set_motor_normal(self, translation, coordinates, movements, motor_info, movements_registry):
        s4_pitch = self._get_s4_motor_pitch(coordinates, movements) # rad from normal

        z_n = self.__to_s4_length(translation, motor_info) / np.cos(s4_pitch)
        y_n = z_n * np.tan(s4_pitch)

        movements_registry["N"][0] = y_n
        movements_registry["N"][1] = z_n

        movements.offset_y = movements_registry["N"][0] + movements_registry["T"][0]
        movements.offset_z = movements_registry["N"][1] + movements_registry["T"][1]

    def _set_motor_tangential(self, translation, coordinates, movements, motor_info, movements_registry):
        s4_pitch = self._get_s4_motor_pitch(coordinates, movements)

        y_t = self.__to_s4_length(translation, motor_info) / np.cos(s4_pitch)
        z_t = -y_t * np.tan(s4_pitch)

        movements_registry["T"][0] = y_t
        movements_registry["T"][1] = z_t

        movements.offset_y = movements_registry["N"][0] + movements_registry["T"][0]
        movements.offset_z = movements_registry["N"][1] + movements_registry["T"][1]

    def _set_motor_sagittal(self, translation, movements, motor_info):
        movements.offset_x = self.__to_s4_length(translation, motor_info)

    def _get_motor_pitch(self, coordinates, movements, motor_info):
        return self.__from_s4_angle(self._get_s4_motor_pitch(coordinates, movements), motor_info)

    def _get_motor_roll(self, movements, motor_info):
        return self.__from_s4_angle(self._get_s4_motor_roll(movements), motor_info)

    def _get_motor_yaw(self, movements, motor_info):
        return self.__from_s4_angle(self._get_s4_motor_yaw(movements), motor_info)

    def _get_motor_normal(self, coordinates, movements, motor_info, movements_registry):
        return self.__from_s4_length(self._get_s4_motor_normal(coordinates, movements, movements_registry), motor_info)

    def _get_motor_tangential(self, coordinates, movements, motor_info, movements_registry):
        return self.__from_s4_length(self._get_s4_motor_tangential(coordinates, movements, movements_registry), motor_info)

    def _get_motor_sagittal(self, movements, motor_info):
        return self.__from_s4_length(self._get_s4_motor_sagittal(movements), motor_info)

    def _get_s4_motor_pitch(self, coordinates, movements):
        return 0.5*np.pi - coordinates.angle_radial() + movements.get_rotations()[0]

    def _get_s4_motor_roll(self,  movements):
        return movements.get_rotations()[1]

    def _get_s4_motor_yaw(self, movements):
        return movements.get_rotations()[2]

    def _get_s4_motor_normal(self, coordinates, movements, movements_registry):
        s4_pitch = self._get_s4_motor_pitch(coordinates, movements)
        offsets  = movements_registry["N"]

        return offsets[0] * np.sin(s4_pitch) + offsets[1] * np.cos(s4_pitch)

    def _get_s4_motor_tangential(self, coordinates, movements, movements_registry):
        s4_pitch = self._get_s4_motor_pitch(coordinates, movements)
        offsets  = movements_registry["T"]

        return offsets[0] * np.cos(s4_pitch) + offsets[1] * np.sin(s4_pitch)

    def _get_s4_motor_sagittal(self, movements):
        return movements.get_offsets()[0]

    def __to_s4_angle(self, angle, motor_info): # user units to rad
        shift_from_ideal = motor_info.shift_from_ideal

        if   motor_info.units == Units.RADIANS:      return motor_info.apply_resolution(angle - shift_from_ideal)
        elif motor_info.units == Units.MILLIRADIANS: return 1e-3*motor_info.apply_resolution(angle - shift_from_ideal)
        elif motor_info.units == Units.DEGREES:      return np.radians(motor_info.apply_resolution(angle - shift_from_ideal))
        else: raise ValueError("Wrong units on motor " + str(motor_info.legacy_ids))

    def __from_s4_angle(self, s4_angle, motor_info): # rad to user units
        shift_from_ideal = motor_info.shift_from_ideal

        if   motor_info.units == Units.RADIANS:      return s4_angle + shift_from_ideal
        elif motor_info.units == Units.MILLIRADIANS: return 1e3*s4_angle + shift_from_ideal
        elif motor_info.units == Units.DEGREES:      return np.degrees(s4_angle) + shift_from_ideal
        else: raise ValueError("Wrong units on motor " + str(motor_info.legacy_ids))

    def __to_s4_length(self, length, motor_info): # user units to m
        shift_from_ideal = motor_info.shift_from_ideal

        if   motor_info.units == Units.METERS:       return motor_info.apply_resolution(length - shift_from_ideal)
        elif motor_info.units == Units.MILLIMETERS:  return 1e-3*motor_info.apply_resolution(length - shift_from_ideal)
        elif motor_info.units == Units.MICRON:       return 1e-6*motor_info.apply_resolution(length - shift_from_ideal)
        else: raise ValueError("Wrong units on motor " + str(motor_info.legacy_ids))

    def __from_s4_length(self, s4_length, motor_info): # m to user units
        shift_from_ideal = motor_info.shift_from_ideal

        if   motor_info.units == Units.METERS:      return s4_length  + shift_from_ideal
        elif motor_info.units == Units.MILLIMETERS: return 1e3*s4_length  + shift_from_ideal
        elif motor_info.units == Units.MICRON:      return 1e6*s4_length  + shift_from_ideal
        else: raise ValueError("Wrong units on motor " + str(motor_info.legacy_ids))
