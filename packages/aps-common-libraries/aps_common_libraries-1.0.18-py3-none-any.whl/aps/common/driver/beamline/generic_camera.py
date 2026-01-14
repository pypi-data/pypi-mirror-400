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
import os.path
import time
import glob
from epics import PV
import pickle
from collections import OrderedDict
import numpy as np
from PIL import Image
import pvapy as pva
from pvapy.utility.adImageUtility import AdImageUtility as adu
import shutil
import h5py
from aps.common.initializer import IniMode, register_ini_instance, get_registered_ini_instance
from aps.common.plot.image import apply_transformations

class CameraInitializationFile:
    @classmethod
    def is_initialized(cls): return hasattr(cls, "APPLICATION_NAME")

    @classmethod
    def initialize(cls,
                 application_name: str = "GENERIC-CAMERA",
                 ini_file_name: str = ".generic_camera_detector.json",
                 ini_mode : int = IniMode.LOCAL_JSON_FILE):
        register_ini_instance(ini_mode=ini_mode,
                              ini_file_name=ini_file_name,
                              application_name=application_name,
                              verbose=False)
        ini_file = get_registered_ini_instance(application_name)

        cls.APPLICATION_NAME      = application_name

        cls.SEND_STOP_COMMAND       = ini_file.get_boolean_from_ini(section="Execution", key="Send-Stop-Command", default=False)
        cls.SEND_SAVE_COMMAND       = ini_file.get_boolean_from_ini(section="Execution", key="Send-Save-Command", default=False)
        cls.REMOVE_IMAGE            = ini_file.get_boolean_from_ini(section="Execution", key="Remove-Image",      default=False)
        cls.WAIT_TIME               = ini_file.get_float_from_ini(  section="Execution", key="Wait-Time",         default=0.1)
        cls.EXPOSURE_TIME           = ini_file.get_float_from_ini(  section="Execution", key="Exposure-Time",     default=0.3)
        cls.PAUSE_AFTER_SHOT        = ini_file.get_float_from_ini(  section="Execution", key="Pause-After-Shot",  default=0.5)
        cls.PIXEL_FORMAT            = ini_file.get_int_from_ini(    section="Execution", key="Pixel-Format",      default=0)
        cls.INDEX_DIGITS            = ini_file.get_int_from_ini(    section="Execution", key="Index-Digits",      default=5)
        cls.FILE_NAME_PREFIX_TYPE   = ini_file.get_int_from_ini(    section="Execution", key="File-Name-Prefix-Type", default=0)
        cls.FILE_NAME_PREFIX_CUSTOM = ini_file.get_string_from_ini( section="Execution", key="File-Name-Prefix-Custom", default="custom_file_name")
        cls.IS_STREAM_AVAILABLE     = ini_file.get_boolean_from_ini(section="Execution", key="Is-Stream-Available", default=True)

        cls.PIXEL_SIZE            = ini_file.get_float_from_ini(section="Detector", key="Pixel-Size",   default=0.65e-6)
        cls.DETECTOR_RESOLUTION   = ini_file.get_float_from_ini(section="Detector", key="Resolution",   default=1.5e-6)

        cls.CAM_PIXEL_FORMAT      = ini_file.get_string_from_ini(section="Epics", key="Cam-Pixel-Format",      default="dp_andor3_skylark:cam1:PixelFormat")
        cls.CAM_ACQUIRE           = ini_file.get_string_from_ini(section="Epics", key="Cam-Acquire",           default="dp_andor3_skylark:cam1:Acquire")
        cls.CAM_EXPOSURE_TIME     = ini_file.get_string_from_ini(section="Epics", key="Cam-Exposure-Time",     default="dp_andor3_skylark:cam1:AcquireTime")
        cls.CAM_IMAGE_MODE        = ini_file.get_string_from_ini(section="Epics", key="Cam-Image-Mode",        default="dp_andor3_skylark:cam1:ImageMode")
        cls.TIFF_ENABLE_CALLBACKS = ini_file.get_string_from_ini(section="Epics", key="Tiff-Enable-Callbacks", default="dp_andor3_skylark:TIFF1:EnableCallbacks")
        cls.TIFF_FILENAME         = ini_file.get_string_from_ini(section="Epics", key="Tiff-File-Name",        default="dp_andor3_skylark:TIFF1:FileName")
        cls.TIFF_FILEPATH         = ini_file.get_string_from_ini(section="Epics", key="Tiff-File-Path",        default="dp_andor3_skylark:TIFF1:FilePath")
        cls.TIFF_FILENUMBER       = ini_file.get_string_from_ini(section="Epics", key="Tiff-File-Number",      default="dp_andor3_skylark:TIFF1:FileNumber")
        cls.TIFF_AUTOSAVE         = ini_file.get_string_from_ini(section="Epics", key="Tiff-Auto-Save",        default="dp_andor3_skylark:TIFF1:AutoSave")
        cls.TIFF_SAVEFILE         = ini_file.get_string_from_ini(section="Epics", key="Tiff-Write-File",       default="dp_andor3_skylark:TIFF1:WriteFile")
        cls.TIFF_AUTOINCREMENT    = ini_file.get_string_from_ini(section="Epics", key="Tiff-Auto-Increment",   default="dp_andor3_skylark:TIFF1:AutoIncrement")
        cls.PVA_IMAGE             = ini_file.get_string_from_ini(section="Epics", key="Pva-Image",             default="dp_andor3_skylark:Pva1:Image")

        default_image_directory = ini_file.get_string_from_ini(section="Image", key="Default-Image-Directory", default=os.path.abspath(os.curdir))
        current_image_directory = ini_file.get_string_from_ini(section="Image", key="Current-Image-Directory", default=os.path.abspath(os.curdir))

        cls.DEFAULT_IMAGE_DIRECTORY = os.path.abspath(os.curdir) if default_image_directory is None else default_image_directory.strip()
        cls.CURRENT_IMAGE_DIRECTORY = os.path.abspath(os.curdir) if current_image_directory is None else current_image_directory.strip()
        cls.DATA_FROM               = ini_file.get_int_from_ini( section="Image", key="Data-From", default=1)  # file
        cls.IMAGE_OPS               = ini_file.get_dict_from_ini(section="Image", key="Image-Ops", default={"file" : [], "stream" :["T", "FH", "FV"]}, type=str)

        return ini_file

    @classmethod
    def store(cls, ini_file=None):
        if ini_file is None: ini_file = get_registered_ini_instance(cls.APPLICATION_NAME)

        ini_file.set_value_at_ini(section="Execution", key="Send-Stop-Command",       value=cls.SEND_STOP_COMMAND)
        ini_file.set_value_at_ini(section="Execution", key="Send-Save-Command",       value=cls.SEND_SAVE_COMMAND)
        ini_file.set_value_at_ini(section="Execution", key="Remove-Image",            value=cls.REMOVE_IMAGE)
        ini_file.set_value_at_ini(section="Execution", key="Wait-Time",               value=cls.WAIT_TIME)
        ini_file.set_value_at_ini(section="Execution", key="Exposure-Time",           value=cls.EXPOSURE_TIME)
        ini_file.set_value_at_ini(section="Execution", key="Pause-After-Shot",        value=cls.PAUSE_AFTER_SHOT)
        ini_file.set_value_at_ini(section="Execution", key="Pixel-Format",            value=cls.PIXEL_FORMAT)
        ini_file.set_value_at_ini(section="Execution", key="Index-Digits",            value=cls.INDEX_DIGITS)
        ini_file.set_value_at_ini(section="Execution", key="File-Name-Prefix-Type",   value=cls.FILE_NAME_PREFIX_TYPE)
        ini_file.set_value_at_ini(section="Execution", key="File-Name-Prefix-Custom", value=cls.FILE_NAME_PREFIX_CUSTOM)
        ini_file.set_value_at_ini(section="Execution", key="Is-Stream-Available",     value=cls.IS_STREAM_AVAILABLE)

        ini_file.set_value_at_ini(section="Detector", key="Pixel-Size",   value=cls.PIXEL_SIZE)
        ini_file.set_value_at_ini(section="Detector", key="Resolution",   value=cls.DETECTOR_RESOLUTION)

        ini_file.set_value_at_ini(section="Epics", key="Cam-Pixel-Format",      value=cls.CAM_PIXEL_FORMAT)
        ini_file.set_value_at_ini(section="Epics", key="Cam-Acquire",           value=cls.CAM_ACQUIRE)
        ini_file.set_value_at_ini(section="Epics", key="Cam-Exposure-Time",     value=cls.CAM_EXPOSURE_TIME)
        ini_file.set_value_at_ini(section="Epics", key="Cam-Image-Mode",        value=cls.CAM_IMAGE_MODE)
        ini_file.set_value_at_ini(section="Epics", key="Tiff-File-Name",        value=cls.TIFF_FILENAME)
        ini_file.set_value_at_ini(section="Epics", key="Tiff-File-Path",        value=cls.TIFF_FILEPATH)
        ini_file.set_value_at_ini(section="Epics", key="Tiff-File-Number",      value=cls.TIFF_FILENUMBER)
        ini_file.set_value_at_ini(section="Epics", key="Tiff-Auto-Save",        value=cls.TIFF_AUTOSAVE)
        ini_file.set_value_at_ini(section="Epics", key="Tiff-Write-File",       value=cls.TIFF_SAVEFILE)
        ini_file.set_value_at_ini(section="Epics", key="Tiff-Auto-Increment",   value=cls.TIFF_AUTOINCREMENT)
        ini_file.set_value_at_ini(section="Epics", key="Tiff-Enable-Callbacks", value=cls.TIFF_ENABLE_CALLBACKS)
        ini_file.set_value_at_ini(section="Epics", key="Pva-Image",             value=cls.PVA_IMAGE)

        ini_file.set_value_at_ini(section="Image", key="Default-Image-Directory", value=cls.DEFAULT_IMAGE_DIRECTORY)
        ini_file.set_value_at_ini(section="Image", key="Current-Image-Directory", value=cls.CURRENT_IMAGE_DIRECTORY)
        ini_file.set_value_at_ini(section="Image", key="Data-From",               value=cls.DATA_FROM)
        ini_file.set_dict_at_ini( section="Image", key="Image-Ops",               values_dict=cls.IMAGE_OPS)

        ini_file.push()

