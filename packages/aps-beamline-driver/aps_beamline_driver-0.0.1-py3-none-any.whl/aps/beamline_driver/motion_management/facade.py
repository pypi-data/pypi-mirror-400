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
import abc, decimal
from typing import List, Dict, Any
from enum import Enum

import numpy as np

from aps.common.data_structures import DictionaryWrapper
from aps.beamline_driver.facade import MethodCallingType

class Movement(Enum):
    ABSOLUTE = 1
    RELATIVE = 2

class Units(Enum):
    MILLIRADIANS = 1
    DEGREES      = 2
    RADIANS      = 3
    MILLIMETERS  = 4
    MICRON       = 5
    METERS       = 6
    VOLTS        = 7
    MILLIVOLTS   = 8
    OTHER        = 9

    @property
    def label(self):
        if   self.value == 1: return "mrad"
        elif self.value == 2: return "deg"
        elif self.value == 3: return "rad"
        elif self.value == 4: return "mm"
        elif self.value == 5: return "\u03bcm"
        elif self.value == 6: return "m"
        elif self.value == 7: return "V"
        elif self.value == 8: return "mV"
        elif self.value == 9: return "Other"

    @classmethod
    def get_label(cls, value: int):
        if   value == 1: return "mrad"
        elif value == 2: return "deg"
        elif value == 3: return "rad"
        elif value == 4: return "mm"
        elif value == 5: return "\u03bcm"
        elif value == 6: return "m"
        elif value == 7: return "V"
        elif value == 8: return "mV"
        elif value == 9: return "Other"

    @classmethod
    def get_native_value(cls, value: int):
        if   value == 1: return Units.MILLIRADIANS
        elif value == 2: return Units.DEGREES
        elif value == 3: return Units.RADIANS
        elif value == 4: return Units.MILLIMETERS
        elif value == 5: return Units.MICRON
        elif value == 6: return Units.METERS
        elif value == 7: return Units.VOLTS
        elif value == 8: return Units.MILLIVOLTS
        elif value == 9: return Units.OTHER

    @classmethod
    def get_labels_list(cls):
        return ["mrad",
                "deg",
                "rad",
                "mm",
                "\u03bcm",
                "m",
                "V",
                "mV",
                "Other"]

class MotorType(Enum):
    ROTATIONAL    = 1
    TRANSLATIONAL = 2
    OTHER         = 3

    @classmethod
    def get_label(value: int):
        if   value == 1: return "Rotational"
        elif value == 2: return "Transational"
        elif value == 3: return "Other"

    @classmethod
    def get_native_value(cls, value: int):
        if   value == 1: return MotorType.ROTATIONAL
        elif value == 2: return MotorType.TRANSLATIONAL
        elif value == 3: return MotorType.OTHER

    @classmethod
    def get_labels_list(cls):
        return ["Rotational",
                "Transational",
                "Other"]


