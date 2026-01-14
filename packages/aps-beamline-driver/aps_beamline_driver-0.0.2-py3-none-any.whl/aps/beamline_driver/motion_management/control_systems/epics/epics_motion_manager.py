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

from aps.beamline_driver.motion_management.facade import MotorsInfo, Movement, Units, MethodCallingType
from aps.beamline_driver.motion_management.abstract_motion_manager import AbstractMotionManager, Keys

from epics import PV

class EpicsMotionManager(AbstractMotionManager):

    def __init__(self, motors_info: MotorsInfo=None, json_file: str=None):
        super(EpicsMotionManager, self).__init__(motors_info=motors_info,
                                                 json_file=json_file,
                                                 method_calling_type=MethodCallingType.STANDARD,
                                                 platform=Keys.Platforms.Beamline)
        self._initialize_pvs()

    def _initialize_pvs(self):
        motors_info = self.get_motors_info()

        self._pvs_put = {}
        self._pvs_get = {}
        for motor_id in motors_info.get_motor_ids():
            motor_info = motors_info.get_motor_info(motor_id)
            self._pvs_put[motor_id] = PV(motor_info.legacy_ids[0])
            self._pvs_get[motor_id] = PV(motor_info.legacy_ids[1])

    def _move_motor(self, motor_id: str, position: float, movement : Movement, units : Units = None, *args, **kwargs):
        native_position = self._get_native_position(position,
                                                    units,
                                                    self.get_motors_info().get_motor_info(motor_id)) # redundant, but harmless

        self.__move_epics_motor(motor_id, native_position, movement, wait=kwargs.get("wait", True))

    def _get_motor_position(self, motor_id: str, units : Units = None, *args, **kwargs) -> float:
        native_position = self.__get_epics_motor_native_position(motor_id)

        return self._convert_native_position(native_position,
                                             units,
                                             self.get_motors_info().get_motor_info(motor_id)) # redundant, but harmless

    def __move_epics_motor(self, motor_id, native_position: float, movement : Movement, wait=True):
        if movement == Movement.ABSOLUTE:   self._pvs_put[motor_id].put(native_position, wait=wait)
        elif movement == Movement.RELATIVE: self._pvs_put[motor_id].put(self._pvs_get[motor_id].get() + native_position, wait=wait)
        else: raise ValueError("Movement not recognized")

    def __get_epics_motor_native_position(self, motor_id):
        return self._pvs_get[motor_id].get()