class DataSource:
    Stream = "stream"
    File   = "file"

def get_data_from_int_to_string(data_from : int):
    if   data_from == 0: return DataSource.Stream
    elif data_from == 1: return DataSource.File
    else: raise ValueError("Data source not recognized")

def get_data_from_string_to_int(data_from : str):
    if   data_from == DataSource.Stream: return 0
    elif data_from == DataSource.File:   return 1
    else: raise ValueError("Data source not recognized")

GENERIC_CAMERA_STATUS_FILE = "generic_camera_status.pkl"

def get_file_name_prefix(file_name_prefix_type, file_name_prefix_custom, exposure_time):
    if file_name_prefix_type == 0:
        file_name_prefix = get_default_file_name_prefix(exposure_time)
    elif file_name_prefix_type == 1:
        custom_file_name_prefix = file_name_prefix_custom
        if not custom_file_name_prefix is None:file_name_prefix = custom_file_name_prefix
        else:                                  file_name_prefix = get_default_file_name_prefix(exposure_time)
    else:
        raise ValueError(f"Configuration Error, file name prefix type not recognized: {file_name_prefix_type}")

    return file_name_prefix

def get_default_file_name_prefix(exposure_time): return f"sample_{int(exposure_time * 1000)}ms"

def get_image_file_path(measurement_directory, file_name_prefix, image_index, index_digits, extension="tif", **kwargs) -> str:
    flat = "" if not kwargs.get("flat", False) else "flat_"

    return os.path.join(measurement_directory, (flat + file_name_prefix + f"_%0{index_digits}i.{extension}") % image_index)