class MotorInfo(object):
    def __init__(self,
                 type :                 MotorType,
                 units :                Units,
                 resolution :           float,
                 repeatability:         float,
                 search_range:          Dict[str, Dict[str, Dict[str, List[float]]]],
                 search_transfer_range: Dict[str, Dict[str, Dict[str, List[float]]]],
                 boundaries:            Dict[str, List[float]],
                 initial_position:      Dict[str, Dict[str, Dict[str, float]]],
                 shift_from_ideal:      float,
                 legacy_ids :           List[str],
                 optimized:             Dict[str, Dict[str, Dict[str, bool]]]):
        self.__type                  = type
        self.__units                 = units
        self.__resolution            = resolution
        self.__repeatability         = repeatability
        self.__search_range          = search_range
        self.__search_transfer_range = search_transfer_range
        self.__boundaries            = boundaries
        self.__initial_position      = initial_position
        self.__shift_from_ideal      = shift_from_ideal
        self.__legacy_ids            = legacy_ids
        self.__optimized             = optimized

    def __get_value_from_key(self, dictionary, beam_manager_type, platform, beam_manager_id) -> Any:
        try:             return dictionary[beam_manager_type][platform].get(beam_manager_id, None)
        except KeyError: return None

    @property
    def type(self) -> MotorType: return self.__type
    @property
    def units(self) -> Units: return self.__units
    @property
    def resolution(self) -> float: return self.__resolution
    @property
    def repeatability(self) -> float: return self.__repeatability
    @property
    def digits(self) -> int: return abs(decimal.Decimal(str(self.__resolution)).as_tuple().exponent)
    @property
    def search_range(self) -> Dict[str, Dict[str, Dict[str, List[float]]]]: return self.__search_range
    @property
    def search_space(self) -> Dict[str, Dict[str, Dict[str, List[float]]]]:
        search_space = {}
        for beam_manager_type in self.__search_range.keys():
            search_space[beam_manager_type] = {}
            for platform in self.__search_range[beam_manager_type].keys():
                search_space[beam_manager_type][platform] = {}
                for beam_manager_id in self.__search_range[beam_manager_type][platform].keys():
                    search_range = self.__search_range[beam_manager_type][platform][beam_manager_id]
                    search_space[beam_manager_type][platform][beam_manager_id] = [round(item, self.digits) for item in np.arange(start=search_range[0],
                                                                                                                                 stop=search_range[1] + self.__resolution,
                                                                                                                                 step=self.__resolution)]
        return search_space

    def search_range_by_key(self, beam_manager_type, platform, beam_manager_id) -> List[float]:
        return self.__get_value_from_key(self.__search_range, beam_manager_type, platform, beam_manager_id)

    def search_space_by_key(self, beam_manager_type, platform, beam_manager_id) -> List[float]:
        try:
            search_range = self.__get_value_from_key(self.__search_range, beam_manager_type, platform, beam_manager_id)
            if not search_range is None:
                return [round(item, self.digits) for item in np.arange(start=search_range[0],
                                                                       stop=search_range[1] + self.__resolution,
                                                                       step=self.__resolution)]
            else: return None
        except KeyError:
            return None

    @property
    def search_transfer_range(self) -> Dict[str, Dict[str, Dict[str, List[float]]]]: return self.__search_transfer_range
    def search_transfer_range_by_key(self, beam_manager_type, platform, beam_manager_id) -> List[float]:
        return self.__get_value_from_key(self.__search_transfer_range, beam_manager_type, platform, beam_manager_id)

    @property
    def boundaries(self) -> Dict[str, List[float]]: return self.__boundaries
    def boundaries_by_key(self, platform) -> List[float]:
        return self.__boundaries.get(platform, None)

    @property
    def initial_position(self) -> Dict[str, Dict[str, Dict[str, float]]]: return self.__initial_position
    def initial_position_by_key(self, beam_manager_type, platform, beam_manager_id) -> float:
        return self.__get_value_from_key(self.__initial_position, beam_manager_type, platform, beam_manager_id)

    @property
    def shift_from_ideal(self) -> float: return self.__shift_from_ideal

    @property
    def legacy_ids(self) -> List[str]: return self.__legacy_ids
    @property
    def optimized(self) -> Dict[str, Dict[str, Dict[str, bool]]]: return self.__optimized
    def optimized_by_key(self, beam_manager_type, platform, beam_manager_id) -> bool:
        return self.__get_value_from_key(self.__optimized, beam_manager_type, platform, beam_manager_id)

    def apply_resolution(self, position):
        significant_digits = abs(decimal.Decimal(str(self.__resolution)).as_tuple().exponent)
        return round(position, significant_digits)

    def __str__(self):
        return "type: " + str(self.__type.name) + \
            ", units: " + str(self.__units.label) + \
            ", resolution: " + str(self.__resolution) + \
            ", repeatability: " + str(self.__repeatability) + \
            ", search_range: " + str(self.__search_range) + \
            ", search_transfer_range: " + str(self.__search_transfer_range) + \
            ", boundaries: " + str(self.__boundaries) + \
            ", initial_position: " + str(self.__initial_position) + \
            ", shift_from_ideal: " + str(self.__shift_from_ideal) + \
            ", legacy_ids: " + str(self.__legacy_ids)  + \
            ", optimized: " + str(self.__optimized)

    def to_dictionary(self):
        return {"type":         self.__type.value,
                "units":        self.__units.value,
                "resolution":   self.__resolution,
                "repeatability":   self.__repeatability,
                "search_range": self.__search_range,
                "search_transfer_range" : self.__search_transfer_range,
                "boundaries":   self.__boundaries,
                "initial_position":   self.__initial_position,
                "shift_from_ideal": self.__shift_from_ideal,
                "legacy_ids":    self.__legacy_ids,
                "optimized": self.__optimized}

    @classmethod
    def from_dictionary(self, dictionary: dict):
        return MotorInfo(type                  = MotorType(dictionary.get("type", 2)),
                         units                 = Units(dictionary.get("units", 9)),
                         resolution            = dictionary.get("resolution", 0.0),
                         repeatability         = dictionary.get("repeatability", 0.0),
                         search_range          = dictionary.get("search_range", {}),
                         search_transfer_range = dictionary.get("search_transfer_range", {}),
                         boundaries            = dictionary.get("boundaries", {}),
                         initial_position      = dictionary.get("initial_position", {}),
                         shift_from_ideal      = dictionary.get("shift_from_ideal", 0.0),
                         legacy_ids            = dictionary.get("legacy_ids", ["", ""]),
                         optimized             = dictionary.get("optimized", {}))

