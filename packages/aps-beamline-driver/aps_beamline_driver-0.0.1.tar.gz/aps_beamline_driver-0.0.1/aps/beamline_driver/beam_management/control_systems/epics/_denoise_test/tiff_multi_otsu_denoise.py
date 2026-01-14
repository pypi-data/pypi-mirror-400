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
import os
import cv2 as cv
import numpy as np
from skimage.filters import threshold_multiotsu

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

from aps.beamline_driver.common.utility import calculate_projections_over_noise

factor               = 1e6
PIXEL_SIZE           = 6.5e-7
IMAGE_SIZE_PIXEL_HxV = [2160, 2560]

def load_image(file_path):
    if os.path.exists(file_path): return np.array(np.array(Image.open(file_path))).astype(np.float32).T
    else:                         raise ValueError('Error: wrong data path. No data is loaded:' + file_path)

image_raw = load_image(os.path.join(os.path.abspath(os.curdir), "sample_300ms_00001.tif"))

h_coord = np.linspace(- IMAGE_SIZE_PIXEL_HxV[0] / 2, IMAGE_SIZE_PIXEL_HxV[0] / 2, IMAGE_SIZE_PIXEL_HxV[0]) * PIXEL_SIZE * factor
v_coord = np.linspace(- IMAGE_SIZE_PIXEL_HxV[1] / 2, IMAGE_SIZE_PIXEL_HxV[1] / 2, IMAGE_SIZE_PIXEL_HxV[1]) * PIXEL_SIZE * factor

dx = (h_coord[1] - h_coord[0]) / 2.
dy = (v_coord[1] - v_coord[0]) / 2.
extent = [h_coord[0] - dx, h_coord[-1] + dx, v_coord[0] - dy, v_coord[-1] + dy]


### De-noised image with threshold based on upper left 10x10 region

image_0, histogram_h, histogram_v = calculate_projections_over_noise(histogram       = image_raw,
                                                                     noise_max_pos   = 10,
                                                                     noise_threshold = 1.1)

'''
Simple Otsu thresholding
'''


def get_otsu_thresholding(image):
    image_8bit = cv.convertScaleAbs(image, alpha=(255.0 / 65535.0))
    # Apply Otsu's thresholding
    ret, otsu_threshold = cv.threshold(image_8bit, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    return otsu_threshold


def get_thresholded_image(image, threshold):
    image_ = np.multiply(image, threshold)
    histogram_h = image_.sum(axis=1)
    histogram_v = image_.sum(axis=0)
    return image_, histogram_h, histogram_v

def plot_image_and_hist(image, title, h_hist, v_hist, h_coord=h_coord, v_coord=v_coord, xlim=None, ylim=None):
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, gridspec_kw={'width_ratios': [2, 1, 1]})
    fig.set_size_inches(12, 4)
    fig.gca().set_title(title)

    im = ax1.imshow(image, extent=extent, norm=LogNorm(vmin=0.01, vmax=np.max(image)))
    if xlim is None: xlim=[h_coord[0], h_coord[-1]]
    if ylim is None: ylim=[v_coord[0], v_coord[-1]]

    ax1.set_xlim(xlim[0], xlim[-1])
    ax1.set_ylim(ylim[0], ylim[-1])
    ax1.set_xlabel("Horizontal [um]")
    ax1.set_ylabel("Vertical [um]")
    plt.colorbar(mappable=im, ax=ax1)

    ax2.set_yscale('log')
    ax3.set_yscale('log')
    ax2.set_xlabel("Horizontal [um]")
    ax3.set_xlabel("Vertical [um]")
    ax2.plot(h_coord, h_hist)
    ax3.plot(v_coord, v_hist)
    ax2.set_xlim(xlim[0], xlim[-1])
    ax3.set_xlim(ylim[0], ylim[-1])


image_cv_raw = cv.imread(filename=os.path.join(os.path.abspath(os.curdir), "sample_300ms_00001.tif"), flags=cv.IMREAD_UNCHANGED).T

threshold_otsu = get_otsu_thresholding(image=image_cv_raw)
image_otsu, hist_h_otsu, hist_v_otsu = get_thresholded_image(image=image_cv_raw, threshold=threshold_otsu)

#plot_image_and_hist(image=image_raw.T, title='Image_raw', h_hist=image_raw.sum(axis=1), v_hist=image_raw.sum(axis=0), xlim=[-50, 50], ylim=[-50, 50])
#plot_image_and_hist(image=image_otsu.T, title='Image_Otsu', h_hist=hist_h_otsu, v_hist=hist_v_otsu, xlim=[-50, 50], ylim=[-50, 50])
#plot_image_and_hist(image=image_0.T, title='Image_Fixie', h_hist=histogram_h, v_hist=histogram_v, xlim=[-50, 50], ylim=[-50, 50])


'''
Simple Otsu thresholding
'''

MED_FILTER_SIZE = 31 # 11

image_cv_raw_8bit = cv.convertScaleAbs(image_cv_raw, alpha=(255.0/image_cv_raw.max()))
img_MedianBlur    = cv.medianBlur(image_cv_raw_8bit, MED_FILTER_SIZE)
thresholds        = threshold_multiotsu(img_MedianBlur)

regions = np.digitize(image_cv_raw_8bit, bins=thresholds)
regions[regions == 0] = 0
regions[regions == 1] = 1
regions[regions == 2] = 1

image_multi_otsu, hist_h_multi_otsu, hist_v_multi_otsu = get_thresholded_image(image = image_cv_raw, threshold = regions)
plot_image_and_hist(image  = image_multi_otsu.T,
                    title  = 'Image_multi_otsu',
                    h_hist = image_multi_otsu.sum(axis = 1),
                    v_hist = image_multi_otsu.sum(axis = 0),
                    xlim=[-50, 50], ylim=[-50, 50])
plt.show()
