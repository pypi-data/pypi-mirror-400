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

from PIL import Image
import numpy
import os

PIXEL_SIZE = 6.5e-7
IMAGE_SIZE_PIXEL_HxV = [2160, 2560]

def load_image(file_path):
    if os.path.exists(file_path): return numpy.array(numpy.array(Image.open(file_path))).astype(numpy.float32).T
    else:                         raise ValueError('Error: wrong data path. No data is loaded:' + file_path)

image = load_image(os.path.join(os.path.abspath(os.curdir), "../../../../../../../../../../../../Library/CloudStorage/Box-Box/Luca-Runyu/AI-Controller/tiff_noise/sample_300ms_00001.tif"))

factor = 1e6

h_coord = numpy.linspace(-IMAGE_SIZE_PIXEL_HxV[0] / 2, IMAGE_SIZE_PIXEL_HxV[0] / 2, IMAGE_SIZE_PIXEL_HxV[0]) * PIXEL_SIZE * factor
v_coord = numpy.linspace(-IMAGE_SIZE_PIXEL_HxV[1] / 2, IMAGE_SIZE_PIXEL_HxV[1] / 2, IMAGE_SIZE_PIXEL_HxV[1]) * PIXEL_SIZE * factor

from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm

dx = (h_coord[1]-h_coord[0])/2.
dy = (v_coord[1]-v_coord[0])/2.
extent = [h_coord[0]-dx, h_coord[-1]+dx, v_coord[0]-dy, v_coord[-1]+dy]

plt.figure(1)
plt.imshow(image.T, extent=extent, norm=LogNorm(vmin=0.01, vmax=numpy.max(image)))
plt.title("Image with noise (log)")
plt.xlabel("Horizontal [um]")
plt.ylabel("Vertical [um]")
plt.colorbar()

_, (ax1, ax2) = plt.subplots(1, 2)
plt.title("Projections (H - V, log)")
ax1.set_yscale('log')
ax2.set_yscale('log')
ax1.set_xlabel("Horizontal [um]")
ax2.set_xlabel("Vertical [um]")
ax1.plot(h_coord, image.sum(axis=1))
ax2.plot(v_coord, image.sum(axis=0))

from aps.beamline_driver.common.utility import calculate_projections_over_noise

image, histogram_h, histogram_v = calculate_projections_over_noise(histogram=image,
                                                                   noise_max_pos=10,
                                                                   noise_threshold=1.1)

plt.figure(3)
plt.imshow(image.T, extent=extent, norm=LogNorm(vmin=0.01, vmax=numpy.max(image)))
plt.title("Image denoised (log)")
plt.xlabel("Horizontal [um]")
plt.ylabel("Vertical [um]")
plt.colorbar()

_, (ax1, ax2) = plt.subplots(1, 2)
plt.title("Projections (H - V, log) denoised")
ax1.set_yscale('log')
ax2.set_yscale('log')
ax1.set_xlabel("Horizontal [um]")
ax2.set_xlabel("Vertical [um]")
ax1.plot(h_coord, histogram_h)
ax2.plot(v_coord, histogram_v)

plt.show()