class MotorsInfo(DictionaryWrapper):
    def __init__(self, **kwargs): super(MotorsInfo, self).__init__(**kwargs)

    def add_motor_info(self, motor_id : str, info : MotorInfo): self.set_parameter(motor_id, info)
    def get_motors_count(self) -> int: return self.get_parameters_number()
    def get_motor_info(self, motor_id : str) -> MotorInfo: return self.get_parameter(motor_id)
    def get_motor_ids(self) -> list: return self.get_parameter_names()
    def get_types(self, motor_ids: list=None) -> dict: return {motor_id: self.get_motor_info(motor_id).type for motor_id in (self.get_motor_ids() if motor_ids is None else motor_ids)}
    def get_units(self, motor_ids: list=None) -> dict: return {motor_id: self.get_motor_info(motor_id).units for motor_id in (self.get_motor_ids() if motor_ids is None else motor_ids)}
    def get_resolutions(self, motor_ids: list=None) -> dict: return {motor_id: self.get_motor_info(motor_id).resolution for motor_id in (self.get_motor_ids() if motor_ids is None else motor_ids)}
    def get_repeatbilities(self, motor_ids: list=None) -> dict: return {motor_id: self.get_motor_info(motor_id).repeatability for motor_id in (self.get_motor_ids() if motor_ids is None else motor_ids)}
    def get_search_ranges(self, beam_manager_type, platform, beam_manager_id, motor_ids: list=None) -> dict:
        return {motor_id: self.get_motor_info(motor_id).search_range_by_key(beam_manager_type, platform, beam_manager_id) \
                for motor_id in (self.get_motor_ids() if motor_ids is None else motor_ids)}
    def get_search_spaces(self, beam_manager_type, platform, beam_manager_id, motor_ids: list=None) -> dict:
        return {motor_id: self.get_motor_info(motor_id).search_space_by_key(beam_manager_type, platform, beam_manager_id) \
                for motor_id in (self.get_motor_ids() if motor_ids is None else motor_ids)}
    def get_search_transfer_ranges(self, beam_manager_type, platform, beam_manager_id, motor_ids: list=None) -> dict:
        return {motor_id: self.get_motor_info(motor_id).search_transfer_range_by_key(beam_manager_type, platform, beam_manager_id) \
                for motor_id in (self.get_motor_ids() if motor_ids is None else motor_ids)}
    def get_boundaries(self, platform, motor_ids: list=None) -> dict:
        return {motor_id: self.get_motor_info(motor_id).boundaries_by_key(platform) \
                for motor_id in (self.get_motor_ids() if motor_ids is None else motor_ids)}
    def get_initial_positions(self, beam_manager_type, platform, beam_manager_id, motor_ids: list=None) -> dict:
        return {motor_id: self.get_motor_info(motor_id).initial_position_by_key(beam_manager_type, platform, beam_manager_id)
                for motor_id in (self.get_motor_ids() if motor_ids is None else motor_ids)}
    def get_shifts_from_ideal(self, motor_ids: list=None) -> dict: return {motor_id: self.get_motor_info(motor_id).shift_from_ideal for motor_id in (self.get_motor_ids() if motor_ids is None else motor_ids)}
    def get_optimized(self, beam_manager_type, platform, beam_manager_id, motor_ids: list=None) -> dict:
        return {motor_id: self.get_motor_info(motor_id).optimized_by_key(beam_manager_type, platform, beam_manager_id) \
                for motor_id in (self.get_motor_ids() if motor_ids is None else motor_ids)}
    def get_motor_ids_to_optimize(self, beam_manager_type, platform, beam_manager_id):
        motor_ids_to_optimize = []
        for motor_id in self.get_motor_ids():
            if self.get_motor_info(motor_id).optimized_by_key(beam_manager_type, platform, beam_manager_id): motor_ids_to_optimize.append(motor_id)
        return motor_ids_to_optimize

    def to_dictionary(self) -> dict: return {motor_id: self.get_motor_info(motor_id).to_dictionary() for motor_id in self.get_motor_ids()}
    @classmethod
    def from_dictionary(self, dictionary: dict):
        motors_info = MotorsInfo()
        for motor_id in dictionary.keys():
            motors_info.add_motor_info(motor_id=motor_id,
                                       info=MotorInfo.from_dictionary(dictionary.get(motor_id)))
        return motors_info

