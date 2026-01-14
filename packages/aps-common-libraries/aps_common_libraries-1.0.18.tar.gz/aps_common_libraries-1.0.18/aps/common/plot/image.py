#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------- #
# Copyright (c) 2022, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2022. UChicago Argonne, LLC. This software was produced       #
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
import copy

import numpy
import numpy as np
from sympy.physics.quantum.gate import zy_basis_transform


def get_fwhm(histogram, bins):
    quote = numpy.max(histogram)*0.5
    cursor = numpy.where(histogram >= quote)

    if histogram[cursor].size > 1:
        bin_size    = bins[1]-bins[0]
        fwhm        = bin_size*(cursor[0][-1]-cursor[0][0])
        coordinates = (bins[cursor[0][0]], bins[cursor[0][-1]])
    else:
        fwhm = 0.0
        coordinates = None

    return fwhm, quote, coordinates

def get_sigma(histogram, bins):
    frequency = histogram/numpy.sum(histogram)
    average   = numpy.sum(frequency*bins)
    return numpy.sqrt(numpy.sum(frequency*((bins-average)**2)))

def get_rms(histogram, bins):
    frequency = histogram/numpy.sum(histogram)
    return numpy.sqrt(numpy.sum(frequency*(bins**2)))

def get_average(histogram, bins):
    frequency = histogram/numpy.sum(histogram)
    return numpy.sum(frequency*bins)

def get_peak_location(histogram, bins):
    return bins[numpy.argmax(histogram)]

from scipy.ndimage import median_filter

def get_peak_location_2D(x_array, y_array, z_array, smooth=False):
    if smooth: z_array = median_filter(z_array, size=3)
    indexes = numpy.unravel_index(numpy.argmax(z_array, axis=None), z_array.shape)

    return x_array[indexes[0]], y_array[indexes[1]], indexes[0], indexes[1]

def transpose(x, y, z): return y, x, z.T
def flip_h(z): return np.flip(z, 1)
def flip_v(z): return np.flip(z, 0)

def apply_transformations(x, y, z, ops : list):
    if ops is None or len(ops) == 0: return x, y, z

    for op in ops:
        op = op.strip()
        if   op == "T":  x, y, z = transpose(x, y, z)
        elif op == "FV": z = flip_v(z)
        elif op == "FH": z = flip_h(z)

    return x, y, z

def rebin_2D(x: numpy.ndarray, y: numpy.ndarray, z: numpy.ndarray, factor: float, exact: bool = False):
    if factor <= 1: raise ValueError("Rebinning factor should be > 1")

    original_shape = z.shape

    if not (x is None or y is None):
        if not original_shape[0] == x.shape[0]: raise ValueError(f"Incompatible shape: x ({x.shape[0]}) vs z.shape[0] ({z.shape[0]})")
        if not original_shape[1] == y.shape[0]: raise ValueError(f"Incompatible shape: y ({y.shape[0]}) vs z.shape[1] ({z.shape[1]})")

    if exact:
        if original_shape[0] % factor != 0: raise ValueError(f"Incompatible shape: z.shape[0] {z.shape[0]} is not divisible by the rebinning factor {factor}")
        if original_shape[1] % factor != 0: raise ValueError(f"Incompatible shape: z.shape[0] {z.shape[1]} is not divisible by the rebinning factor {factor}")

        new_shape = [int(original_shape[0] / factor),
                     int(original_shape[1] / factor)]

        new_z = z.reshape((new_shape[0], original_shape[0] // new_shape[0],
                           new_shape[1], original_shape[1] // new_shape[1])).mean(-1).mean(1)
    else:
        new_shape = [max(1, int(original_shape[0] / factor)),
                     max(1, int(original_shape[1] / factor))]
        block_shape = [original_shape[0] / new_shape[0],
                       original_shape[1] / new_shape[1]]

        new_z = np.zeros((new_shape[0], new_shape[1]))
        for i in range(new_shape[0]):
            for j in range(new_shape[1]):
                start_i = int(i * block_shape[0])
                end_i   = int((i + 1) * block_shape[0])
                start_j = int(j * block_shape[1])
                end_j   = int((j + 1) * block_shape[1])
                new_z[i, j] = z[start_i : end_i, start_j : end_j].mean()

    if not (x is None or y is None):
        new_x = numpy.linspace(x[0], x[-1], new_shape[0])
        new_y = numpy.linspace(y[0], y[-1], new_shape[1])
    else:
        new_x = None
        new_y = None

    return new_x, new_y, new_z

def rebin_1D(x : np.ndarray, y : np.ndarray, factor : float, exact: bool = False):
    if factor <= 1: raise ValueError("Rebinning factor should be > 1")

    original_shape = y.shape[0]

    if not x is None and not original_shape == x.shape[0]: raise ValueError(f"Incompatible shape: x ({x.shape[0]}) vs y ({original_shape})")
    if exact and original_shape % factor != 0: raise ValueError(f"Incompatible shape: y {original_shape} is not divisible by the rebinning factor {factor}")

    num_full_chunks = len(y) // factor

    reshaped = y[:num_full_chunks * factor].reshape(-1, factor)
    new_y    = reshaped.mean(axis=1)

    if not exact:
        remainder = len(y) % factor
        if remainder != 0:
            remaining_mean = y[-remainder:].mean()
            new_y = np.append(new_y, remaining_mean)

    if not x is None: new_x = numpy.linspace(x[0], x[-1], new_y.shape[0])
    else:             new_x = None

    return new_x, new_y