def get_image_data(file_name):
    with h5py.File(file_name, 'r') as image_file:
        h_coord = image_file["stored_image/h_coord"][()]
        v_coord = image_file["stored_image/v_coord"][()]
        image   = image_file["stored_image/image"][()]

    return image, h_coord, v_coord

def get_image_data_array(directory_name):
    images = [get_image_data(f_single) for f_single in sorted(glob.glob(os.path.join(directory_name, ".hdf5")))]
    if len(images) == 0: raise IOError('Error: wrong data path. No data is loaded. {}'.format(directory_name))

    return np.array(images)

class GenericCamera():
    @classmethod
    def _get_image_stream_data(cls, PV_stream: PV, pixel_size, image_ops, **kwargs) -> [np.ndarray, np.ndarray, np.ndarray]:
        units = kwargs.get("units", "mm")

        _, image, _, _, _, _, _ = adu.reshapeNtNdArray(PV_stream.get(''))

        image = copy.deepcopy(image).astype(np.float32)

        factor = 1e6 if units == "um" else (1e3 if units == "mm" else (1e2 if units == "cm" else 1.0))

        size_h = image.shape[1]
        size_v = image.shape[0]

        h_coord = np.linspace(-size_h / 2, size_h / 2, size_h) * pixel_size * factor
        v_coord = np.linspace(-size_v / 2, size_v / 2, size_v) * pixel_size * factor

        h_coord, v_coord, image = apply_transformations(h_coord, v_coord, image, image_ops)

        return image, h_coord, v_coord

    @classmethod
    def _get_image_file_data(cls, measurement_directory, file_name_prefix, image_index, index_digits, pixel_size, image_ops, **kwargs) -> [np.ndarray, np.ndarray, np.ndarray]:
        units     = kwargs.get("units", "mm")
        file_path = kwargs.get("file_path", None)
        file_path = file_path if not file_path is None else get_image_file_path(measurement_directory, file_name_prefix, image_index, index_digits, **kwargs)

        if os.path.exists(file_path): image = np.array(np.array(Image.open(file_path))).astype(np.float32)
        else:                         raise ValueError('Error: wrong data path. No data is loaded:' + file_path)

        factor = 1e6 if units == "um" else (1e3 if units == "mm" else (1e2 if units == "cm" else 1.0))

        size_h = image.shape[1]
        size_v = image.shape[0]

        h_coord = np.linspace(-size_h / 2, size_h / 2, size_h) * pixel_size * factor
        v_coord = np.linspace(-size_v / 2, size_v / 2, size_v) * pixel_size * factor

        h_coord, v_coord, image = apply_transformations(h_coord, v_coord, image, image_ops)

        return image, h_coord, v_coord

    @classmethod
    def _store_image_data(cls, h_coord, v_coord, image, file_name):
        with h5py.File(file_name, 'w') as h5file:
            image_file = h5file.create_group("stored_image")
            image_file.create_dataset('h_coord', data=h_coord)
            image_file.create_dataset('v_coord', data=v_coord)
            image_file.create_dataset('image',   data=image)

    def __init__(self,
                 measurement_directory: str = None,
                 exposure_time: int = None,
                 status_file: str = GENERIC_CAMERA_STATUS_FILE,
                 file_name_prefix: str = None,
                 detector_delay: float = None,
                 mocking_mode: bool = False,
                 configuration_file = CameraInitializationFile):
        self.__configuration_file = configuration_file

        if not self.__configuration_file.is_initialized(): raise ValueError("Camera Configuration is not initialized")

        self.__exposure_time          = exposure_time if not exposure_time is None else self.__configuration_file.EXPOSURE_TIME
        self.set_measurement_file(measurement_directory, file_name_prefix)
        self.__status_file            = status_file if not status_file is None else GENERIC_CAMERA_STATUS_FILE

        self.__mocking_mode           = mocking_mode
        self.__send_stop_command      = self.__configuration_file.SEND_STOP_COMMAND
        self.__send_save_command      = self.__configuration_file.SEND_SAVE_COMMAND
        self.__is_stream_available    = self.__configuration_file.IS_STREAM_AVAILABLE

        if not self.__mocking_mode:
            self.__PV_dict = {
                "cam_acquire"          : PV(self.__configuration_file.CAM_ACQUIRE),       # 0="Done", 1="Acquire"
                "cam_exposure_time"    : PV(self.__configuration_file.CAM_EXPOSURE_TIME),
                "cam_image_mode"       : PV(self.__configuration_file.CAM_IMAGE_MODE),    # "0=Fixed" or "1=Continuous"
                "cam_pixel_format"     : PV(self.__configuration_file.CAM_PIXEL_FORMAT),  # "0=Mono8, 5=Mono16, 8=Mono12"
                "tiff_filename"        : PV(self.__configuration_file.TIFF_FILENAME),
                "tiff_filepath"        : PV(self.__configuration_file.TIFF_FILEPATH),
                "tiff_filenumber"      : PV(self.__configuration_file.TIFF_FILENUMBER),
                "tiff_autosave"        : PV(self.__configuration_file.TIFF_AUTOSAVE),
                "tiff_savefile"        : PV(self.__configuration_file.TIFF_SAVEFILE),
                "tiff_autoincrement"   : PV(self.__configuration_file.TIFF_AUTOINCREMENT),
                "tiff_enable_callbacks": PV(self.__configuration_file.TIFF_ENABLE_CALLBACKS),
                "pva_image"            : pva.Channel(self.__configuration_file.PVA_IMAGE),
            }

            if not self.__PV_dict["cam_acquire"].wait_for_connection(timeout=5.0): raise TimeoutError("Requested detector is not available")

            if detector_delay is None:
                self.__has_delay = False
            else:
                self.__has_delay      = True
                self.__detector_delay = detector_delay

            self.__detector_stop()
            self.__configure_camera(1)
        else:
            print("ImageCollector initialized in Mocking Mode")

    def __to_dict(self):
        dictionary = OrderedDict()
        dictionary["cam_image_mode"]        = self.__PV_dict["cam_image_mode"].get()
        dictionary["cam_exposure_time"]     = self.__PV_dict["cam_exposure_time"].get()
        dictionary["cam_pixel_format"]      = self.__PV_dict["cam_pixel_format"].get()
        dictionary["tiff_filename"]         = self.__PV_dict["tiff_filename"].get()
        dictionary["tiff_filepath"]         = self.__PV_dict["tiff_filepath"].get()
        dictionary["tiff_filenumber"]       = self.__PV_dict["tiff_filenumber"].get()
        dictionary["tiff_autosave"]         = self.__PV_dict["tiff_autosave"].get()
        dictionary["tiff_savefile"]         = self.__PV_dict["tiff_savefile"].get()
        dictionary["tiff_autoincrement"]    = self.__PV_dict["tiff_autoincrement"].get()
        dictionary["tiff_enable_callbacks"] = self.__PV_dict["tiff_enable_callbacks"].get()

        return dictionary

    def __to_pickle_file(self):
        if not self.__mocking_mode:
            self.__detector_stop()

            file = open(self.__status_file, 'wb')
            pickle.dump(self.__to_dict(), file)
            file.close()

    def __from_pickle_file(self):
        if not self.__mocking_mode:
            self.__detector_stop()

            file = open(self.__status_file, 'rb')
            dictionary = pickle.load(file)
            file.close()

            self.__PV_dict["cam_image_mode"].put(       dictionary["cam_image_mode"])
            self.__PV_dict["cam_exposure_time"].put(    dictionary["cam_exposure_time"])
            self.__PV_dict["cam_pixel_format"].put(     dictionary["cam_pixel_format"])
            self.__PV_dict["tiff_filename"].put(        dictionary["tiff_filename"])
            self.__PV_dict["tiff_filepath"].put(        dictionary["tiff_filepath"])
            self.__PV_dict["tiff_filenumber"].put(      dictionary["tiff_filenumber"])
            self.__PV_dict["tiff_autosave"].put(        dictionary["tiff_autosave"])
            self.__PV_dict["tiff_savefile"].put(        dictionary["tiff_savefile"])
            self.__PV_dict["tiff_autoincrement"].put(   dictionary["tiff_autoincrement"])
            self.__PV_dict["tiff_enable_callbacks"].put(dictionary["tiff_enable_callbacks"])

    def get_configuration_file(self): return copy.deepcopy(self.__configuration_file)

    def save_status(self):
        self.__to_pickle_file()

    def restore_status(self):
        self.__detector_stop()  # 1 waiting time
        self.__from_pickle_file()

    def set_measurement_file(self, measurement_directory=None, file_name_prefix=None):
        self.__measurement_directory  = measurement_directory if not measurement_directory is None else self.__configuration_file.CURRENT_IMAGE_DIRECTORY
        file_name_prefix              = file_name_prefix if not file_name_prefix is None else get_file_name_prefix(file_name_prefix_type=self.__configuration_file.FILE_NAME_PREFIX_TYPE,
                                                                                                                   file_name_prefix_custom=self.__configuration_file.FILE_NAME_PREFIX_CUSTOM,
                                                                                                                   exposure_time=self.__exposure_time)
        self.__file_name_prefix = file_name_prefix

    def collect_single_shot_image(self, image_index=1, **kwargs):
        if not self.__mocking_mode:
            self.__initialize_current_image(image_index)
            self.__detector_acquire() # 2 waiting time + exposure time
        else:
            time.sleep(self.get_total_acquisition_time())
            print("Mocking Mode: collected image #" + str(image_index))
        time.sleep(self.__configuration_file.PAUSE_AFTER_SHOT)

        data_from    = get_data_from_int_to_string(self.__configuration_file.DATA_FROM)
        image_ops    = self.__configuration_file.IMAGE_OPS[data_from]
        pixel_size   = self.__configuration_file.PIXEL_SIZE
        index_digits = self.__configuration_file.INDEX_DIGITS

        if data_from == DataSource.Stream:
            if not self.__is_stream_available: raise ValueError("Image stream is not availabe on this detector")

            image, h_coord, v_coord = GenericCamera._get_image_stream_data(PV_stream=self.__PV_dict["pva_image"],
                                                                           pixel_size=pixel_size,
                                                                           image_ops=image_ops,
                                                                           **kwargs)
        elif data_from == DataSource.File:
            image, h_coord, v_coord = GenericCamera._get_image_file_data(measurement_directory=self.__measurement_directory,
                                                                         file_name_prefix=self.__file_name_prefix,
                                                                         image_index=image_index,
                                                                         index_digits=index_digits,
                                                                         pixel_size=pixel_size,
                                                                         image_ops=image_ops,
                                                                         **kwargs)
        else:
            raise ValueError("Data source not recognized")

        file_name = get_image_file_path(measurement_directory=self.__measurement_directory,
                                        file_name_prefix=self.__file_name_prefix,
                                        image_index=image_index,
                                        index_digits=index_digits,
                                        extension="hdf5",
                                        **kwargs)

        if os.path.exists(file_name): shutil.copyfile(file_name, file_name + ".bkp")
        GenericCamera._store_image_data(h_coord, v_coord, image, file_name)

    def get_image_data(self, image_index: int = 1) -> [np.ndarray, np.ndarray, np.ndarray]:
        file_name = get_image_file_path(measurement_directory=self.__measurement_directory,
                                        file_name_prefix=self.__file_name_prefix,
                                        image_index=image_index,
                                        index_digits=self.__configuration_file.INDEX_DIGITS,
                                        extension="hdf5")

        return get_image_data(file_name)

    def end_collection(self): # to be done at the end of the data collection
        if not self.__mocking_mode:
            self.__PV_dict["tiff_autosave"].put(0)
            self.__PV_dict["tiff_autoincrement"].put(0)

    def set_idle(self):
        self.__detector_idle()

    def get_total_acquisition_time(self):
        return 3 * self.__configuration_file.WAIT_TIME + self.__exposure_time

    def __detector_idle(self):
        self.__detector_wait()
        self.__detector_stop()
        self.__detector_save()

    def __detector_acquire(self):
        self.__detector_start()
        self.__detector_idle()

    def __detector_start(self):
        self.__PV_dict["cam_acquire"].put(1)
        time.sleep(self.__configuration_file.WAIT_TIME)

    def __detector_stop(self):
        if self.__send_stop_command: self.__PV_dict["cam_acquire"].put(0)
        time.sleep(self.__configuration_file.WAIT_TIME)

    def __detector_save(self):
        if self.__send_save_command: self.__PV_dict["tiff_savefile"].put(1)

    def __detector_acquiring(self):
        return self.__PV_dict["cam_acquire"].get() in (1, "Acquiring")

    def __detector_done(self):
        return self.__PV_dict["cam_acquire"].get() in (0, "Done")

    def __initialize_current_image(self, index):
        self.__detector_stop()  # 1 waiting time
        self.__configure_camera(index)

        if self.__configuration_file.REMOVE_IMAGE:
            current_file_image = os.path.join(self.__measurement_directory, (self.__file_name_prefix + f"_%0{self.__configuration_file.INDEX_DIGITS}i.tif") % index)
            if os.path.exists(current_file_image):
                try: os.remove(current_file_image)
                except: pass

    def __configure_camera(self, index):
        self.__PV_dict["cam_image_mode"].put(0)
        self.__PV_dict["cam_pixel_format"].put(self.__configuration_file.PIXEL_FORMAT)
        self.__PV_dict["cam_exposure_time"].put(self.__exposure_time)
        self.__PV_dict["tiff_enable_callbacks"].put(1)
        self.__PV_dict["tiff_filepath"].put(self.__measurement_directory)
        self.__PV_dict["tiff_autosave"].put(1)
        self.__PV_dict["tiff_autoincrement"].put(0)
        self.__PV_dict["tiff_filename"].put(self.__file_name_prefix)
        if index > 0: self.__PV_dict["tiff_filenumber"].put(index)

    def __detector_wait(self):
        if not self.__has_delay:
            time.sleep(self.__exposure_time + self.__configuration_file.WAIT_TIME)
        else:
            time.sleep(self.__configuration_file.WAIT_TIME)  # wait for the detector to start
            kk = 0
            while self.__detector_acquiring():
                time.sleep(self.__detector_delay)
                kk += self.__detector_delay
                if kk > 120:
                    self.__detector_stop()
                    time.sleep(1)
                    self.__detector_start()
                    time.sleep(1)
                    kk = 0