class IMotionManager():
    @abc.abstractmethod
    def method_calling_type(self) -> MethodCallingType: raise NotImplementedError
    @abc.abstractmethod
    def set_method_calling_type(self, value: MethodCallingType): raise NotImplementedError
    @abc.abstractmethod
    def move_motor(self, motor_id: str, position: float, movement : Movement, units : Units = None, *args, **kwargs): raise NotImplementedError
    @abc.abstractmethod
    def get_motor_position(self, motor_id: str, units : Units = None, *args, **kwargs) -> float: raise NotImplementedError
    @abc.abstractmethod
    def get_motors_info(self) -> MotorsInfo : raise NotImplementedError
    @abc.abstractmethod
    def move_motors(self, motor_positions : dict, movement : Movement, units: dict=None, *args, **kwargs): raise NotImplementedError
    @abc.abstractmethod
    def get_motor_positions(self, motor_ids: list=None, units: dict=None, *args, **kwargs) -> dict: raise NotImplementedError
    @abc.abstractmethod
    def to_json(self, file_name, *args, **kwargs): raise NotImplementedError
    @classmethod
    @abc.abstractmethod
    def from_json(cls, file_name, *args, **kwargs): raise NotImplementedError

# ------------------------------------------------------------------ #

def format_motor_positions(motion_manager : IMotionManager):
    text = "Motors Position:"
    info = motion_manager.get_motors_info()
    for id in info.get_motor_ids():
        text += "\n" + id + " = " + str(motion_manager.get_motor_position(motor_id=id)) + " " + str(info.get_motor_info(id).units.name)
    return text

def print_motor_positions(motion_manager : IMotionManager):
    print(format_motor_positions(motion_manager))


