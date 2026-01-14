# coding: utf-8
# Author: Gauthier Patin
# Licence: GNU GPL v3.0

import os
import pandas as pd
import numpy as np
import colour
import json
from typing import Optional, Union, List, Tuple
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter
import scipy.interpolate as sip
from scipy.interpolate import interp1d
import seaborn as sns
import matplotlib.pyplot as plt
from uncertainties import ufloat, ufloat_fromstr, unumpy
from pathlib import Path
import itertools
from datetime import datetime
import importlib.resources as pkg_resources
import xarray as xr
from scipy.interpolate import RegularGridInterpolator
import ipywidgets as ipw
from ipywidgets import *
from IPython.display import display, clear_output
import subprocess
from PIL import Image
from great_tables import GT, md, style, loc
import math
import msdb
import re

# underlying modules of the  microfading package
from . import plotting
from . import config
from . import process_rawfiles

####### DEFINE GENERAL PARAMETERS #######

# Chromacity coordinates (x,y) of D65 illuminants
D65 = colour.CCS_ILLUMINANTS["cie_10_1964"]["D65"]


# Dictionary used when plotting the colorimetric labels along axes
labels_eq = {
    'dE76': r'$\Delta E_{ab}$',
    'dE94': r'$\Delta E_{94}$',
    'dE00': r'$\Delta E_{00}$',         
    'dR_vis': r'$\Delta R_{vis}$',
    'dL*' : r'$\Delta L^*$',
    'da*' : r'$\Delta a^*$',
    'db*' : r'$\Delta b^*$',
    'dC*' : r'$\Delta C^*$',
    'dh' : r'$\Delta h$',    
    'L*' : r'$L^*$',
    'a*' : r'$a^*$',
    'b*' : r'$b^*$',
    'C*' : r'$C^*$',
    'h' : r'$h$', 
    'He' : 'MJ/m2',
    'Hv' : 'Mlxh',      
    'JND' : 'JND'  
}

# Dictionary to store the light dose units
dose_units = {'He':'He_MJ/m2', 'Hv':'Hv_Mlxh', 't': 't_sec'}


#### DATABASES RELATED FUNCTIONS ####


def create_DB():
    """Create the database files on your local computer

    Returns
    -------
    ipywidgets
        The function returns ipywidgets inside which you can enter the name of the database files and the location of these files on your computer. 
    """       

    return msdb.create_db()


def delete_device_info(key:Optional[str] = None):
    """Delete information about devices stored in the config_info.json file

    Parameters
    ----------
    key : Optional[str], optional
        Device ID value, by default None
        When None, it returns an ipywidget from which one can select the device ID.    
    """

    return config.delete_device_info(key=key)


def is_DB():
    """Check whether the databases files were created and registered.

    Returns
    -------
    (str, bool)
        If the dabasses files are created and registered, it returns True along with a print statement. Otherwise, it returns False.
    """
    

    # retrieve the config info about the databases
    config_db = config.get_config_info()['databases']

    # check whether the databases have been registered
    if len(config_db) == 0:
        print('The databases have not been registered. Please enter databases configuration info by using the function set_DB() or create the databases files (create_DB()). For more information on the databases, please consult the documentation: https://g-patin.github.io/microfading/databases-management/')
        return False

    db_files = ['projects_info.csv', 'objects_info.csv','devices.txt','institutions.txt', 'users_info.txt','object_types.txt', 'object_techniques.txt', 'object_materials.txt', 'object_creators.txt', 'white_standards.txt', 'lamps.txt']
        
    db_path = config.get_config_info()['databases']['path_folder']
    if all(list(map(os.path.isfile, [str(Path(db_path)/x) for x in db_files]))):
        print(f'All the database files were created and can be found in the following directory: {db_path}')            
        return True

    else:
        print(f'The database files were created, but one or several files are currently missing.')
        print(f'The following files ({db_files}) should be present in the following directory: {db_path}')
        return False


def get_databases_info():
    """Retrieve the info related to the databases."""
    return config.get_databases_info()


def get_datasets(MFT:Optional[str] = 'fotonowy', rawfiles:Optional[bool] = False, BWS:Optional[bool] = True, stdev:Optional[bool] = False):
    """Retrieve exemples of dataset files. These files are meant to give the users the possibility to test the MFT class and its functions.  

    Parameters
    ----------
    MFT : Optional[str], optional
        Microfading device that has been used to obtain the files, by default 'fotonowy'
        One can choose a single option among the following choices: 'fotonowy', 'sMFT', 
        'fotonowy' corresponds to the microfading device of the Polish company Fotonowy
        'sMFT' corresponds to stereo-MFT (see Patin et al. 2022. Journal of Cultural Heritage, 57)

    rawfiles : Optional[bool], optional
        Whether to get rawdata files, by default False
        The raw files were obtained from microfading analyses performed with the Fotonowy device and consist of four files per analysis.

    BWS : Optional[bool], optional
        Whether to include the microfading measurements on blue wool standards (BWS), by default True

    stdev : Optional[bool], optional
        Whether to have microfading measurements wiht standard deviation values, by default False
        It only works if the rawfiles parameters is set to 'False'. The rawfiles do not have standard deviation values.

    Returns
    -------
    list
        It returns a list of strings, where each string corresponds to the absolute path of a microfading measurement excel file. Subsequently, one can use the list as input for the MFT class. 
    """

    # Whether to select files with standard deviation values
    if stdev:
        if MFT == 'sMFT':
            data_files = [
                '2024-144_MF.BWS0024.G02_avg_BW1_reference_2024-08-02_MFT1.xlsx',
                '2024-144_MF.BWS0025.G02_avg_BW2_reference_2024-08-02_MFT1.xlsx',
                '2024-144_MF.BWS0026.G02_avg_BW3_reference_2024-08-02_MFT1.xlsx',                
            ]

        elif MFT == 'fotonowy':
            data_files = [
                '2024-144_MF.BWS0024.G01_avg_BW1_reference_2024-07-30_MFT2.xlsx',
                '2024-144_MF.BWS0025.G01_avg_BW2_reference_2024-08-02_MFT2.xlsx',
                '2024-144_MF.BWS0026.G01_avg_BW3_reference_2024-08-07_MFT2.xlsx',
                '2024-144_MF.dayflower4.G01_avg_0h_model_2024-07-30_MFT2.xlsx',
                '2024-144_MF.indigo3.G01_avg_0h_model_2024-08-02_MFT2.xlsx',
            ]
        
    else:
        if MFT == 'sMFT':
            data_files = [
                '2024-144_MF.BWS0026.04_G02_BW3_reference_2024-08-02_MFT1.xlsx',
                '2024-144_MF.BWS0025.04_G02_BW2_reference_2024-08-02_MFT1.xlsx',
                '2024-144_MF.BWS0024.04_G02_BW1_reference_2024-08-02_MFT1.xlsx',
                '2024-144_MF.yellowwood.01_G01_yellow_model_2024-08-01_MFT1.xlsx',
                '2024-144_MF.vermillon.01_G01_red_model_2024-07-31_MFT1.xlsx',
            ]

        elif MFT == 'fotonowy':
            data_files = [
                '2024-144_MF.BWS0024.01_G01_BW1_reference_2024-07-30_MFT2.xlsx',
                '2024-144_MF.BWS0025.01_G01_BW2_reference_2024-08-02_MFT2.xlsx',
                '2024-144_MF.BWS0026.01_G01_BW3_reference_2024-08-07_MFT2.xlsx',
                '2024-144_MF.vermillon3.01_G01_0h_model_2024-07-31_MFT2.xlsx',
                '2024-144_MF.yellowwood4.01_G01_0h_model_2024-08-01_MFT2.xlsx',
            ]
 
    # Whether to select rawfiles according to a choosen device
    if rawfiles:
        if MFT == 'sMFT':
            data_files = [
                '2024-144_BWS0024_04_G02_BW1_c01_000001.txt',
                '2024-144_yellowwood_01_G01_yellow_c01_000001.txt',
            ]

        elif MFT == 'fotonowy':
            data_files = [
                '2024-8200 P-001 G01 uncleaned_01-spect_convert.txt',
                '2024-8200 P-001 G01 uncleaned_01-spect.txt',
                '2024-8200 P-001 G01 uncleaned_01.txt',
                '2024-8200 P-001 G01 uncleaned_01.rfc',
                '2024-144 BWS0024 G01 BW1_01-spect_convert.txt',
                '2024-144 BWS0024 G01 BW1_01-spect.txt',
                '2024-144 BWS0024 G01 BW1_01.txt',
                '2024-144 BWS0024 G01 BW1_01.rfc',
            ]

    # Whether to include the BWS files or not
    if BWS == False:
        data_files = [x for x in data_files if 'BWS' not in x]


    # Get the paths to the data files within the package
    file_paths = []
    for file_name in data_files:
        
        with pkg_resources.path('microfading.datasets', file_name) as data_file:
             file_paths.append(data_file)


    return file_paths   


def get_comments_info():
    """Retrieve the information regarding the comments recorded inside raw microfading files. 
    """
    return config.get_comments_info()


def get_config(key:Optional[str] = 'all'):
    """Retrieve the content of the config_info.json file

    Parameters
    ----------
    key : str, optional
        Give you the possibility to retrieve a specific category of information, by default 'all'
        One can enter a key value among the following list: ['colorimetry', 'databases', 'devices', 'exposure', 'filters', 'functions', 'lamps', 'light_dose', 'institution', 'report_figures']

    Returns
    -------
    dict
        It returns the information inside a dictionary.
    """
    return config.get_config_info(key=key)


def get_config_path():
    """Retrieve the absolute path of the config_info.json file.   
    """
    return config.get_config_path()


def get_colorimetry_info():
    """Retrieve the colorimetric information (observer, illuminant, and white standard) recorded in the config_info.json file of the microfading package.

    Returns
    -------
    pandas dataframe or string
        It returns the information inside a dataframe if they have been recorded.
    """    
    return config.get_colorimetry_info()


def get_devices_info():
    """Retrieve the configuration information related to the devices.

    Returns
    -------
    pandas dataframe
        It returns the list of devices inside a pandas dataframe with four columns: 'Id', 'name', 'description', 'process_function'
    """    
    return config.get_devices_info()


def get_exposure_conditions():
    """Retrieve the exposure lighting conditions recorded in the config_info.json file of the microfading package.

    Returns
    -------
    pandas dataframe or string
        It returns the information inside a dataframe if they have been recorded.
    """   
    return config.get_exposure_conditions()


def get_institution_info():
    """Retrieve the information related to the institution that performed the microfading analysis.

    Returns
    -------
    pandas dataframe
        It returns the institution info inside a pandas dataframe.
    """    
    return config.get_institution_info()


def get_light_dose_info():
    """Retrieve the light dose info recorded in the config_info.json file of the microfading package.

    Returns
    -------
    pandas dataframe or string
        It returns the information inside a dataframe if they have been recorded.
    """       
    return config.get_light_dose_info()


def get_parameters_info():
    """Retrieve the names of the parameters used in the info tab of interim files.

    Returns
    -------
    list
        It returns a list containing the parameters used in the info tab of interim files.
    """

    datasets_folder = Path(__file__).parent / 'datasets'
    datasets_files = [x for x in os.listdir(datasets_folder) if '.xlsx' in x]

    df_dataset_file = pd.read_excel(Path(__file__).parent / 'datasets' / datasets_files[0], sheet_name='info', index_col='parameter')
    parameters = list(df_dataset_file.index)

    return parameters


def process_rawdata(
        
    files: list,
    device: str,
    filenaming:Optional[str] = 'none',
    folder:Optional[str] = '.',
    db:Optional[bool] = 'default',
    comment:Optional[str] = '',
    fading_mode:Optional[str] = 'default',
    waiting_time:Optional[int] = 1,
    authors:Optional[str] = 'XX',
    white_standard:Optional[str] = 'default',
    rounding:Union[int,tuple,list] = (4,3),
    interpolate_wl:Union[tuple,str] = 'default',
    interpolate_exposure:Union[tuple,str] = ('He', 0.1),
    interpolation:Optional[bool] = 'default',
    dose_unit:Optional[str] = 'default',
    step:Optional[float | int] = 0.1,
    average:Optional[int] = 'undefined',
    observer:Optional[str] = 'default',
    illuminant:Optional[str] = 'default',
    background:Optional[str] = 'undefined',
    beam_power:Optional[tuple] = None,
    language:Optional[str] = None,
    output_format:Optional[str] = 'xlsx',
    delete_files:Optional[bool] = 'default',
    return_filename:Optional[bool] = False
    ):
    """
    Process the microfading raw files created by the software that performed the microfading analysis. 


    Parameters
    ----------
    files : list
        A list of string that corresponds to the absolute path of the raw files.
    
    device : str
        Define the  microfading that has been used to generate the raw files ('fotonowy'). Currently, this function can only process raw files obtained with a Fotonowy. Don't hesitate to contact us, if you would like process your own specific microfading raw files with our package.

        If you registered your microfading device using the function set_devices_info() (for more information about it: https://g-patin.github.io/microfading/retrieve-test-datasets/), you can also entered the ID number of your device and it will directly take into account the parameters and information that you provided. 
    
    filenaming : [str | list], optional
        Define the filename of the output excel file, by default 'none' 
        When 'none', it uses the filename of the raw files
        When 'auto', it creates a filename based on the info provided by the databases
        A list of parameters provided in the info sheet of the excel output can be used to create a filename   

    folder : str, optional
        Folder where the final data files should be saved, by default '.'
    
    db : bool, optional
        Whether to make use of the databases, by default False
        When True, it will populate the info sheet in the interim file (the output excel file) with the data found in the databases.
        Make sure that the databases were created and that the information about about the project and the objects were recorded.
    
    comment : str, optional
        Whether to include a comment in the final excel file, by default ''
    
    authors : str, optional
        Initials of the persons that performed and processed the microfading measurements, by default 'XX' (unknown).
        Make sure that you registered the persons in the users.txt file (see function 'add_users' of the msdb package).
        If there are several persons, use a dash to connect the initials (e.g: 'JD-MG-OL').
    
    white_standard : str, optional
        ID number of the white standard used when performing the microfading analyses, by default 'default'
        When 'default', it will search for the registered values in the config_info.json file. If you have not registered any values, it assumes that you used the Fotolon provided by Fotonowy.
    
    rounding : [int, tuple], optional
        Rounding the spectral and colorimetric coordinates, by default (4,3)
        The value corresponds to the amount of digits after the decimal separator.
        When an integer is provided, it is applied to both the spectral and colorimetric value.
        When a tuple is provided, the first value relates to the spectral values while the second relates to the colorimetric values.

    interpolation : bool, optional
        Whether to interpolate the spectral and colorimetric data, by default True
        When True, it will interpolate the data according to the "dose_unit" and "step" values provided in the following parameters.
        When True, it will also interpolate the spectral values along the wavelengths (1 value every 1 nm).                 
        
    dose_unit : str, optional
        The unit of the light dose energy for which the spectral values are being interpolated, by default 'default'
        When 'default', it will search for the registered values in the config_info.json file. If you have not registered any values, it will select 'He' by default.
        When 'He', it performs interpolation based on the radiant exposure (MJ/m²) and for which you can define a step (see next parameter)
        When 'Hv', it performs interpolation based on the exposure dose (Mlxh) and for which you can define a step (see next parameter)
        When 't', it performs interpolation based on the exposure duration (sec) and for which you can define a step (see next parameter) 

    step : [float  |  int], optional
        Interpolation step related to the scale previously mentioned ('He', 'Hv', 't'), by default 0.1

    average : [int], optional
        Average of the measurements, by default 'undefined'
        If you use always the same average value, you can save it up in the config_info.json file (use the set_devices_info() function). Then enter 'default' as  value for the average parameter in order to retrieve the average value savied in the config file.

    observer : str, optional
        Reference CIE *observer* in degree ('10deg' or '2deg'). by default 'default'.
        When 'default', it fetches the observer value recorded in the db_config.json file of the package. If no value has been recorded, then it sets the observer value to '10deg'. 

    illuminant : (str, optional)  
        Reference CIE *illuminant*. It can be any value of the following list: ['A', 'B', 'C', 'D50', 'D55', 'D60', 'D65', 'D75', 'E', 'FL1', 'FL2', 'FL3', 'FL4', 'FL5', 'FL6', 'FL7', 'FL8', 'FL9', 'FL10', 'FL11', 'FL12', 'FL3.1', 'FL3.2', 'FL3.3', 'FL3.4', 'FL3.5', 'FL3.6', 'FL3.7', 'FL3.8', 'FL3.9', 'FL3.10', 'FL3.11', 'FL3.12', 'FL3.13', 'FL3.14', 'FL3.15', 'HP1', 'HP2', 'HP3', 'HP4', 'HP5', 'LED-B1', 'LED-B2', 'LED-B3', 'LED-B4', 'LED-B5', 'LED-BH1', 'LED-RGB1', 'LED-V1', 'LED-V2', 'ID65', 'ID50']. by default 'default'.
        When 'default', it fetches the illuminant value recorded in the db_config.json file of the package. If no value has been recorded, then it sets the illuminant value to 'D65'.      

    language : Optional[str], optional
        The language of the computer used to perform the microfading analyses, by default None
        When None, English is assumed to be the language that was used.
        If you are working on a Windows computer, you can use of the following languages (non-exhaustive list) : 'en', 'fr', 'it', 'nl', 'de', 'es'.
        If you are working on a Linux OS, open a terminal, enter " locale -a ", and choose one language among the returned list.
        For more information, consult the online documentation (https://g-patin.github.io/microfading/language-setting/).
    
    output_format : str, optional
        Output file format for the interim files, by default 'xlsx'.
        By default, the interim files will be saved as '.xlxs' (excel). When 'ods', it will save the output files as '.ods', which is the open source version of excel.
        
    delete_files : bool, optional
        Whether to delete the raw files, by default 'default'

    return_filename : Optional[bool], optional
        Whether to return the filename of the created excel file that contains the microfading data and metadata, by default True

    Returns
    -------
    Excel file
        It returns an excel file composed of three tabs (info, CIELAB, spectra).
    """
    
    # Load the config_info file    
    config_info = config.get_config_info()
    
    
    # Set the db value
    if db == 'default':
        if len(config_info['databases']) == 0:
            db = False            
        else:
            db = config_info['databases']['usage']


    # Is the device recorded ?
    if device not in config_info['devices'].keys():
        pass


    # Set the average value (not relevant for all microfading devices)
    if average == 'default':
        if len(config_info['device']) == 0:
            average = 'undefined'
        else:
            average = config_info['device'][device]['average']   
         

    # Set the observer value
    if observer == 'default':        
        if len(config_info['colorimetry']) == 0:
            observer = '10deg'
        else:
            observer = config.get_colorimetry_info().loc['observer'].values[0]

    
    # Set the illuminant value
    if illuminant == 'default':
        if len(config_info['colorimetry']) == 0:
            illuminant = 'D65'
        else:
            illuminant = config.get_colorimetry_info().loc['illuminant'].values[0]


    # Set the interpolation value
    if interpolation == 'default':
        if len(config_info['devices']) == 0:
            interpolation = True
        elif device in config_info['devices'].keys():
            interpolation = config_info['devices'][device]['interpolation']
        else:
            interpolation = True

    
    # Set the dose unit value
    if dose_unit == 'default':
        if len(config_info['light_dose']) == 0:
            dose_unit = 'He'
        elif device in config_info['devices'].keys():
            dose_unit = config_info['devices'][device]['dose_unit'] .split('_')[0] 
        else:
            dose_unit = 'He'

    elif dose_unit not in ['t', 'He', 'Hv']:
        return f'The dose unit value that you entered {dose_unit} is not valid. Please choose a dose unit among the following values ("defaut", "t", "He", "Hv")'
      
    
    # Set the white reference value
    if white_standard == 'default':
        if len(config_info['devices']) == 0:
            white_standard = 'default'

        elif device.lower() in ['fotonowy', 'stereo', 'smft']:
            white_standard = 'default'        

        elif device not in config.get_devices_info().columns:
            return f'The device value you entered ({device}) cannot be found in the registered list of devices ({config.get_devices_info().columns}). Please register the device or enter a valid device ID.'
        
        else:
            white_standard = config.get_devices_info()[device]['white_standard']
    
    # Set the delete_files value
    if delete_files == 'default' and db==True:
        if len(config_info['devices']) == 0:
            delete_files = False 

        else:
            delete_files = config.get_devices_info()[device]['delete_rawfiles']

    # Retrieve the process function
    if device.lower() in ['fotonowy', 'smft', 'stereo']:
        process_function = device.lower()

    else:
        process_function = config_info['devices'][device]['process_function']
    
    
    # Set the fading mode
    if fading_mode == 'default':
        if len(config_info['devices']) == 0 or device not in config_info['devices'].keys():
            if device.lower() in ['fotonowy', 'oriel']:
                fading_mode = 'continuous'
            elif device.lower() in ['smft', 'stereo']:
                fading_mode = 'alternate'

        else:
            fading_mode = config_info['devices'][device]['fading_mode']            
    
    
    # Run the process_rawfiles function
    if 'fotonowy' in process_function:
        return process_rawfiles.MFT_fotonowy(files=files, filenaming=filenaming, folder_output=folder, db=db, comment=comment, device_nb=device, authors=authors, white_standard=white_standard, rounding=rounding, interpolation=interpolation, dose_unit=dose_unit, step=step, average=average, observer=observer, illuminant=illuminant, background=background, language=language,output_format=output_format, delete_files=delete_files, return_filename=return_filename)

    
    elif 'stereo' in process_function:
        return process_rawfiles.MFT_stereo(files=files, filenaming=filenaming, folder_output=folder, db=db, comment=comment, device_nb=device, fading_mode=fading_mode, waiting_time=waiting_time, authors=authors, white_standard=white_standard, rounding=rounding, interpolate_wl=interpolate_wl, interpolate_exposure=interpolate_exposure, observer=observer, illuminant=illuminant, background=background, beam_power=beam_power, delete_files=delete_files, return_filename=return_filename)
    

def reset_config(keys:Union[str, list] = 'all'):
    """Reset the content of config_info.json to its initial state, i.e. an empty dictionary.

    Parameters
    ----------
    keys : Union[str, list], optional
        Select which dictionaries inside the config_info file to reset by entering the keys related to each dictionary, by default 'all'
        The following keys are valid: 'colorimetry', 'comments', 'databases', 'devices', 'exposure', 'filenaming', 'filters', 'functions', 'light_dose', 'lamps', 'institution', 'report_figures'.

        When 'all', it resets all the dictionaries.
    """
    
    return config.reset_config(keys=keys)


def set_colorimetry_info():
    """Record the colorimetric information (observer, illuminant, white standard) in the config_info.json file of the microfading package.
    """
    return config.set_colorimetry_info()


def set_comments_info():
    """Set the type and position of info recorded in the comments section of raw microfading files.    
    """
    return config.set_comments_info()


def set_devices_info():
    """Record the device info in the config_info.json file of the microfading package.
    """
    return config.set_devices_info()


def set_exposure_conditions():
    """Record the exposure lighting conditions in the config_info.json file of the microfading package.
    """
    return config.set_exposure_conditions()
    

def set_DB(folder_path:Optional[str] = '', use:Optional[bool] = True):
    """Record the databases info in the config_info.json file of the microfading package.

    Parameters
    ----------
    folder_path : Optional[str], optional
        Location of the database files on your local computer, by default ''

    use : Optional[bool], optional
        Whether the functions of the microfading package should use by default the database files, by default True

    """
    
    return config.set_db(folder_path=folder_path, use=use)
    

def set_filenaming():
    """Record the filenaming info in the config_info.json file of the microfading package.
    """
    return config.set_filenaming()


def set_light_dose():
    """Record the unit of the light dose in the config_info.json file of the microfading package.
    """    
    return config.set_light_dose()


def set_institution_info():
    """Set the information regarding your institution. As a user of the microfading package, you can enter information regarding your professional environment. These information will be automatically added in the microfading data file and inside the reports.

    Returns
    -------
    It returns several ipywdigets where you can enter the information regarding your professional environment.
    """
    return config.set_institution_info()


def set_report_figures():
    """Configure some of the parameters when creating figures for reports.    
    """
    print('Work in progress. Function not implemented yet.')
    return 
    return config.set_report_figures()



#### MICROFADING CLASS ####         

class MFT(object):

    def __init__(self, files:list, BWS:Optional[bool] = True) -> None:
        """Instantiate a Microfading (MFT) class object in order to manipulate and visualize microfading analysis data.

        Parameters
        ----------
        files : list
            A list of string, where each string corresponds to the absolute path of text or csv file that contains the data and metadata of a single microfading measurement. The content of the file requires a specific structure, for which an example can be found in "datasets" folder of the microfading package folder (Use the get_datasets function to retrieve the precise location of such example files). If the file structure is not respected, the script will not be able to properly read the file and access its content.

        BWS : bool, optional
            When False, it ignores the measurements performed on BWS samples if included. 
        
        """
        self.files = files
        self.BWS = BWS        

        if self.BWS == False:
            self.files = [x for x in self.files if 'BW' not in x.name]

       
    def __repr__(self) -> str:
        return f'Microfading data class - Number of files = {len(self.files)}'
       
    
    def add_info(self, parameters:Union[list,str], values:Union[list,str,int]):
        """Add information inside the info tab of microfading interim files.

        Parameters
        ----------
        parameters : Union[list,str]
            Parameters defined in the info tab of microfading interim files. A single parameter as a string or a list of parameters can be given.
            When a list of parameters is given, make sure that the length of parameters is equal to the length of values. 
            For a list of valid parameters, use the function get_parameters_info().

        values : Union[list,str,int]
            The new values that will be added in the info tab. 

        Raises
        ------
        ValueError
            If the parameter is invalid, it will return an error message.
        """

        if isinstance(parameters, str):
            parameters = [parameters]

        if isinstance(values, (str,int,float)):
            values = [values]        

        if len(parameters) == 1 and isinstance(values, list):
            values = [values]


        info_df = self.get_metadata()

        for parameter, value in zip(parameters,values):
                       
            
            # List available parameters if parameter not found
            if parameter not in info_df.index:
                raise ValueError(f"Parameter '{parameter}' not found in the 'info' sheet.\nAvailable parameters: {list(info_df.index)}")

            info_df.loc[parameter] = value

        
        for col, file in zip(info_df.columns, self.files):

            df_cl = pd.read_excel(file, sheet_name='CIELAB') 
            df_sp = pd.read_excel(file, sheet_name='spectra') 
            df_info = info_df[col]            
            df_info.name = 'value'
            
            # Write all sheets back to the Excel file
            with pd.ExcelWriter(file) as writer:

                df_info.to_excel(writer, sheet_name='info', index=True)
                df_cl.to_excel(writer, sheet_name="CIELAB", index=False)
                df_sp.to_excel(writer, sheet_name="spectra", index=False)
    
    
    def compute_delta(self, coordinates:Optional[list] = ['dE00'], dose_unit:Optional[list] = 'He', dose_values:Union[int, float, list, tuple] = 'all', derivation:Optional[bool] = False, rounding:Optional[int] = 4, concat:Optional[bool] = True):
        """Retrieve the CIE delta values for a given set of colorimetric coordinates corresponding to the given microfading analyses.

        Parameters
        ----------
        coordinates : list, optional
            List of colorimetric coordinates, by default ['dE00']
            Any of the following coordinates can be added to the list: 'dE76', 'dE00', 'dR_vis' , 'L*', 'a*', 'b*', 'C*', 'h'.

        dose_unit : str, optional
            Define the light energy dose, by default 'He'
            Any of the following units can be entered: 'He', 'Hv', 't'. Where 'He' corresponds to radiant energy (MJ/m2), 'Hv' to exposure dose (Mlxh), and 't' to times (sec)

        dose_values : Union[int, float, list, tuple], optional
            Dose values for which the colourimetric values will be returned, by default 'all'
            When 'all', it returns the colourimetric values for all the dose values available in the given input data files.
            A single dose value (an integer or a float number) can be entered.
            A list of dose values, as integer or float, can also be entered.
            A tuple of three values (min, max, step) will be used in a numpy.arange() function to return an array of dose values. 

        derivation : bool, optional
            Whether to return the first derivative values of the desired coordinates, by default False

        rounding : int, optional
            Rounding of the colorimetric values, by default 4
            The value corresponds to the amount of digits after the decimal separator.

        concat : bool, optional
            Whether to concat the data column-wise
            When True, it returns a single pandas dataframe
            When False, it returns a list of pandas dataframes


        Returns
        -------
        A list of pandas dataframes
            It returns a a list of pandas dataframes where each column corresponds to a light energy dose or a desired coordinate.
        """          

        # Retrieve the data        
        cielab_data = self.read_files(sheets=['CIELAB'])
        cielab_data = [x[0] for x in cielab_data]       

        # Rename the LabCh coordinates to dL*, da*, db*, dC*, dh
        coordinates = [f'd{x}' if x in ['L*','a*','b*','C*','h'] else x for x in coordinates]

        # Compute the delta values
        deltas = self.get_cielab(coordinates=coordinates, dose_unit=dose_unit, dose_values=dose_values, rounding=rounding, concat=False)

        # Whether to compute the first derivation 
        if derivation:
            deltas = [pd.DataFrame(np.gradient(x.T.values, x.index, axis=1).T, columns=x.columns, index=x.index) for x in deltas]

        if concat:
            deltas = pd.concat(deltas, axis=1)

        return deltas     
   
    
    def compute_fitting(self, plot:Optional[bool] = True, return_data:Optional[bool] = False, dose_unit:Optional[str] = 'Hv', coordinate:Optional[str] = 'dE00', equation:Optional[str] = 'power_3p', initial_params:Optional[List[float]] = 'auto', bounds:Optional[list] = None, x_range:Optional[Tuple[int]] = (0,5.1,0.1), save: Optional[bool] = False, path_fig: Optional[str] = 'cwd') -> Union[None, Tuple[np.ndarray, np.ndarray]]:
        """Fit the values of a given colourimetric coordinates. 

        Parameters
        ----------
        plot : bool, optional
            Whether to show the fitted data, by default True

        return_data : bool, optional
            Whether to return the fitted data, by default False

        dose_unit : string, optional
            Unit of the light energy dose, by default 'He'
            Any of the following units can be used: 'He', 'Hv', 't'. Where 'He' corresponds to radiant energy (MJ/m2), 'Hv' to exposure dose (Mlxh), and 't' to times (sec)

        coordinate : string, optional
            Select the desired colourimetric coordinate from the following list: ['L*', 'a*','b*', 'C*', 'h', 'dL*', 'da*','db*', 'dC*', 'dh', 'dE76', 'dE00', 'dR_vis'], by default 'dE00'

        equation : str, optional
            Mathematical equation used to fit the coordinate values, by default 'c0*(x**c1)'.
            Any others mathematical can be given. The following equation is often relevant for fitting microfading data: '((x) / (c0 + (c1*x))) + c2'.

        initial_params : List[float], optional
            Initial guesses of the 'c' parameters given in the equation (c0, c1, c2, etc.), by default [0.1, 0.0]

        bounds : List[float], optional
            Bound with lower and upper limits the parameters of the equation computed by the algorithm, by default None.
            
        x_range : Tuple[int], optional
            Values along which the fitted values should be computed (start, end, step), by default (0, 1001, 1)

        save : bool, optional
            Whether to save the plot, by default False

        path_fig : str, optional
            Absolute path of the figure to be saved, by default 'default'

        Returns
        -------
        Union[None, Tuple[np.ndarray, np.ndarray]]
            It returns a typle of four element: fitted_parameters, fitted_data, pcov values, r_squared value. When plot is set to True, a figure plotting the x and fitted y values will appear.
        """

        # Retrieve the range light dose values
        doses = {'He':'He_MJ/m2', 'Hv':'Hv_Mlxh', 't': 't_sec'}  
        x_model = np.arange(*x_range)
           
        # Retrieve the data        
        all_data = []

        for data in self.get_data(data='cl'):
            if 'mean' in data.columns.get_level_values(1):
                cl_mean_data = data.xs(key='mean', axis=1, level=1)    # the mean colorimetric data
                doses_data = data.xs(key='nominal', axis=1, level=1)   # the light energy data
                
                all_data.append(pd.concat([doses_data, cl_mean_data], axis=1))

            else:
                all_data.append(data.xs(key='nominal', axis=1, level=1))                

        # Added the delta LabCh values to the data dataframes
        coordinates = ['L*', 'a*', 'b*', 'C*', 'h']
        data = [d.assign(**{f'd{coord}': d[coord] - d[coord].values[0] for coord in coordinates}) for d in all_data]
                
        # Select the wanted dose_unit and coordinate
        selected_data = [x[[doses[dose_unit], coordinate]] for x in data]
        selected_data = [x.set_index(x.columns[0]) for x in selected_data]
        
        # Define the fitting equation and bounds
        config_functions = get_config()['functions']
        existing_equations = list(config_functions.keys())
        
    
        if equation in existing_equations:
            if bounds == None:
                bounds = eval(config_functions[equation]['bounds'])
            equation = config_functions[equation]['expression']           
                
        # Define the function to fit
        def fit_function(x, *params):
            param_dict = {f'c{i}': param for i, param in enumerate(params)}
            param_dict['x'] = x
            return eval(equation, globals(), param_dict)        
        
        # Create an empty dataframe for the fitted data
        fitted_data = pd.DataFrame(index=pd.Series(x_model))

        # Empty list to store the labels
        fitted_labels = []

        # Emtpy list to store the optimized parameters
        fitted_parameters = []

        if initial_params == 'auto':
            initial_params = ['auto']

        initial_params = initial_params * len(self.files)

        
        for d, p in zip(selected_data,initial_params):

            # retrieve the x(light dose) and y(coordinate) values
            x_data, y_data = d.index, d.iloc[:,0].values

            # estimate the initial parameters
            if p == 'auto':  

                y_diff = y_data[-1] - y_data[0]

                if equation == "c0*x":
                    if y_diff < 0:
                        p = [-0.1]
                    elif y_diff > 0:
                        p = [0.1]
                    elif y_diff == 0:
                        p  = [0]

                elif equation == "c0*x+c1":                    

                    if y_diff < 0:
                        c0 = -0.1
                    elif y_diff > 0:
                        c0 = 0.1
                    elif y_diff == 0:
                        c0  = 0

                    c1 = y_data[0]
                    p = [c0,c1]

                elif equation == "c0*(x**c1)":                    

                    if y_diff < 0:
                        c0 = -0.1
                    elif y_diff > 0:
                        c0 = 0.1
                    elif y_diff == 0:
                        c0  = 0
                    
                    p = [c0,0.1]

                elif equation == "c0*(x**c1)+c2":                    

                    if y_diff < 0:
                        c0 = -0.1
                    elif y_diff > 0:
                        c0 = 0.1
                    elif y_diff == 0:
                        c0  = 0
                    
                    c2 = y_data[0]
                    p = [c0,0.1,c2]

                
                elif equation == "(c0/(1+np.exp(c1*x)))":                    

                    if y_diff < 0:
                        c0 = -0.1
                    elif y_diff > 0:
                        c0 = 0.1
                    elif y_diff == 0:
                        c0  = 0
                                        
                    p = [c0,-0.1]


                elif equation == "(c0/(1+np.exp(c1*x)))+c2":                    

                    if y_diff < 0:
                        c0 = -0.1
                    elif y_diff > 0:
                        c0 = 0.1
                    elif y_diff == 0:
                        c0  = 0                    
                    
                    c2 = y_data[0]
                    p = [c0,-0.1,c2]

            
            # perform the curve fitting, return the optimized parameters (popt) and the covariance matrix (pcov)
            popt, pcov = curve_fit(fit_function, x_data, y_data, p0=p, bounds=bounds)
            
            # generate fitted y data
            fitted_y = fit_function(x_model, *popt)
            
            # append it to the fitted_data dataframe
            fitted_data = pd.concat([fitted_data, pd.DataFrame(fitted_y, index=pd.Series(x_model))], axis=1)
            
            # Calculate R-squared value
            residuals = y_data - fit_function(x_data, *popt)
            ss_res, ss_tot = np.sum(residuals**2), np.sum((y_data - np.mean(y_data))**2)        
            r_squared = np.round(1 - (ss_res / ss_tot), 3)

            # Create a string representation of the equation with optimized parameters
            optimized_equation = equation
            for i, param in enumerate(popt):
                optimized_equation = optimized_equation.replace(f'c{i}', str(np.round(param,2)))

            fitted_labels.append(f'{optimized_equation}, $R^2$ = {r_squared}')
            fitted_parameters.append(popt)

        fitted_data.columns = [f'{x.split(".")[-1]}, $y$ = {y}' for x,y in zip(self.get_meas_ids, fitted_labels)]         
        
        # Plot the data
        if plot:            

            labels_H = {
                'Hv': 'Exposure dose $H_v$ (Mlxh)',
                'He': 'Radiant Exposure $H_e$ (MJ/m²)',
                't' : 'Exposure duration (seconds)'
            }

            sns.set_theme(context='paper', font='serif', palette='colorblind')
            fig, ax = plt.subplots(1,1, figsize=(10,6))
            fs = 24

            
            pd.concat(selected_data, axis=1).plot(ax=ax, color='0.7', ls='-', lw=5, legend=False)
            fitted_data.plot(ax=ax, lw=2, ls='--')

            ax.set_xlabel(labels_H[dose_unit], fontsize=fs)
            ax.set_ylabel(labels_eq[coordinate],fontsize=fs)
            
            ax.set_xlim(0)    

            ax.xaxis.set_tick_params(labelsize=fs)
            ax.yaxis.set_tick_params(labelsize=fs)   

            plt.tight_layout()    
            
            
            # Whether to save the figure
            if save:

                filename = f'MFT_{coordinate}-fitted.png'

                if save:      
                    
                    if path_fig == 'cwd':
                        path_fig = f'{os.getcwd()}/{filename}' 

                    plt.savefig(path_fig, dpi=300, facecolor='white')

            plt.show()
        
        if return_data:
            return fitted_parameters, fitted_data, pcov, r_squared   
    
    
    def compute_JND(self, dose_unit:Optional[str] = 'Hv', JND_dE = 1.5, light_intensity=50, daily_exposure:Optional[int] = 10, yearly_exposure:Optional[int] = 365, fitting = True):
        """Compute the just noticeable difference (JND) corresponding to each input data file.

        Parameters
        ----------
        dose_unit : Optional[str], optional
            Unit of the light dose energy, by default 'Hv'
            Any of the following units can be entered: 'He', 'Hv', 't'. Where 'He' corresponds to radiant energy (MJ/m2), 'Hv' to exposure dose (Mlxh), and 't' to times (sec)

        JND_dE : float, optional
            The dE00 value corresponding to one JND, by default 1.5

        light_intensity : int, optional
            The illuminance or the irradiance value of the intended light source, by default 50

        daily_exposure : Optional[int], optional
            Amount of exposure hours per day, by default 10

        yearly_exposure : Optional[int], optional
            Amount of exposure days per year, by default 365

        fitting : bool, optional
            Whether to fit the microfading data necessary to compute the JND value, by default True

        Returns
        -------
        A list of numerical values as string (uncertainty string with a nominal and standard deviation value)
            It returns a list of numerical values corresponding to the amount of years necessary to reach one JND. 
        """

        H_step = 0.01
        dE_fitted = self.compute_fitting(dose_unit='Hv', x_range=(0,5.1,H_step), return_data=True, plot=False)[1]
        dE_rate = np.gradient(dE_fitted.T.values, H_step, axis=1)
        dE_rate_mean = [np.mean(x[-20:]) for x in dE_rate]
        dE_rate_std = [np.std(x[-20:]) for x in dE_rate]

        rates = [ufloat(x, y) for x,y in zip(dE_rate_mean, dE_rate_std)]

        times_years = []

        for rate in rates:

            if dose_unit == 'Hv':
                
                JND_dose = (JND_dE / rate) * 1e6                     # in lxh
                time_hours = JND_dose / light_intensity
                time_years = time_hours / (daily_exposure * yearly_exposure)            

            if dose_unit == 'He':
                JND_dose = (JND_dE / rate) * 1e6                     # in J/m²
                time_sec = JND_dose / light_intensity
                time_hours = time_sec / 3600
                time_years = time_hours / (daily_exposure * yearly_exposure)

            times_years.append(time_years)

        return times_years
    
    
    def compute_mean(self, return_data:Optional[bool] = True, criterion:Optional[str] = 'spot_group', dose_unit:Optional[str] = 'He', dose_values:Optional[tuple] = (0, 'chd', 0.1), rounding:Union[int,tuple,list] = (4,3), save:Optional[bool] = False, folder:Optional[str] = '.', filename:Optional[str] = 'default'):
        """Compute mean and standard deviation values of several microfading measurements.

        Parameters
        ----------        
        
        return_data : bool, optional
            Whether to return the data, by default True        

        criterion : str, optional
            _description_, by default 'group'            

        dose_unit : str, optional
            The ligth dose unit used to average the colorimetric and spectral data, by default 'He' 
            Any of the following units can be entered: 'He', 'Hv', 't'. Where 'He' corresponds to radiant energy (MJ/m2), 'Hv' to exposure dose (Mlxh), and 't' to times (sec)
        
        dose_values : tuple, optional
            Tuple of three values (start, end, step) defining the dose values for which the average values will be returned, by default (0, 'chd', 0.1)
            The logical start value is 0, but it does not have to be. Just make sure that it is smaller than the end values. 
            The end value can be one of the following options: 'chd', 'max', an integer or float of your choice smaller or equal to the common highest available dose (chd).
            
            When 'chd', it will compute the average values over the common light dose range.
            When 'max', it will compute the average values over the largest light dose range.
                                       
            For example, let's say that you have three measurements - one from 0 to 2 MJ/m2, one from 0 to 1.5 MJ/m2m and a last one from 0 to 3 MJ/m2 - for which you want to compute the mean and standard deviation values. When selecting 'chd', it will return values from 0 to 1.5 MJ/m2. When selecting 'max', it will return values from 0 to 3 MJ/m2 with standard deviation values of 0 between 2 and 3 MJ/m2.                      
        
        rounding : [int, tuple], optional
            Rounding the spectral and colorimetric coordinates, by default (4,3)
            It represents the number of digits after the comma.
            When an integer is provided, it is applied to both the spectral and colorimetric value.
            When a tuple is provided, the first value relates to the spectral values while the second relates to the colorimetric values.
            
        save : bool, optional
            Whether to save the average data as an excel file, by default False

        folder : str, optional
            Folder where the excel file will be saved, by default 'default'
            When 'default', the file will be saved in the same folder as the input files
            When '.', the file will be saved in the current working directory
            One can also enter a valid path as a string.

        filename : str, optional
            Filename of the excel file containing the average values, by default 'default'
            When 'default', it will use the filename of the first input file
            One can also enter a filename, but without a filename extension.

        Returns
        -------
        tuple, excel file
            It returns a tuple composed of three elements (info, CIELAB data, spectral data). When 'save' is set to True, an excel is created to stored the tuple inside three distinct excel sheet (info, CIELAB, spectra).

        Raises
        ------
        RuntimeError
            _description_
        """

        # Raise error if only one measurement is provided
        if len(self.files) < 2:        
            raise RuntimeError('Not enough files. At least two measurement files are required to compute the average values.')
        
        
        ###### DEFINE FUNCTIONS #######
        
        # Define averaging function
        def mean_std_with_nan(arrays):
            '''Compute the mean of several numpy arrays of different shapes.'''
            
            # Find the maximum shape
            max_shape = np.max([arr.shape for arr in arrays], axis=0)
                    
            # Create arrays with NaN values
            nan_arrays = [np.full(max_shape, np.nan) for _ in range(len(arrays))]
                    
            # Fill NaN arrays with actual values
            for i, arr in enumerate(arrays):
                nan_arrays[i][:arr.shape[0], :arr.shape[1]] = arr
                    
            # Calculate mean
            mean_array = np.nanmean(np.stack(nan_arrays), axis=0)

            # Calculate std
            std_array = np.nanstd(np.stack(nan_arrays), axis=0)
                    
            return mean_array, std_array
        
        # Define to function to convert value to float number
        def to_float(x):
            try:
                return float(x)
            except ValueError:
                return x


        ###### DEFINE THE DOSE VALUES #######

        if isinstance(dose_values[1], (int,float)):

            highest_dose = np.max([x for x in self.get_doses(dose_unit=dose_unit, max_doses=True)])
            if dose_values[1] > highest_dose:
                print(f'Process aborted. The end dose value you enter ({dose_values[1]}) is above the maximum light dose value available ({highest_dose} {dose_units[dose_unit]}).')
                return
            else:                
                wanted_dose_range = 'all'
                wanted_dose_values = np.arange(*dose_values)

        elif dose_values[1] == 'max':

            highest_dose = np.max([x for x in self.get_doses(dose_unit=dose_unit, max_doses=True)])
            wanted_dose_range = 'all'
            wanted_dose_values = np.arange(dose_values[0], highest_dose+dose_values[2], dose_values[2])
            

        elif dose_values[1] == 'chd':

            common_highest_dose = np.min([x for x in self.get_doses(dose_unit=dose_unit, max_doses=True)])
            wanted_dose_range = (dose_values[0], common_highest_dose, dose_values[2])
            wanted_dose_values = np.arange(*wanted_dose_range)

        else:
            print(f'Process aborted. The dose_values you entered ({dose_values}) is not valid. The first and third values of the tuple should be numbers (integer or float). The second value can either be "max", "chd" or a number. See the online documentation for more information.')
            return

        
        ###### AVERAGE SPECTRAL DATA #######

        # Retrieve the wavelength range
        wl = self.get_wavelength.iloc[:,0]
        wl.name = 'wavelength_nm'

        # Retrieve the spectral data
        data_sp = self.get_spectra(dose_unit=dose_unit, dose_values=wanted_dose_range,concat=False)
       
        # Compute the average values
        if dose_values[1] == 'chd':           

            wanted_sp_mean = np.mean(data_sp, axis=0)
            wanted_sp_std = np.std(data_sp, axis=0)
        
        else:     

            longest_dose_values = pd.concat(self.get_doses(dose_unit=dose_unit, max_doses=False), axis=1).dropna(axis=1).iloc[:,0].values
            sp = mean_std_with_nan(data_sp)
            sp_mean = pd.DataFrame(sp[0], index=wl, columns=longest_dose_values).T
            sp_std = pd.DataFrame(sp[1], index=wl, columns=longest_dose_values).T
            
            sp_mean_interpolation_functions = [sip.interp1d(sp_mean.index, sp_mean[col], kind='linear', fill_value='extrapolate') for col in sp_mean.columns]     
            sp_mean_interpolated_data = np.vstack([f(wanted_dose_values) for f in sp_mean_interpolation_functions])
            wanted_sp_mean = pd.DataFrame(sp_mean_interpolated_data, index=wl, columns=wanted_dose_values)

            sp_std_interpolation_functions = [sip.interp1d(sp_std.index, sp_std[col], kind='linear', fill_value='extrapolate') for col in sp_std.columns]     
            sp_std_interpolated_data = np.vstack([f(wanted_dose_values) for f in sp_std_interpolation_functions])
            wanted_sp_std = pd.DataFrame(sp_std_interpolated_data, index=wl, columns=wanted_dose_values)
           

    
        # Create a multi-index pandas DataFrame
        
        doses_tuples = [(dose, measurement) for dose in wanted_dose_values for measurement in ['mean', 'std']]
        multiindex_cols = pd.MultiIndex.from_tuples(doses_tuples, names=[dose_units[dose_unit], 'data_type'])
        
        data_df_sp = np.empty((len(wl), len(wanted_dose_values) * 2))       
        data_df_sp[:, 0::2] = wanted_sp_mean
        data_df_sp[:, 1::2] = wanted_sp_std
        df_sp_final = pd.DataFrame(data_df_sp,columns=multiindex_cols, index=wl)
        
        df_sp_final = round(df_sp_final, rounding[0])
                  
        

        ###### COLORIMETRIC DATA #######

        # Retrieve the spectral data
        data_cl = self.get_cielab(coordinates=['t_sec', 'Hv_Mlxh', 'L*', 'a*', 'b*', 'C*', 'h', 'dE76', 'dE00', 'dR_vis'], dose_unit=dose_unit, dose_values=wanted_dose_range,concat=False)
        
        
        # Compute the average values
        if dose_values[1] == 'chd':           

            wanted_cl_mean = np.mean(data_cl, axis=0)
            wanted_cl_std = np.std(data_cl, axis=0)
        
                
        # Create a multi-index pandas DataFrame
        
        cielab_tuples = [(x, measurement) for x in data_cl[0].columns.get_level_values('coordinate') for measurement in ['mean', 'std']]
        multiindex_cols = pd.MultiIndex.from_tuples(cielab_tuples, names=['coordinate', 'data_type'])
        
        data_df_cl = np.empty((wanted_cl_mean.shape[0], wanted_cl_mean.shape[1] * 2))       
        data_df_cl[:, 0::2] = wanted_cl_mean
        data_df_cl[:, 1::2] = wanted_cl_std
        df_cl_final = pd.DataFrame(data_df_cl,columns=multiindex_cols, index=data_cl[0].index)
                
        df_cl_final = round(df_cl_final, rounding[0])

        if dose_unit == 'He':
            df_cl_final.drop([('Hv_Mlxh','std'), ('t_sec','std')], axis=1, inplace=True)
            mapper = {('Hv_Mlxh', 'mean'): ('Hv_Mlxh', 'nominal'), ('t_sec', 'mean'): ('t_sec', 'nominal')}
            df_cl_final.columns = pd.MultiIndex.from_tuples([mapper.get(x, x) for x in df_cl_final.columns])

        elif dose_unit == 'Hv':
            df_cl_final.drop([('He_MJ/m2','std'), ('t_sec','std')], axis=1, inplace=True)
            mapper = {('He_MJ/m2', 'mean'): ('He_MJ/m2', 'nominal'), ('t_sec', 'mean'): ('t_sec', 'nominal')}
            df_cl_final.columns = pd.MultiIndex.from_tuples([mapper.get(x, x) for x in df_cl_final.columns])

        elif dose_unit == 't':
            df_cl_final.drop([('He_MJ/m2','std'), ('Hv_Mlxh','std')], axis=1, inplace=True)
            mapper = {('He_MJ/m2', 'mean'): ('He_MJ/m2', 'nominal'), ('Hv_Mlxh', 'mean'): ('Hv_Mlxh', 'nominal')}
            df_cl_final.columns = pd.MultiIndex.from_tuples([mapper.get(x, x) for x in df_cl_final.columns])

        df_cl_final.columns.names = ('coordinate', 'data_type')
        
    

        ###### INFO #######
        
        data_info = self.get_metadata().fillna('none')
        
        # Select the first column as a template
        df_info = data_info.iloc[:,0]
        

        # Measurement type
        df_info.loc['measurement_type'] = '[MEAN MICROFADING ANALYSES]'
        

        # Date time
        most_recent_dt = max(data_info.loc['datetime_analysis'])
        df_info.loc['datetime_analysis'] = most_recent_dt

        df_info.loc['datetime_processing'] = datetime.now()
        
        
        # Project data info
        df_info.loc['project_id'] = '_'.join(sorted(set(data_info.loc['project_id'].values)))
        df_info.loc['project_leader'] = '_'.join(sorted(set(data_info.loc['project_leader'].values)))
        df_info.loc['co-researchers'] = '_'.join(sorted(set(data_info.loc['co-researchers'].values)))
        df_info.loc['start_date'] = '_'.join(sorted(set(data_info.loc['start_date'].values)))
        df_info.loc['end_date'] = '_'.join(sorted(set(data_info.loc['end_date'].values)))
        df_info.loc['keywords'] = '_'.join(sorted(set(data_info.loc['keywords'].values)))
        df_info.loc['methods'] = '_'.join(sorted(set(data_info.loc['methods'].values)))

        # Object data info
        if len(set([x.split('_')[0] for x in data_info.loc['institution'].values])) > 1:
            df_info.loc['institution'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['institution'].values])))
        
        df_info.loc['object_id'] = '_'.join(sorted(set(data_info.loc['object_id'].values)))
        df_info.loc['object_category'] = '_'.join(sorted(set(data_info.loc['object_category'].values)))
        df_info.loc['object_type'] = '_'.join(sorted(set(data_info.loc['object_type'].values)))
        df_info.loc['object_technique'] = '_'.join(sorted(set(data_info.loc['object_technique'].values)))
        df_info.loc['object_title'] = '_'.join(sorted(set(data_info.loc['object_title'].values)))
        df_info.loc['object_name'] = '_'.join(sorted(set(data_info.loc['object_name'].values)))
        df_info.loc['object_creator'] = '_'.join(sorted(set(data_info.loc['object_creator'].values)))
        df_info.loc['object_date'] = '_'.join(sorted(set(data_info.loc['object_date'].values)))
        df_info.loc['object_material'] = '_'.join(sorted(set(data_info.loc['object_material'].values)))
        df_info.loc['object_comment'] = '_'.join(sorted(set(data_info.loc['object_comment'].values)))
        df_info.loc['color'] = '_'.join(sorted(set(data_info.loc['color'].values)))
        df_info.loc['support'] = '_'.join(sorted(set(data_info.loc['support'].values)))
        df_info.loc['colorants_name'] = '_'.join(sorted(set(data_info.loc['colorants_name'].values)))
        df_info.loc['binding'] = '_'.join(sorted(set(data_info.loc['binding'].values)))
        df_info.loc['ratio'] = '_'.join(sorted(set(data_info.loc['ratio'].values)))
        df_info.loc['thickness_um'] = '_'.join(sorted(set(data_info.loc['thickness_um'].values)))
        df_info.loc['status'] = '_'.join(sorted(set(data_info.loc['status'].values)))

        # Device data info
        if len(set(data_info.loc['device'].values)) > 1:
            df_info.loc['device'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['device'].values])))
        
        df_info.loc['measurement_mode'] = '_'.join(sorted(set(data_info.loc['measurement_mode'].values)))
        df_info.loc['zoom'] = '_'.join(sorted(set(data_info.loc['zoom'].values)))
        df_info.loc['iris'] =  '_'.join(set([str(x) if f'{x}'.isnumeric() else x for x in list(data_info.loc['iris'].values)]))
        df_info.loc['geometry'] = '_'.join(sorted(set(data_info.loc['geometry'].values)))
        df_info.loc['distance_ill_mm'] = '_'.join(set([str(x) if f'{x}'.isnumeric() else x for x in list(data_info.loc['distance_ill_mm'].values)]))
        df_info.loc['distance_coll_mm'] = '_'.join(set([str(x) if f'{x}'.isnumeric() else x for x in list(data_info.loc['distance_coll_mm'].values)]))
         

        if len(set(data_info.loc['fiber_fading'].values)) > 1:
            df_info.loc['fiber_fading'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['fiber_fading'].values])))

        if len(set(data_info.loc['fiber_ill'].values)) > 1:
            df_info.loc['fiber_ill'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['fiber_ill'].values])))

        if len(set(data_info.loc['fiber_coll'].values)) > 1:
            df_info.loc['fiber_coll'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['fiber_coll'].values])))

        if len(set(data_info.loc['lamp_fading'].values)) > 1:
            df_info.loc['lamp_fading'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['lamp_fading'].values])))

        if len(set(data_info.loc['lamp_ill'].values)) > 1:
            df_info.loc['lamp_ill'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['lamp_ill'].values])))

        if len(set(data_info.loc['filter_fading'].values)) > 1:
            df_info.loc['filter_fading'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['filter_fading'].values])))

        if len(set(data_info.loc['filter_ill'].values)) > 1:
            df_info.loc['filter_ill'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['filter_ill'].values])))

        if len(set(data_info.loc['white_standard'].values)) > 1:
            df_info.loc['white_standard'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['white_standard'].values])))
        

        # Analysis data info
        
        criterion_value = df_info.loc[criterion]
        object_id = df_info.loc['object_id']
        if criterion == 'spot_group':            
            df_info.loc['meas_id'] = f'MF.{object_id}.{criterion_value}'
        elif criterion == 'object' or criterion == 'project':
             df_info.loc['meas_id'] = f'MF.{criterion_value}'
        else:
            print('Choose one of the following options for the criterion parameter: ["group", "object", "project"]')

        meas_nbs = '-'.join([x.split('.')[-1] for x in self.get_meas_ids])
        df_info.loc['spot_group'] = f'{"-".join(sorted(set(data_info.loc["spot_group"].values)))}_{meas_nbs}'    
        df_info.loc['spot_description'] = '_'.join(sorted(set(data_info.loc['spot_description'].values)))
        df_info.loc['background'] = '_'.join(sorted(set(data_info.loc['background'].values)))  
        
        '''
        spot_images_infos = sorted(set(data_info.loc['spot_images'].values))
        spot_images_info = spot_images_infos[0]
        for el in spot_images_infos[1:]:
            print(el)
            spot_images_info = spot_images_info + el
        
        print(spot_images_info)
        df_info.loc['spot_images'] = spot_images_info
        '''

        if len(set(data_info.loc['specular_component'].values)) > 1:
            df_info.loc['specular_component'] = '_'.join(sorted(set([x.split('_')[0] for x in data_info.loc['specular_component'].values]))) 

        
        df_info.loc['integration_time_sample_ms'] = np.round(np.mean(data_info.loc['integration_time_sample_ms'].astype(float).values),1)
        df_info.loc['integration_time_whitestandard_ms'] = np.round(np.mean(data_info.loc['integration_time_whitestandard_ms'].astype(float).values),1)
        df_info.loc['average'] = np.round(np.mean(data_info.loc['average'].astype(float).values),1) 
        df_info.loc['duration_min'] = np.round(np.mean(data_info.loc['duration_min'].values),1)
        df_info.loc['interval_sec'] = np.round(np.mean(data_info.loc['interval_sec'].astype(float).values),1)
        df_info.loc['measurements_N'] = len(self.files)
        df_info.loc['illuminant'] = '_'.join(sorted(set(data_info.loc['illuminant'].values)))
        df_info.loc['observer'] = '_'.join(sorted(set(data_info.loc['observer'].values)))


        # Beam data info

        df_info.loc['beam_photo'] = '_'.join(sorted(set(data_info.loc['beam_photo'].values)))
        #df_info.loc['resolution_micron/pixel'] = '_'.join(set([str(x) if f'{x}'.isnumeric() else x for x in list(data_info.loc['resolution_micron/pixel'].values)]))
        df_info.loc['resolution_micron/pixel'] = '_'.join(set([str(x) for x in list(data_info.loc['resolution_micron/pixel'].values)]))

        fwhm = data_info.loc['FWHM_micron']
        fwhm_avg = np.mean([i for i in [to_float(x) for x in fwhm] if isinstance(i, (int, float))])
        df_info.loc['FWHM_micron'] = fwhm_avg

        power_infos = list(data_info.loc['radiantFlux_mW'].values)
        
        if len(set(power_infos)) == 1:
            df_info.loc['radiantFlux_mW'] = power_infos[0]

        else:
            df_info.loc['radiantFlux_mW'] = "_".join(power_infos)
        
        """
        power_values = []
        
        for power_info in power_infos:
            if "_" in str(power_info):
                power_value = ufloat_fromstr(power_info.split('_')[0])
                power_values.append(power_value)                            

            else: 
                power_values.append(power_info)               
                
        power_mean = np.round(np.mean(power_values),3)
        power_std = np.round(np.std(power_values),3)
        df_info.loc['radiantFlux_mW'] = f'{ufloat(power_mean,power_std)}'    
        """         

        irr_values = [str(ufloat(x,0)) if isinstance(x, int) else x for x in data_info.loc['irradiance_Ee_W/m^2'] ] 
        irr_mean = np.int32(np.mean([unumpy.nominal_values(ufloat_fromstr(x)) for x in irr_values]))
        irr_std = np.int32(np.std([unumpy.nominal_values(ufloat_fromstr(x)) for x in irr_values]))
        irr_avg = ufloat(irr_mean, irr_std)    
        df_info.loc['irradiance_Ee_W/m^2'] = irr_avg
       
        lm = [x for x in data_info.loc['luminuousFlux_lm'].values]
        lm_avg = np.round(np.mean(lm),3)
        df_info.loc['luminuousFlux_lm'] = lm_avg

        ill = [x for x in data_info.loc['illuminance_Ev_Mlx']]
        ill_avg = np.round(np.mean(ill),3)
        df_info.loc['illuminance_Ev_Mlx'] = ill_avg

        
        # Results data info
        df_info.loc['radiantExposure_He_MJ/m^2'] = df_cl_final.index.values[-1]
        df_info.loc['exposureDose_Hv_Mlxh'] = float(np.round(df_cl_final['Hv_Mlxh'].values[-1],4))
        

        # Rename the column
        df_info.name = 'value'
                
        
        ###### SAVE THE MEAN DATAFRAMES #######
        
        if save:  

            # set the folder
            if folder == ".":
                folder = Path('.')  

            elif folder == 'default':
                folder = Path(self.files[0]).parent

            else:
                if Path(folder).exists():
                    folder = Path(folder)         

            # set the filename
            if filename == 'default':
                project_id = df_info['project_id']
                new_meas_id = df_info['meas_id']
                object_name = df_info['object_name']
                spot_description = df_info['spot_description']                
                date = df_info['datetime_analysis'].date()
                device_id = df_info['device'].split('_')[0]

                filename = f'{project_id}_{new_meas_id}_{object_name}_avg_{spot_description}_{date}_{device_id}.xlsx'

            else:
                filename = f'{Path(self.files[0]).stem}_MEAN{Path(self.files[0]).suffix}'

            
            # create a excel writer object
            with pd.ExcelWriter(folder / filename) as writer:

                df_info.to_excel(writer, sheet_name='info', index=True)
                df_cl_final.to_excel(writer, sheet_name="CIELAB", index=True)
                df_sp_final.to_excel(writer, sheet_name='spectra', index=True)

            print(f'{folder / filename} successfully created.')
        

        ###### RETURN THE MEAN DATAFRAMES #######
            
        if return_data:
            return df_info, df_cl_final, df_sp_final
    
    
    def compute_sp_derivate(self):
        """Compute the first derivative values of reflectance spectra.

        Returns
        -------
        a list of pandas dataframes
            It returns the first derivative values of the reflectance spectra inside dataframes where each column corresponds to a single spectra.
        """

        sp = self.get_data(data='sp')                    

        sp_derivation = [pd.DataFrame(pd.concat([pd.DataFrame(np.gradient(x.iloc[:,:], axis=0), index=pd.Series(x.index), columns=x.columns)], axis=1),index=pd.Series(x.index), columns=x.columns) for x in sp]

        return sp_derivation
    
    
    def get_spectra(self, wl_range:Union[int, float, list, tuple] = 'all', dose_unit:Optional[str] = 'He', dose_values:Union[int, float, list, tuple] = 'all', spectral_mode:Optional[str] = 'R', derivation:Optional[bool] = False, smoothing:Optional[list] = [1,0], concat:Optional[bool] = True):
        """Retrieve the reflectance spectra related to the input files.

        Parameters
        ----------
        wl_range : Union[int, float, list, tuple], optional
            Select the wavelengths for which the spectral values should be given with a two-values tuple corresponding to the lowest and highest wavelength values, by default 'all'
            When 'all', it will returned all the available wavelengths contained in the datasets.
            A single wavelength value (an integer or a float number) can be entered.
            A list of specific wavelength values as integer or float can also be entered.
            A tuple of two or three values (min, max, step) will take the range values between these two first values. By default the step is equal to 1.

        dose_unit : string, optional
            Unit of the light energy dose, by default 'He'
            Any of the following units can be used: 'He', 'Hv', 't'. Where 'He' corresponds to radiant energy (MJ/m2), 'Hv' to exposure dose (Mlxh), and 't' to times (sec).

        dose_values : Union[int, float, list, tuple], optional
            Dose values for which the reflectance values will be returned, by default 'all'
            When 'all', it returns the reflectance values for all the dose values available in the given input data files.
            A single dose value (an integer or a float number) can be entered.
            A list of dose values, as integer or float, can also be entered.
            A tuple of three values (min, max, step) will be used in a numpy.arange() function to return an array of dose values. 

        spectral_mode : string, optional
            When 'R', it returns the reflectance spectra
            When 'A', it returns the absorption spectra using the following equation: A = -log(R)

        derivation : bool, optional
            Whether to return the first derivative values of the desired spectral values, by default False.
        
        smoothing : list of two integers, optional
            Whether to smooth the reflectance data using the Savitzky-Golay filter from the Scipy package, by default [1,0]
            The first integer corresponds to the window length and should be less than or equal to the size of a reflectance spectrum. The second integer corresponds to the polyorder parameter which is used to fit the samples. The polyorder value must be less than the value of the window length.

        concat : bool, optional
            Whether to concat the reflectance data column-wise
            When True, it returns a single pandas dataframe
            When False, it returns 
            
        Returns
        -------
        A list of pandas dataframes
            It returns a list of pandas dataframes where the columns correspond to the dose values and the rows correspond to the wavelengths.
        """

        data_sp = []
        files = self.read_files(sheets=['spectra', 'CIELAB'])   

        dose_units = {'He':'He_MJ/m2', 'Hv':'Hv_Mlxh', 't':'t_sec'}     

        for file, meas_id in zip(files, self.get_meas_ids):
            df_sp = file[0]            
            
            # whether to compute the absorption spectra
            if spectral_mode == 'A':
                df_sp = np.log(df_sp) * (-1)              

            # Set the light dose unit
            if dose_unit == 'Hv':
                Hv = file[1]['Hv_Mlxh','nominal'].values
                df_sp.columns = df_sp.columns.set_levels(Hv, level=0)                
                #df_sp.index.name = 'wl-nm_Hv-Mlxh'
            
            elif dose_unit =='t':
                t = file[1]['t_sec','nominal'].values
                df_sp.columns = df_sp.columns.set_levels(t, level=0)
                #df_sp.index.name = 'wl-nm_t-sec'                

            # Set the wavelengths
            if isinstance(wl_range, tuple):
                if len(wl_range) == 2:
                    wl_range = (wl_range[0],wl_range[1],1)
                
                wavelengths = np.arange(wl_range[0], wl_range[1], wl_range[2])                               

            elif isinstance(wl_range, list):
                wavelengths = wl_range                               

            elif isinstance(wl_range, int):
                wl_range = [wl_range]
                wavelengths = wl_range  

            else:
                wavelengths = df_sp.index          
                
            df_sp = df_sp.loc[wavelengths]

            
            # Smooth the data
            doses = df_sp.columns
            df_sp = pd.DataFrame(savgol_filter(df_sp.T.values, window_length=smoothing[0], polyorder=smoothing[1]).T, columns=doses, index=wavelengths)
            
            # Set the dose values 
            if isinstance(dose_values, tuple):
                if len(dose_values) == 2:
                    dose_values = (dose_values[0],dose_values[1],1)
                
                wanted_doses = np.arange(dose_values[0], dose_values[1], dose_values[2])
                
            elif isinstance(dose_values, int) or isinstance(dose_values, float):            
                wanted_doses = [dose_values]

            elif isinstance(dose_values, (list,np.ndarray)):
                wanted_doses = dose_values

            else:
                wanted_doses = sorted(set(df_sp.columns.get_level_values(0)))


            def multiindex_2Dinterpolation(df, meas_id, dose_unit, wanted_x, wanted_y, level_name='nominal'):
                interpolator = RegularGridInterpolator((df.index, df.columns.get_level_values(0)), df.values, method='linear')

                # Create a meshgrid of the new points
                new_wv_grid, new_ev_grid = np.meshgrid(wanted_y, wanted_x, indexing='ij')

                # Flatten the grid arrays and combine them into coordinate pairs
                new_points = np.array([new_wv_grid.ravel(), new_ev_grid.ravel()]).T

                # Interpolate the data at the new points
                interpolated_values = interpolator(new_points)

                # Reshape the interpolated values to match the new grid shape
                interpolated_values = interpolated_values.reshape(len(wanted_y), len(wanted_x))

                # Create a new DataFrame with the interpolated data
                new_columns = pd.MultiIndex.from_product([[meas_id] ,wanted_x, [level_name]], names=['meas_id',dose_units[dose_unit], 'data_type'])
                interpolated_df = pd.DataFrame(interpolated_values, index=wanted_y, columns=new_columns)

                interpolated_df.index.name = 'wavelength_nm'
                
                return interpolated_df
                
            
            if wanted_doses[-1] > doses[-1][0]:
                print(f'The maximum wanted light dose value exceed the common highest available dose value ({doses[-1][0]} {dose_units[dose_unit].split("_")[1]}). Please select light dose values within the available light dose range.')
                return
        
            if sorted(set(df_sp.columns.get_level_values(1))) == ['mean', 'std']:
                df_sp_n = df_sp.xs(key='mean', axis=1, level=1)
                df_sp_s = df_sp.xs(key='std', axis=1, level=1)
                
                interpolated_df_sp_n = multiindex_2Dinterpolation(df_sp_n, meas_id, dose_unit, wanted_doses, df_sp.index, 'mean')   #.T[::2].T
                interpolated_df_sp_s = multiindex_2Dinterpolation(df_sp_s, meas_id, dose_unit, wanted_doses, df_sp.index, 'std')    #.T[::2].T
                interpolated_df_sp = pd.concat([interpolated_df_sp_n,interpolated_df_sp_s], axis=1).sort_index(axis=1)                
                
                
            else:
                interpolated_df_sp = multiindex_2Dinterpolation(df_sp, meas_id, dose_unit, wanted_doses, df_sp.index)
                                    
            
            # append the spectral data
            data_sp.append(interpolated_df_sp) 

        if concat:
            data_sp = pd.concat(data_sp, axis=1)


        if derivation:
            data_sp = data_sp.loc[:, data_sp.columns.get_level_values('data_type') != 'std']
            data_sp = pd.DataFrame(np.gradient(data_sp, axis=0), index=data_sp.index, columns=data_sp.columns)
            
        return data_sp
    
    
    def get_cielab(self, coordinates:Optional[list] = ['dE00'], dose_unit:Optional[str] = 'He', dose_values:Union[int, float, list, tuple] = 'all', data_type:Union[str, list] = 'all', rounding:Optional[int] = 4, concat:Optional[bool] = True):
        """Retrieve the colourimetric values for one or multiple light dose values.

        Parameters
        ----------
        coordinates : Optional[list], optional
            Select the desired colorimetric coordinates from the following list: ['L*', 'a*','b*', 'C*', 'h', 'dL*', 'da*','db*', 'dC*', 'dh', 'dE76', 'dE00', 'dR_vis'], by default ['dE00']
            When 'all', it returns all the colorimetric coordinates.

        dose_unit : Optional[str], optional
            Unit of the light dose energy, by default ['He']
            Any of the following units can be added to the list: 'He', 'Hv', 't'. Where 'He' corresponds to radiant energy (MJ/m2), 'Hv' to exposure dose (Mlxh), and 't' to times (sec)

        dose_values : Union[int, float, list, tuple], optional
            Dose values for which the colourimetric values will be returned, by default 'all'
            When 'all', it returns the colourimetric values for all the dose values available in the given input data files.
            A single dose value (an integer or a float number) can be entered.
'            A list of dose values, as integer or float, can also be entered.
'            A tuple of three values (min, max, step) will be used in a numpy.arange() function to return an array of dose values. 

        data_type : Union[str, list], optional
            Select the type of data, by default 'all'
            One can enter one of the following options ('nominal', 'mean', 'std') as a string, or combined inside a list, e.g. ['nominal', 'std'] 

        rounding : Optional[int], optional
            Rounding of the colorimetric values, by default 4
            The value corresponds to the amount of digits after the decimal separator.
        
        concat : Optional[bool], optional
            Whether to concatenate the dataframes together, by default False
        

        Returns
        -------
        A pandas dataframe or a list of pandas dataframes
            It returns the values of the wanted colour coordinates inside dataframes where each coordinate corresponds to a column.
        """              

        # Retrieve the range light dose values
        if isinstance(dose_values, (float, int)):
            dose_values = [dose_values]

        elif isinstance(dose_values, tuple):
            dose_values = np.arange(dose_values[0], dose_values[1], dose_values[2])

        elif isinstance(dose_values, (list, np.ndarray)):
            dose_values = dose_values        
        
        
        # Read the files containing the data        
        cielab_data = self.read_files(sheets='CIELAB')
        cielab_data = [x[0] for x in cielab_data]

        # Create an empty list with all the colorimetric data
        all_data = []
              
        # Compute the delta LabCh values and add the data into the list all_data  
        for data in cielab_data:
            
            # for data with std values
            if sorted(set(data.columns.get_level_values(1))) == ['mean', 'std']:
                data_dLabCh = delta_coord = [unumpy.uarray(d[coord, 'mean'], d[coord, 'std']) - unumpy.uarray(d[coord, 'mean'], d[coord, 'std'])[0] for coord in ['L*', 'a*', 'b*', 'C*', 'h'] for d in [data]]

                delta_means = [unumpy.nominal_values(x) for x in delta_coord]
                delta_stds = [unumpy.std_devs(x) for x in delta_coord]

                delta_coord_mean = [(f'd{coord}', 'mean') for coord in ['L*', 'a*', 'b*', 'C*', 'h']]
                delta_coord_std = [(f'd{coord}', 'std') for coord in ['L*', 'a*', 'b*', 'C*', 'h']]

                for coord_mean,delta_mean,coord_std,delta_std in zip(delta_coord_mean,delta_means, delta_coord_std,delta_stds):                    
                    data[coord_mean] = delta_mean
                    data[coord_std] = delta_std

                    all_data.append(data)          
                
            # for data without std values
            else:
                
                data_LabCh = data[['L*','a*','b*','C*','h']]
                data_dLabCh = data_LabCh - data_LabCh.iloc[0,:]
                data_dLabCh = data_dLabCh.rename(columns={'L*': 'dL*', 'a*': 'da*' ,'b*': 'db*','C*': 'dC*','h': 'dh'}, level=0)
                data_cielab = pd.concat([data,data_dLabCh], axis=1)
                data_cielab.index.name = dose_units[dose_unit]

                all_data.append(data_cielab)

        
        # Select the wanted dose_unit and coordinate
        if coordinates == 'all':
            wanted_data = all_data
            wanted_data = [x.set_index((dose_units[dose_unit], 'nominal')) for x in wanted_data]
        else:       
            wanted_data = [x[[dose_units[dose_unit]] + coordinates] for x in all_data]       
            wanted_data = [x.set_index(x.columns[0]) for x in wanted_data]     

              
        if isinstance(dose_values, str):
            if dose_values == 'all':
                interpolated_data = [x.reset_index() for x in wanted_data]
                   
        else:

            # Interpolation function, assuming linear interpolation
            interp_functions = lambda x, y: interp1d(x, y, kind='linear', bounds_error=False)

            
            # Double comprehension list to interpolate each dataframe in wanted_data
            interpolated_data = [
                pd.DataFrame({
                    col: interp_functions(df.index, df[col])(dose_values)
                    for col in df.columns
                }, index=dose_values)
                .rename_axis(dose_units[dose_unit])
                .reset_index()
                for df in wanted_data
            ]

        
        wanted_dataframes = []

        for dataframe, meas_id in zip(interpolated_data, self.get_meas_ids):

            dataframe = dataframe.set_index([dataframe.columns[0]])
            dataframe.columns.names = ('coordinate', 'data_type')

            if dose_unit == 'He':
                dataframe.index = np.round(dataframe.index,1) 
                       
            
            multiindex_cols = pd.MultiIndex.from_tuples([(meas_id, col[0], col[1]) for col in dataframe.columns], names=['meas_id','coordinate', 'data_type'])
            dataframe.columns = multiindex_cols
            dataframe.index.name = dose_units[dose_unit]

            # Whether to round the values
            if isinstance(rounding, int):
                dataframe = np.round(dataframe, rounding)

            # Append the dataframe values inside a list
            wanted_dataframes.append(dataframe)
        
        
        # Concatenate the dataframes along the columns
        wanted_dataframe_concat = pd.concat(wanted_dataframes, axis=1)
        wanted_dataframe_concat.index.name = dose_units[dose_unit]

        # Select the data types
        if data_type == 'all' and concat == False:
            wanted_output = wanted_dataframes

        elif data_type == 'all' and concat == True:
            wanted_output = wanted_dataframe_concat
        
        elif data_type in ['nominal', 'mean', 'std']:
            wanted_output = wanted_dataframe_concat.loc[:, (slice(None), slice(None), [data_type])]

        elif isinstance(data_type, list):
            wanted_output = wanted_dataframe_concat.loc[:, (slice(None), slice(None), data_type)]

        else:
            print(f'Process aborted. The data_type value you entered {data_type} is not valid.')
            return
                        
        # Sort the data
        if concat:
            wanted_output = wanted_output.sort_index()
        
        # Return the values
        return wanted_output    
    
      
    def get_illuminant(self, illuminant:Optional[str] = 'D65', observer:Optional[str] = '10'):
        """Retrieve data over the illuminant.

        Parameters
        ----------
        illuminant : Optional[str], optional
            Select the illuminant, by default 'D65'
            It can be any value within the following list: ['A', 'B', 'C', 'D50', 'D55', 'D60', 'D65', 'D75', 'E', 'FL1', 'FL2', 'FL3', 'FL4', 'FL5', 'FL6', 'FL7', 'FL8', 'FL9', 'FL10', 'FL11', 'FL12', 'FL3.1', 'FL3.2', 'FL3.3', 'FL3.4', 'FL3.5', 'FL3.6', 'FL3.7', 'FL3.8', 'FL3.9', 'FL3.10', 'FL3.11', 'FL3.12', 'FL3.13', 'FL3.14', 'FL3.15', 'HP1', 'HP2', 'HP3', 'HP4', 'HP5', 'LED-B1', 'LED-B2', 'LED-B3', 'LED-B4', 'LED-B5', 'LED-BH1', 'LED-RGB1', 'LED-V1', 'LED-V2', 'ID65', 'ID50', 'ISO 7589 Photographic Daylight', 'ISO 7589 Sensitometric Daylight', 'ISO 7589 Studio Tungsten', 'ISO 7589 Sensitometric Studio Tungsten', 'ISO 7589 Photoflood', 'ISO 7589 Sensitometric Photoflood', 'ISO 7589 Sensitometric Printer']

        observer : Optional[str], optional
            Standard observer in degree, by default '10'
            It can be either '2' or '10'

        Returns
        -------
        tuple
            It returns a tuple with two set of values: the chromaticity coordinates (x,y) of the illuminant (CCS) and the spectral distribution of the illuminant (SDS) from 300 to 780 nm.
        """

        observers = {
            '10': "cie_10_1964",
            '2' : "cie_2_1931"
        }
       
        CCS = colour.CCS_ILLUMINANTS[observers[observer]][illuminant]
        SDS = colour.SDS_ILLUMINANTS[illuminant]

        return CCS, SDS

     
    def get_observer(self, observer:Optional[str] = '10'):
        """Retrieve data over the observer.

        Parameters
        ----------
        observer : Optional[str], optional
            Standard observer in degree, by default '10'
            It can be either '2' or '10'

        Returns
        -------        
            Returns the x_bar,  y_bar, z_bar spectra between 360 and 830 nm.
        """

        observers = {
            '10': "CIE 1964 10 Degree Standard Observer",
            '2' : "CIE 1931 2 Degree Standard Observer"
        }

        return colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER[observers[observer]]   
     

    def get_data(self, data:Union[str, list] = 'all', xarray:Optional[bool] = False):
        """A generic way to retrieve the microfading data. For more precise data retrieving, the function get_cielab() or get_spectra() will be more adequate.

        Parameters
        ----------
        data : str|list, optional
            Possibility to select the type of data, by default 'all'.
            When 'all', it returns all the data (spectral and colorimetric).
            When 'sp', it only returns the spectral data.
            When 'cl', it only returns the colorimetric data.  
            When 'Lab', it returns the CIE L*a*b* values.
            A list of strings can be entered to select specific colourimetric data among the following: ['dE76,'dE00','dR_vis', 'L*', 'a*', 'b*', 'C*', 'h'].

        xarray : bool, optional
            When True, the data are returned as an xarray.Dataset object, else as pandas dataframe object, by default False.

        Returns
        -------
        It returns a list of pandas dataframes or xarray.Dataset objects
        """

        all_files = self.read_files(sheets=['spectra','CIELAB'])
        all_data = []
        data_sp = [] 
        data_cl = [] 

        for data_file in all_files:

            df_sp = data_file[0]
            df_cl = data_file[1]

            if sorted(set(df_sp.columns.get_level_values(1))) == ['mean', 'std']:
                sp_n = df_sp.xs('mean', level=1, axis=1).values
                sp_s = df_sp.xs('std', level=1, axis=1).values

                L_n = df_cl["L*","mean"].values
                a_n = df_cl["a*","mean"].values
                b_n = df_cl["b*","mean"].values
                C_n = df_cl["C*","mean"].values
                h_n = df_cl["h","mean"].values
                dE76_n = df_cl["dE76","mean"].values
                dE00_n = df_cl["dE00","mean"].values
                dR_vis_n = df_cl["dR_vis","mean"].values

                L_s = df_cl["L*","std"].values
                a_s = df_cl["a*","std"].values
                b_s = df_cl["b*","std"].values
                C_s = df_cl["C*","std"].values
                h_s = df_cl["h","std"].values
                dE76_s = df_cl["dE76","std"].values
                dE00_s = df_cl["dE00","std"].values
                dR_vis_s = df_cl["dR_vis","std"].values
                
            else:
                sp_n = df_sp.xs('nominal', level=1, axis=1).values
                sp_s = df_sp.xs('nominal', level=1, axis=1)
                sp_s.loc[:,:] = 0
                sp_s = sp_s.values

                L_n = df_cl["L*","nominal"].values
                a_n = df_cl["a*","nominal"].values
                b_n = df_cl["b*","nominal"].values
                C_n = df_cl["C*","nominal"].values
                h_n = df_cl["h","nominal"].values
                dE76_n = df_cl["dE76","nominal"].values
                dE00_n = df_cl["dE00","nominal"].values
                dR_vis_n = df_cl["dR_vis","nominal"].values

                L_s = np.zeros(len(L_n))
                a_s = np.zeros(len(a_n))
                b_s = np.zeros(len(b_n))
                C_s = np.zeros(len(C_n))
                h_s = np.zeros(len(h_n))
                dE76_s = np.zeros(len(dE76_n))
                dE00_s = np.zeros(len(dE00_n))
                dR_vis_s = np.zeros(len(dR_vis_n))
            
            wl = data_file[0].iloc[:,0].values
            He = data_file[1]['He_MJ/m2','nominal'].values
            Hv = data_file[1]['Hv_Mlxh','nominal'].values
            t = data_file[1]['t_sec','nominal'].values
            
            spectral_data = xr.Dataset(
                {
                    'sp': (['wavelength','dose'], sp_n),
                    'sp_s': (['wavelength','dose'], sp_s)                
                },
                coords={
                    'wavelength': wl,   
                    'dose': He,
                    'He': ('dose', He),
                    'Hv': ('dose', Hv),  # Match radiant energy
                    't': ('dose', t)  # Match radiant energy
                }
            )

            color_data = xr.Dataset(
                {
                    'L*': (['dose'], L_n),
                    'a*': (['dose'], a_n),
                    'b*': (['dose'], b_n),
                    'C*': (['dose'], C_n),
                    'h': (['dose'], h_n),
                    'dE76': (['dose'], dE76_n),
                    'dE00': (['dose'], dE00_n),
                    'dR_vis': (['dose'], dR_vis_n),
                    'L*_s': (['dose'], L_s),
                    'a*_s': (['dose'], a_s),
                    'b*_s': (['dose'], b_s),
                    'C*_s': (['dose'], C_s),
                    'h_s': (['dose'], h_s),
                    'dE76_s': (['dose'], dE76_s),
                    'dE00_s': (['dose'], dE00_s),
                    'dR_vis_s': (['dose'], dR_vis_s),
                },
                coords={                    
                    'He': ('dose',He),
                    'Hv': ('dose',Hv),
                    't': ('dose',t),
                }
            )                
                    
            sp = spectral_data.set_xindex(["He","Hv","t"])
            cl = color_data.set_xindex(["He","Hv","t"])
            combined_data = xr.merge([sp, cl])

        all_data.append(combined_data)            
        
        
        if data == 'all':
            if xarray == False:                
                [data_sp.append(x[0]) for x in all_files]
                [data_cl.append(x[1]) for x in all_files]
                return data_sp, data_cl
            
            else:
                return all_data

        elif data == 'sp':
            if xarray == False:                
                [data_sp.append(x[0]) for x in all_files]                                           
            else:                
                data_sp = [x.sp for x in all_data]
                

            return data_sp
        
        elif data == 'cl':
            if xarray == False:
                [data_cl.append(x[1]) for x in all_files]
            else:
                data_cl = [x[['L*','a*','b*','C*','h','dE76','dE00','dR_vis']] for x in all_data]
            
            return data_cl
        
        elif data == 'Lab':
            if xarray == False:
                [data_cl.append(x[1][['L*','a*','b*']]) for x in all_files]
            else:
                data_cl = [x[['L*','a*','b*']] for x in all_data]

            return data_cl
        
        elif isinstance(data,list):
            if xarray == False:
                dic_doses = {'He': 'He_MJ/m2', 'Hv':'Hv_Mlxh', 't':'t_sec'}
                data = [dic_doses[x] if x in dic_doses.keys() else x for x in data]
                [data_cl.append(x[1][data]) for x in all_files]

            else:
                data = [elem for elem in data if elem not in ['Hv','He','t']]
                data_cl = [x[data] for x in all_data]
            
            return data_cl
        
        else:
            print("Enter a valid data parameter. It can either be a string ('sp', 'cl', 'Lab', 'all') or a list of strings ['dE00','dE76', 'L*', 'a*', 'b*', 'C*', 'h']")
            return None

    
    def get_metadata(self, labels:Union[list,str] = 'all', section:Optional[str] = 'all'):
        """Retrieve the metadata.

        Parameters
        ----------
        labels : Union[list,str], optional
            A string or a list of strings corresponding to the wanted metadata labels, by default 'all'
            The metadata labels can be found in the 'info' sheet of microfading excel files.
            When 'all', it returns all the metadata

        section : Optional[str], optional
            Retrieve metadata from one of the following sections: 'project', 'object', 'device', 'analysis', 'spot', 'beam', 'results'.
            For example, if you want to retrieve all the information about the objects, you can enter 'object' as a value.

        Returns
        -------
        pandas dataframe
            It returns the metadata inside a pandas dataframe where each column corresponds to a single file.
        """
        
        df = self.read_files()
        metadata = [x[0] for x in df]

        sections = ['project', 'object', 'device', 'analysis', 'spot', 'beam', 'results']
        df_metadata = pd.DataFrame(index = metadata[0].set_index('parameter').index)

        for m in metadata:
            m = m.set_index('parameter')
            Id = m.loc['meas_id']['value']
            
            df_metadata[Id] = m['value']

        
        if section in sections:

            if section == 'results':                
                df_metadata = df_metadata.loc[f'[RESULTS INFO]':]

            else:
                end_label = f'[{sections[sections.index(section) + 1].upper()} INFO]'
                df_metadata = df_metadata.loc[f'[{section.upper()} INFO]':end_label].iloc[:-1,:]

            return df_metadata
        
        elif labels != 'all' and isinstance(labels, (str,list)):
            return df_metadata.loc[labels] 
                
        else: 
            return df_metadata        
               
            
    def get_doses(self, dose_unit:Union[str,list] = 'all', max_doses:Optional[bool] = False, concat=True):
        """Retrieve the light energy doses related to each microfading measurement.

        Parameters
        ----------
        dose_unit : Union[str,list], optional
            Unit of the light dose energy, by default 'all'
            Any of the following units can be added to the list: 'He', 'Hv', 't'. Where 'He' corresponds to radiant energy (MJ/m2), 'Hv' to exposure dose (Mlxh), and 't' to times (sec). When a single unit is requested, it can be given as a string value ('He', 'Hv', or 't'). Otherwise, enter the dose unit values inside a list.

        max_doses : bool, optional
            Whether to return the maximum light dose values, by default False.

        concat : Optional[bool], optional
            Whether to concatenate the dose into a single dataframe, by default True
            When False, it returns a list of dataframes

        Returns
        -------
        a pandas dataframe or a list of pandas dataframes        
        """
        
        # retrieve the CIELAB datasheets
        data = self.read_files(sheets='CIELAB')

        # select the wanted dose units
        if dose_unit in ['He', 'Hv', 't']:
            wanted_doses = [dose_units[dose_unit]]

        elif dose_unit == 'all':
            wanted_doses = ['He_MJ/m2', 'Hv_Mlxh', 't_sec']

        elif isinstance(dose_unit, list):
            wanted_doses = [dose_units[x] for x in dose_unit]

        else:
            print(f'The dose_unit value you entered ("{dose_unit}") is not valid. Please consult the docstrings and documentation to enter valid values.')
            return

        # select the doses columns from the CIELAB datasheets
        all_doses = [x[0][wanted_doses] for x in data]

        # add a header for the measurement ids
        meas_ids = self.get_meas_ids
        df_doses = []
        
        for meas_id, df_dose in zip(meas_ids, all_doses):
            
            multiindex_cols = pd.MultiIndex.from_tuples([(meas_id, col[0], col[1]) for col in df_dose.columns], names=['meas_id','dose', 'data_type'])
            df_dose.columns = multiindex_cols
            df_doses.append(df_dose)

        # whether to retrieve the max dose values
        if max_doses:
            
            max_doses_values = [x.iloc[-1,:].values for x in df_doses]
            
            df_doses = []
            for meas_id, max_doses_value in zip(meas_ids,max_doses_values):

                multiindex_cols = pd.MultiIndex.from_tuples([(meas_id, col[1], col[2]) for col in df_dose.columns], names=['meas_id','dose', 'data_type'])
                df = pd.DataFrame(max_doses_value).T
                df.columns = multiindex_cols
                
                df_doses.append(df)
            
        # whether to concatenate the dataframes into a single dataframe
        if concat:
            df_doses = pd.concat(df_doses, axis=1)
        
        return df_doses
        
     
    @property
    def get_meas_ids(self):
        """Return the measurement id numbers corresponding to the input files.
        """
        info = self.get_metadata()        
        return info.loc['meas_id'].values


    @property
    def get_objects(self):
        """Return the object id numbers corresponding to the input files.
        """

        metadata_parameters = self.get_metadata().index

        if 'object_id' in metadata_parameters:

            df_info = self.get_metadata(labels=['object_id'])
            objects = sorted(set(df_info.values[0]))

            return objects
                   
        else:
            print(f'The info tab of the microfading interim file(s) {self.files} does not contain an object_id parameter.')
            return None
  

    def get_sRGB(self, illuminant='default', observer='default', dose_unit: Optional[str] = 'He', dose_values:Union[int, float, list, tuple] = 'all', clip:Optional[bool] = True):
        """Compute the sRGB values. 

        Parameters
        ----------
        illuminant : (str, optional)  
            Reference *illuminant* ('D65', or 'D50'). by default 'default'.
            When 'default', it fetches the illuminant value recorded in the db_config.json file of the package. If no value has been recorded, then it sets the illuminant value to 'D65'.
 
        observer : (str|int, optional)
            Reference *observer* in degree ('10' or '2'). by default 'default'.
            When 'default', it fetches the observer value recorded in the db_config.json file of the package. If no value has been recorded, then it sets the observer value to '10'.

        dose_unit : Optional[str], optional
            Unit of the light dose energy, by default ['He']
            Any of the following units can be entered: 'He', 'Hv', 't'. Where 'He' corresponds to radiant energy (MJ/m2), 'Hv' to exposure dose (Mlxh), and 't' to times (sec)

        dose_values : Union[int, float, list, tuple], optional
            Dose values for which the colourimetric values will be returned, by default 'all'
            When 'all', it returns the colourimetric values for all the dose values available in the given input data files.
            A single dose value (an integer or a float number) can be entered.
            A list of dose values, as integer or float, can also be entered.
            A tuple of three values (min, max, step) will be used in a numpy.arange() function to return an array of dose values. 

        clip : Optional[bool], optional
            Whether to constraint the srgb values between 0 and 1.

        Returns
        -------
        pandas dataframe
            It returns the sRGB values inside a dataframe where each column corresponds to a single file.
        """        
        
        # Set the observer value
        if observer == 'default':
            if isinstance(config.get_colorimetry_info(message=False), pd.DataFrame):
                observer = config.get_colorimetry_info().loc['observer']['value']
            elif config.get_colorimetry_info(message=False) == None:
                observer = '10deg'
            else:
                observer = '10deg'

        else:
            observer = f'{str(observer)}deg'

        # Set the illuminant value
        if illuminant == 'default':
            if isinstance(config.get_colorimetry_info(message=False), pd.DataFrame):
                illuminant = config.get_colorimetry_info().loc['illuminant']['value']
            elif config.get_colorimetry_info() == None:
                illuminant = 'D65'
            else:
                illuminant = 'D65'
        
        # Get colorimetric data related to the standard observer
        observers = {
            '10deg': 'cie_10_1964',
            '2deg' : 'cie_2_1931',
        }
        cmfs_observers = {
            '10deg': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1964 10 Degree Standard Observer"],
            '2deg': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1931 2 Degree Standard Observer"] 
            }
        
        ccs_ill = colour.CCS_ILLUMINANTS[observers[observer]][illuminant]

        
                
        '''
        df_sp_nominal = [
            df.loc[:, pd.IndexSlice[:, 'mean']] if 'mean' in df.columns.get_level_values(2)
            else df.loc[:, pd.IndexSlice[:, 'nominal']]
            for df in df_sp
        ]
        
        if 'mean' in df_sp.columns.get_level_values(2):
            df_sp_nominal = df_sp.xs(key='mean', axis=1, level=2)
        else:
            df_sp_nominal = df_sp
        '''  

        # Retrieve the spectral data
        df_sp = self.get_spectra(dose_unit=dose_unit, dose_values=dose_values)  

        # Remove the std columns from the spectral data if any
        df_sp = df_sp.loc[:, df_sp.columns.get_level_values('data_type') != 'std']        

        # Retrieve the wavelengths
        wl = df_sp.index

        # Compute the XYZ values
        XYZ = [colour.sd_to_XYZ(colour.SpectralDistribution(x,wl), cmfs_observers[observer], illuminant=colour.SDS_ILLUMINANTS[illuminant]) for x in df_sp.T.values]
                
        # Compute the sRGB values and clip them between 0 and 1 if needed
        if clip:
            srgb = np.round([colour.XYZ_to_sRGB(x / 100, illuminant=ccs_ill) for x in XYZ],4).clip(0,1)

        else:
            srgb = np.round([colour.XYZ_to_sRGB(x / 100, illuminant=ccs_ill) for x in XYZ],4)

        # Compile the sRGB values inside a pandas dataframe and return it
        df_srgb = pd.DataFrame(srgb, columns=['R','G','B'], index=df_sp.columns).T

        return df_srgb
         
    
    @property
    def get_wavelength(self):
        """Return the wavelength range of the microfading measurements.
        """
        data = self.get_data(data='sp')

        wavelengths = pd.concat([pd.Series(x.index.values) for x in data], axis=1)
        wavelengths.columns = self.get_meas_ids

        return wavelengths


    def get_XYZ(self, illuminant:Optional[str] = 'default', observer:Union[str,int] = 'default', dose_unit: Optional[str] = 'He', dose_values:Union[int, float, list, tuple] = 'all', rounding:Optional[int] = 2):
        """Compute the XYZ values. 

        Parameters
        ----------
        illuminant : (str, optional)  
            Reference *illuminant* ('D65', or 'D50'). by default 'default'.
            When 'default', it fetches the illuminant value recorded in the db_config.json file of the package. If no value has been recorded, then it sets the illuminant value to 'D65'.
 
        observer : (str|int, optional)
            Reference *observer* in degree ('10' or '2'). by default 'default'.
            When 'default', it fetches the observer value recorded in the db_config.json file of the package. If no value has been recorded, then it sets the observer value to '10'.

        dose_unit : Optional[str], optional
            Unit of the light dose energy, by default ['He']
            Any of the following units can be entered: 'He', 'Hv', 't'. Where 'He' corresponds to radiant energy (MJ/m2), 'Hv' to exposure dose (Mlxh), and 't' to times (sec)

        dose_values : Union[int, float, list, tuple], optional
            Dose values for which the colourimetric values will be returned, by default 'all'
            When 'all', it returns the colourimetric values for all the dose values available in the given input data files.
            A single dose value (an integer or a float number) can be entered.
            A list of dose values, as integer or float, can also be entered.
            A tuple of three values (min, max, step) will be used in a numpy.arange() function to return an array of dose values. 

        rounding : Optional[int], optional
            Rounding of the colorimetric values, by default 2
            The value corresponds to the amount of digits after the decimal separator.

        Returns
        -------
        pandas dataframe
            It returns the XYZ values inside a dataframe where each column corresponds to a single file.
        """

        # Set the observer value
        if observer == 'default':
            if isinstance(config.get_colorimetry_info(message=False), pd.DataFrame):
                observer = config.get_colorimetry_info().loc['observer']['value']
            elif config.get_colorimetry_info(message=False) == None:
                observer = '10deg'
            else:
                observer = '10deg'

        else:
            observer = f'{str(observer)}deg'

        # Set the illuminant value
        if illuminant == 'default':
            if isinstance(config.get_colorimetry_info(message=False), pd.DataFrame):
                illuminant = config.get_colorimetry_info().loc['illuminant']['value']
            elif config.get_colorimetry_info() == None:
                illuminant = 'D65'
            else:
                illuminant = 'D65'             
                
        # Get colorimetric data related to the standard observer
        cmfs_observers = {
            '10deg': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1964 10 Degree Standard Observer"],
            '2deg': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1931 2 Degree Standard Observer"] 
            } 
        
        # Retrieve the spectral data
        df_sp = self.get_spectra(dose_unit=dose_unit, dose_values=dose_values)  

        # Remove the std columns from the spectral data if any
        df_sp = df_sp.loc[:, df_sp.columns.get_level_values('data_type') != 'std'] 

        # Retrieve the wavelengths
        wl = df_sp.index

        # Compute the XYZ values
        XYZ = [colour.sd_to_XYZ(colour.SpectralDistribution(x,wl), cmfs_observers[observer], illuminant=colour.SDS_ILLUMINANTS[illuminant]) for x in df_sp.T.values]

        # Compile the XYZ values inside a pandas dataframe    
        df_XYZ = pd.DataFrame(XYZ, columns=['X','Y','Z'], index=df_sp.columns).T

        # Round the XYZ values
        if isinstance(rounding, int):
            df_XYZ = np.round(df_XYZ, rounding)

        # Return the pandas dataframe with the XYZ values
        return df_XYZ   
        

    def get_xy(self, illuminant:Optional[str] = 'default', observer:Union[str, int] = 'default', dose_unit: Optional[str] = 'He', dose_values:Union[int, float, list, tuple] = 'all', rounding:Optional[int] = 4):
        """Compute the xy values. 

        Parameters
        ----------
        illuminant : (str, optional)  
            Reference *illuminant* ('D65', or 'D50'). by default 'default'.
            When 'default', it fetches the illuminant value recorded in the db_config.json file of the package. If no value has been recorded, then it sets the illuminant value to 'D65'.
 
        observer : (str|int, optional)
            Reference *observer* in degree ('10' or '2'). by default 'default'.
            When 'default', it fetches the observer value recorded in the db_config.json file of the package. If no value has been recorded, then it sets the observer value to '10'.

        dose_unit : Optional[str], optional
            Unit of the light dose energy, by default ['He']
            Any of the following units can be entered: 'He', 'Hv', 't'. Where 'He' corresponds to radiant energy (MJ/m2), 'Hv' to exposure dose (Mlxh), and 't' to times (sec)

        dose_values : Union[int, float, list, tuple], optional
            Dose values for which the colourimetric values will be returned, by default 'all'
            When 'all', it returns the colourimetric values for all the dose values available in the given input data files.
            A single dose value (an integer or a float number) can be entered.
            A list of dose values, as integer or float, can also be entered.
            A tuple of three values (min, max, step) will be used in a numpy.arange() function to return an array of dose values. 

        rounding : Optional[int], optional
            Rounding of the colorimetric values, by default 4
            The value corresponds to the amount of digits after the decimal separator.

        Returns
        -------
        pandas dataframe
            It returns the xy values inside a dataframe where each column corresponds to a single file.
        """
        

        # Set the observer value
        if observer == 'default':
            if isinstance(config.get_colorimetry_info(message=False), pd.DataFrame):
                observer = config.get_colorimetry_info().loc['observer']['value']
            elif config.get_colorimetry_info(message=False) == None:
                observer = '10deg'
            else:
                observer = '10deg'

        else:
            observer = f'{str(observer)}deg'

        # Set the illuminant value
        if illuminant == 'default':
            if isinstance(config.get_colorimetry_info(message=False), pd.DataFrame):
                illuminant = config.get_colorimetry_info().loc['illuminant']['value']
            elif config.get_colorimetry_info() == None:
                illuminant = 'D65'
            else:
                illuminant = 'D65'             
                
        # Get colorimetric data related to the standard observer
        cmfs_observers = {
            '10deg': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1964 10 Degree Standard Observer"],
            '2deg': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1931 2 Degree Standard Observer"] 
            }       
        
        # Retrieve the spectral data
        df_sp = self.get_spectra(dose_unit=dose_unit, dose_values=dose_values)  

        # Remove the std columns from the spectral data if any
        df_sp = df_sp.loc[:, df_sp.columns.get_level_values('data_type') != 'std'] 

        # Retrieve the wavelengths
        wl = df_sp.index

        # Compute the xy values
        xy = [colour.XYZ_to_xy(colour.sd_to_XYZ(colour.SpectralDistribution(x,wl), cmfs_observers[observer], illuminant=colour.SDS_ILLUMINANTS[illuminant])) for x in df_sp.T.values]

        # Compile the xy values inside a pandas dataframe      
        df_xy = pd.DataFrame(xy, columns=['x','y'], index=df_sp.columns).T

        # Round the xy values
        if isinstance(rounding, int):
            df_xy = np.round(df_xy, rounding)

        # Return the pandas dataframe with the xy values
        return df_xy

     
    def plots(self, plots=['CIELAB', 'SP', 'SW', 'dE', 'dLab']):
        """Create plots

        Parameters
        ----------
        plots : list, optional
            _description_, by default ['CIELAB', 'SP', 'SW', 'dE', 'dLab']
        """

        for plot in plots:
            if plot == 'CIELAB':
                self.plot_CIELAB(legend_labels='default', legend_fontsize=18)

            elif plot == 'SP':
                self.plot_sp(spectra='i+f')

            elif plot == 'SW':
                self.plot_swatches_circle()

            elif plot == 'dE':
                self.plot_delta()

  
    def plot_bars(self, BWS_lines:Optional[bool] = False, coordinate:Optional[str] = 'dE00', dose_unit:Optional[str] = 'Hv', dose_value:Union[int, float, str] = 'hcd', xlabels:Union[str, list] = 'default', group_objects:Optional[bool] = False, fontsize:Optional[int] = 24, rotate_xlabels:Optional[int] = 45, position_xlabels:Optional[str] = 'right', position_text:Optional[tuple] = (0.75,0.98), colors:Union[str,float,list]=None, save:Optional[bool] = False, path_fig:Optional[str] = 'cwd'):
        """Plot a bar graph of a given colorimetric coordinate for a given light dose value.

        Parameters
        ----------
        BWS_lines : Optional[bool], optional
            Whether to display the blue wool standard values as horizontal lines or as bars, by default True

        coordinate : Optional[str], optional
            Colorimetric coordinate to be displayed, by default 'dE00'
            It can be any coordinates among the following list : ['L*','a*','b*','C*','h','dL*','da*','db*','dC*','dh','dE76','dE00','dR_vis'].

        dose_unit : Optional[str], optional
            Unit of the light energy dose, by default 'Hv'
            Any of the following units can be used: 'He', 'Hv', 't'. Where 'He' corresponds to radiant energy (MJ/m2), 'Hv' to exposure dose (Mlxh), and 't' to times (sec)

        dose_value : Union[int, float, str], optional
            Values of the light dose energy, by default 'hcd'
            'hcd' stands for 'highest common dose' value. When 'hcd' it will take the highest dose values common to all the microfading files.

        xlabels : Union[str, list], optional
            Values of the labels on the x-axis (one label per bar), by default 'default'
            When 'default', it takes the measurement id as label.

        fontsize : Optional[int], optional
            Fontsize of the plot (title, ticks, and labels), by default 24

        rotate_xlabels : Optional[int], optional
            Whether to rotate the labels on the x-axis, by default 0
            It can be any integer value between 0 and 360.

        position_xlabels : Optional[str], optional
            Position of the labels according to each bar ('center', 'left', 'right'), by default 'center'

        position_text : Optional[tuple], optional
            Position (x,y) of the text with the exposure dose value, by default (0.03,0.92)

        colors : Union[str,float,list], optional
            Colors of the bar, by default None
            When 'sample', the color of each bar will be based on srgb values computed from the reflectance values. 
            A single string or float value can also be used to define the color of all the bars (see matplotlib colour values). 
            A list string can also be given, in that case, the number of element in the list should be equal to the number of bars. 

        save : bool, optional
            Whether to save the figure, by default False

        path_fig : str, optional
            Absolute path required to save the figure, by default 'cwd'
            When 'cwd', it will save the figure in the current working directory.
        """

        # Function to truncate decimal values
        def trunc(values, decs=0):
            return np.trunc(values*10**decs)/(10**decs)

              
        # Define the light dose value      
        doses_dic = {'He':'He_MJ/m2', 'Hv':'Hv_Mlxh', 't':'t_sec'}
        max_doses = self.get_doses(dose_unit=dose_unit, max_doses=True, concat=True).values
        hcd = trunc(np.min(max_doses), 3)   # highest common dose truncated to 3 decimals
        
        if dose_value == 'hcd':
            dose_value = hcd
        elif dose_value > hcd:
            print(f'The choosen dose_value ({dose_value} {doses_dic[dose_unit].split("_")[1]}) is bigger than one of the final dose values. Thus the dose_value has been set to {np.min(max_doses)} {doses_dic[dose_unit].split("_")[1]}, which is the lowest final dose value.')
            dose_value = np.min(max_doses)

        
        # Define the labels on the x-axis
        if xlabels == 'default':
            xlabels = self.get_meas_ids

        elif xlabels == 'meas_nb':
            xlabels = [x.split('.')[-1] for x in self.get_meas_ids]

        elif xlabels in [x for x in self.get_metadata().index if '[' not in x]:
            xlabels = self.get_metadata(labels=xlabels).values

                
        # Define the colour of the bars
        if colors == 'sample':
            colors =[list(x) for x in self.get_sRGB(dose_values=0).T.values]
        
        elif isinstance(colors, str):
            colors = [colors] * len(self.files)

        elif isinstance(colors, float):
            colors = [str(colors)] * len(self.files)
              
        
        # Define the objects ID
        object_ids = self.get_metadata(labels='object_id').values

        
        # Define the object name
        object_names = self.get_metadata(labels='object_name').values
        
        # Gather the data and relevant info inside a dataframe
        all_data = self.get_cielab(coordinates=[coordinate], dose_unit=dose_unit, dose_values=dose_value, concat=False)
        cl_data = [x.iloc[0].values[0] for x in all_data]
        cl_data_std = [x.iloc[0].values[1] if 'std' in x.columns.get_level_values(2) else 0 for x in all_data]
        
        plot_data = {
            'y': cl_data,
            'y_std': cl_data_std, 
            'xlabels': xlabels,
            'type': self.get_metadata(labels='object_type').values,
            'name': object_ids,
            'objectID':self.get_metadata(['object_id']).values[0],
            'colors': colors
        }
        
        df_data = pd.DataFrame.from_dict(plot_data)        
        
        
        # Create the plot
        sns.set_theme(font='serif')
        fig, ax = plt.subplots(1,1, figsize=(15,8))

        if BWS_lines == True:         
            
            df_BWS = df_data[df_data['type'] == 'BWS']
            df_data = df_data[df_data['type'] != 'BWS']
            object_ids = df_data['objectID'].values
            
            ls_dic = {'BW1':'-','BW2':'--','BW3':'-.','BW4':':', 'BWS0028':'-','BWS0029':'--','BWS0030':'-.','BWS0031':':'}
            label_dic = {'BW1':'-','BW2':'--','BW3':'-.','BW4':':', 'BWS0028':'BW1','BWS0029':'BW2','BWS0030':'BW3','BWS0031':'BW4'}
            
            for col in df_BWS.T.columns:
                data_BWS = df_BWS.T[col]
                
                ax.axhline(data_BWS['y'], color='blue', ls =ls_dic[data_BWS['name']], label=label_dic[data_BWS['name']])
                ax.axhspan(ymin=data_BWS['y']-data_BWS['y_std'], ymax=data_BWS['y']+data_BWS['y_std'], alpha=0.5, color='0.75', ec='none')        
        
        #return df_data
        x = np.arange(0,len(df_data))

        
        if colors == None:
            colors = None
        else:
            colors = df_data['colors']

        if not group_objects: 
            ax.bar(x=x, height=df_data['y'], yerr=df_data['y_std'], capsize=5, color=colors, edgecolor='none')

        else:

            i = 1
            x_ticks = []
            labels = []

            
            for obj in sorted(set(object_ids)):

                df_obj = df_data.query(f'objectID == "{obj}"')
                

                y_values = df_obj['y'].values
                meas_ids = df_obj['xlabels'].values
                srgb_values = df_obj['colors'].values
                
                labels_obj = []
                N = len(meas_ids)    
                obj_tick = str(int(np.cumsum(np.arange(1,1+N))[-1] / N)).zfill(2)
                
                for ID, value, srgb in zip(meas_ids, y_values, srgb_values):
                
                    ax.bar(i, value, width=1, color=srgb, ec="none")
                    
                    labels_obj.append(str(ID.split('.')[2]))
                    x_ticks.append(i)
                    i = i + 1

                
                labels_obj = list(map(lambda x: x.replace((obj_tick), f'{obj_tick}\n{obj}'), labels_obj))
                
                labels.append(labels_obj)
            
                ax.bar(i, 0)
                labels.append([''])
                i = i + 1    
                x_ticks.append(i)

            # Define the labels for x-axis ticks
            labels = [x for xs in labels for x in xs]
            
            # Set the x-ticks and xlabels
            ax.set_xticks(x_ticks)
            ax.set_xticklabels(labels)

            # Display the legend
            handles, labels = ax.get_legend_handles_labels()
            unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
            ax.legend(*zip(*unique),fontsize=fontsize-4)




        ax.xaxis.set_tick_params(labelsize=fontsize)
        ax.yaxis.set_tick_params(labelsize=fontsize)

        ax.xaxis.grid() # horizontal lines only

        
        ax.set_ylabel(labels_eq[coordinate], fontsize=fontsize)

        if not group_objects: 
            ax.set_xticks(x)
            ax.set_xticklabels(df_data['xlabels'], rotation=rotate_xlabels, ha=position_xlabels)

        ax.text(x=position_text[0], y=position_text[1], s=f'Light dose = {dose_value} {doses_dic[dose_unit].split("_")[1]}', fontsize=fontsize-6, transform=ax.transAxes, ha='left', va='top')

        if BWS_lines == True:
            ax.legend(fontsize=fontsize-4)

        plt.tight_layout()

        if save == True:
            if path_fig == 'cwd':
                path_fig = f'{os.getcwd()}/{coordinate}-bar.png'                    
                
            fig.savefig(path_fig,dpi=300, facecolor='white') 

        plt.show()     


    def plot_bwse(self, frequency:Optional[bool] = False, bins:Optional[list] = [1,2,3,4,5], colors:Union[str,float,list]=None, figsize:Optional[tuple] = (10,10), rotate_xlabels:Optional[int] = 0, position_xlabels:Optional[str] = 'center', fontsize:Optional[int] = 24, fontsize_xaxis:Optional[int] = 20, title_fontsize:Optional[int] = 24, title:Optional[str] = None, save:Optional[bool] = False, path_fig:Optional[str] = 'cwd'):

        bwse_df = self.get_metadata(labels=['BWSE']).loc['BWSE']
        bwse_values = bwse_df.values
        labels = bwse_df.index

        wanted_data = [labels,bwse_values]

        if colors == 'sample':
            colors = self.get_sRGB(dose_values=0).values.reshape(len(self.files),-1)

        print('Work in progress. Function to be implemented in future versions.')
        return
        return wanted_data
        plotting.BWSE(data=wanted_data, frequency=frequency, bins=bins, figsize=figsize, colors=colors, fontsize=fontsize, title=title, title_fontsize=title_fontsize, rotate_xlabels=rotate_xlabels, position_xlabels=position_xlabels,  save=save, path_fig=path_fig)
    
    
    def plot_CIELAB(
            self,
            dE:Optional[bool] = False,
            stdev:Optional[bool] = True, 
            data_settings:Optional[dict] = {},
            figure_settings:Optional[dict] = {},
            legend_settings:Optional[dict] = {},
            lines_settings:Optional[dict] = {},             
            save:Optional[bool] = False,
            path_fig:Optional[str] = 'cwd', 
            report:Optional[bool] = False):
        """Plot the Lab values related to the input the microfading files.

        Parameters
        ----------
        
        dE : bool, optional
            Whether to display the dE00 curves in the bottom left suplots instead of the CIELAB 2D space, by default False
        
        stdev : bool, optional
            Whether to display the standard deviation values if any, by default True
        
        data_settings : dict, optional
            Adjust settings related to the data, by default {}.
            Enter key:value inside the dictionary. The following keys are valid : 'dose_unit', 'dose_values', 'data_type'.

            'dose_unit' [str] corresponds to the unit of the light energy dose, by default 'He'. 
            Any of the following units can be used: 'He', 'Hv', 't'. Where 'He' corresponds to radiant energy (MJ/m2), 'Hv' to exposure dose (Mlxh), and 't' to times (sec). If you set dE to True, it will plot the dE00 values as a function of the chosen 'dose_unit'.

            'dose values' [str,int,float,list,tuple] selects the light dose valules for which the colourimetric delta values will be returned, by default 'all'.
            When 'all', it returns the colourimetric values for all the dose values available in the given input data files.
            A single dose value (an integer or a float number) can be entered.
            A list of dose values, as integer or float, can also be entered.
            A tuple of three values (min, max, step) will be used in a numpy.arange() function to return an array of dose values.
            
            'data_type' [str,list] corresponds to the type of data to be displayed, by default 'all'.
            There are three data types you can choose from ('nominal', 'mean', 'std'). When 'all' it will select all the data_types, but you can enter a single data_type as a string or combined inside a list, e.g: ['nominal', 'mean']. For more information about the data types, please consult the online documentation (https://g-patin.github.io/microfading/datafiles/).
    
        figure_settings : dict, optional
            Adjust the settings related to the figure, by default {}.
            Enter key:value inside the dictionary. The following keys are valid : 'title', 'xlabel', 'ylabel', 'fontsize', 'fontsize_title'.

            'title' [str] defines the suptitle of the figure, by default None.

            'xlabel' [str] defines the x-axis label of the bottom left subplot. It only works when dE is set to True. By default, it takes the value based on the dose_unit (see data_settings).

            'ylabel' [str] defines the y-axis label of the bottom left subplot. It only works when dE is set to True. By default 'CIE $\Delta E_{00}$'.

            'fontsize' [int] defines the fontsize of the axes labels and ticks, by default 18.

            'fontsize_title' [int] defines the fontsize of the title if any, by default 20.

        legend_settings : dict, optional
            Adjust the settings related to the legend, by default {}.
            Enter key:value inside the dictionary. The following keys are valid : 'fontsize','labels', 'ncols', 'obs_ill', 'position', 'title'.

            'fontsize' [int] defines the fontsize of the legend, by default 14. 

            'labels' [str, list] defines the labels displayed inside the legend, by default 'default'. If you enter an empy list [] or an empty string '', the legend won't be displayed. When set to 'default', each label is made of the measurement id and the spot description. You can also enter a list of strings, as long as the number of string elements inside the list is equal to the number of measurements being displayed. Finally, you can enter a template string based on the parameters available in the info tab (metadata) of the measurement files. The parameters have to be inserted inside square brackets [], e.g: 'id: [meas_id] - [object_type]'. For more information about it, please consult the online documentation (https://g-patin.github.io/microfading/data-visualization/).

            'ncols' [int] defines the number of columns inside the legend, by default 1.

            'obs_ill' [bool] defines whether the observer and illuminant information should be displayed, by default False.

            'position' [str] defines the position of the legend inside the figure, by default 'in'.
            When 'in' the legend is displayed inside the plot, when 'out' the legend is located outside the plot.

            'title' [str] defines whether to add a title to the legend, by default None.

        lines_settings : dict, optional
            Adjust the settings related to the plot lines, by default {}.
            Enter key:value inside the dictionary. The following keys are valid : 'alpha', 'colors', 'markers', 'size'.

            'alpha' [int, float, list] defines the transparency of the markers, by default 1.
            It has to be a value between 0 and 1 included, where 0 corresponds to a fully transparent marker and 1 to an opaque marker. You can define a single alpha values (int or float) similar for all the measurements, or you can enter a list of numerical values if you wish to define the transparency related to individual measurements.

            'colors' [str, list] defines the colors of the markers, by default None.
            When 'sample', it will compute the initial color the sample on which the measurement was performed and use it a color for the marker. A single color value as string can be entered and will then be applied to all the measurements. A list of string can be entered to individually define the color related to each measurement. Valid values for the string are based on the matplotlib color values. 

            'markers' [str, list] defines the style of the markers, by default 'o'.
            When 'random', it will applied different marker styles. A single marker style as a string can be entered and will be applied to all the measurements. A list of string can be entered to individually define the marker related to each measurement. Valid values for the string are based on the matplotlib marker styles.

            'size' [int, list] defines the size of the markers, by default 6.
            When 'random', it will applied different marker sizes. A single marker size as a integer can be entered and will be applied to all the measurements. A list of integers can be entered to individually define the size of the marker related to each measurement. 
        
        save : bool, optional
            Whether to save the figure, by default False

        path_fig : str, optional
            Absolute path required to save the figure, by default 'cwd'
            When 'cwd', it will save the figure in the current working directory.

        report : bool, optional
            Whether to apply specific features for reports.
            [PARAMETER NOT ACTIVE YET]

        Returns
        -------
        png file
            It returns a figure with 4 subplots that can be saved as a png file.
        """

        # Extract the data settings           
        dose_unit = data_settings.get('dose_unit', 'He')
        dose_values = data_settings.get('dose_values', 'all') 
        data_type = data_settings.get('data_type', 'all')
        
        
        # Extract the legend settings
        legend_labels = legend_settings.get('labels', 'default')   
        legend_title = legend_settings.get('title', None)
        legend_obs_ill = legend_settings.get('obs_ill', False)


        # Define the colorimetric coordinates to plot
        if dE:
            coordinates = ['dE00','L*', 'a*', 'b*']
        else:
            coordinates = ['L*', 'a*', 'b*']

        # Whether to include the std values
        if stdev:
            data_type = 'all'
        else:
            data_type = ['nominal','mean']
        
        # Retrieve the data
        data = self.get_cielab(coordinates=coordinates, dose_unit=dose_unit, dose_values=dose_values, data_type=data_type, concat=True)    
        
        # Retrieve the metadata
        info = self.get_metadata()                     
                
        # Whether to show the observer and illuminant info
        if legend_obs_ill == True:
            obs_ill = '-'.join(list(info.loc[['observer', 'illuminant']].T.values[0]))
            legend_settings['obs_ill'] = obs_ill.replace('deg', '$^o$')
        
        # Define the labels
        if legend_labels == 'default':
            spot_descriptions = info.loc['spot_description'].values
            legend_labels = [f'{x}-{y}' for x,y in zip(self.get_meas_ids,spot_descriptions)]

            if legend_title == None:
                legend_title = 'Measurement $n^o$'

            legend_settings['labels'] = legend_labels
            legend_settings['title'] = legend_title

        elif '[' in legend_labels and ']' in legend_labels:

            values_in_brackets = re.findall(r'\[(\w+)\]', legend_labels)
            info_legend_labels = []

            for col in info.columns:
                # Replace each placeholder with the value from the info DataFrame
                label = legend_labels
                for value in values_in_brackets:
                    label = label.replace(f'[{value}]', str(info.loc[value, col]))
                info_legend_labels.append(label)

            legend_settings['labels'] = info_legend_labels

        # Whether to plot the observer and illuminant info
        if legend_obs_ill:
            
            if len(config.get_config_info()['colorimetry']) == 0:
                observer = '10deg'
                illuminant = 'D65'
            else:
                observer = config.get_colorimetry_info().loc['observer']['value']
                illuminant = config.get_colorimetry_info().loc['illuminant']['value']

            dic_obs = {'10deg':'$\mathrm{10^o}$', '2deg':'$\mathrm{2^o}$'}            
            obs_ill = f'{dic_obs[observer]}-{illuminant}'
        
        else:
            obs_ill = None

        
        plotting.CIELAB(
            data=data,
            dE=dE,
            stdev=stdev,
            data_settings=data_settings,
            figure_settings=figure_settings,
            legend_settings=legend_settings,
            lines_settings=lines_settings,            
            save=save,
            path_fig=path_fig
        )        
        

    def plot_coordinates(self, coordinates:Union[list, str] = ['L*', 'a*', 'b*'], dose_unit:Optional[str] = 'He', std:Optional[bool] = True, fontsize:Optional[int] = 24, ls:Union[list,str] = None, colors:Union[str,list] = None, title:Optional[str] = None, title_fontsize:Optional[int] = 20, legend_labels:Union[str,list] = 'default', legend_position:Optional[str] = 0, legend_fontsize:Optional[int] = 20, legend_title:Optional[str] = None, figsize:Optional[tuple] = 'default', save:Optional[bool] = False, path_fig:Optional[str] = 'cwd'):

        # Retrieve the data
        data_coordinates = self.get_cielab(coordinates=coordinates, dose_unit=dose_unit, concat=True)

        # Retrieve the info dataframe
        df_info = self.get_metadata()
        
        # Define the legend labels
        if legend_labels == 'default':           

            if 'spot_description' in df_info.index:                
                spot_descriptions = df_info.loc['spot_description'].values

            else:
                spot_descriptions = [''] * len(self.files)
                
            legend_labels = [f'{x}-{y}' for x,y in zip(self.get_meas_ids,spot_descriptions)]
        
        
        return plotting.coordinates(data=data_coordinates, std=std, fontsize=fontsize, legend_labels=legend_labels, legend_fontsize=legend_fontsize, legend_position=legend_position, legend_title=legend_title, title=title, title_fontsize=title_fontsize, ls=ls, figsize=figsize, save=save, path_fig=path_fig)       
    
    
    def plot_swatches_circle(self, orientation:Optional[str] = 'horizontal', light_doses:Optional[list] = [0,0.5,1,2,5,15], JND:Optional[list] = [1,2,3,5,10], dose_unit:Union[str,tuple] = 'Hv', dE:Optional[bool] = True, museum_exposure:Optional[tuple] = (), fontsize:Optional[int] = 32, equation:Optional[str] = 'power_3p', initial_params:Optional[List[float]] = 'auto', bounds:Optional[list] = (-np.inf, np.inf), save:Optional[bool] = False, path_fig:Optional[str] = 'cwd', title:Optional[str] = None, report:Optional[bool] = False, circle_h:Optional[float] = 0): 
        """Plot the microfading data with circular colored patches. 

        Parameters
        ----------

        light_doses : list, optional
            Light doses in Mlxh for which a coloured patches will be created, by default [0,0.5,1,2,5,1]
            There has been at least two numerical values in the list. The first value corresponds to the color background of the plot and is usually set to 0. The other values will be plotted as circular patches.

        JND : list, optional
            Whether to plot circular patches of just noticeable differences, by default [1,2,3,5,10]
            NOT YET IMPLEMENTED

        dose_unit : [str, tuple], optional
            Unit of the light energy dose, by default 'Hv'
            Any of the following units can be used: 'He', 'Hv', 't'. Where 'He' corresponds to radiant energy (MJ/m2), 'Hv' to exposure dose (Mlxh), and 't' to times (hours) (exh,50,10,365)
        
        dE : bool, optional
            Whether to include the dE00 value between the background and each circular patche, by default True

        fontsize : int, optional
            Fontsize of the plot (title, ticks, and labels), by default 24        

        equation : str, optional
            Mathematical equation used to fit the coordinate values, by default 'c0*(x**c1) + c2'.
            Any others mathematical can be given. The following equation can also be used for fitting microfading data: '((x) / (c0 + (c1*x)))'.

        initial_params : List[float], optional
            Initial guesses of the 'c' parameters given in the equation (c0, c1, c2, etc.), by default [0.1, 0.0]
            In the default values, only c0 and c1 are provided ; c2 is retrieved from the initial value of each colorimetric coordinate plot.

        bounds : List[float], optional

        save : bool, optional
            Whether to save the figure, by default False

        path_fig : str, optional
            Absolute path required to save the figure, by default 'cwd'
            When 'cwd', it will save the figure in the current working directory.

        title : str, optional
            Whether to add a title to the plot, by default None, by default None        

        report : bool, optional
            Whether to use the report configuration to create the visualization, by default False
            NOT YET IMPLEMENTED

        circle_h : float, optional
            Adjust the height of the colored circles, by default 0
            One can enter a negative or positive float number to shape the colored circles as desired (circular or more oval).

        Returns
        -------
        A png file
            _description_
        """
       
        # Define the title
        if title == 'default':
            title = list(self.get_meas_ids)

        
        # Compute the extrapolated Lab values
        list_extrapolated_Lab = []

        for coord in ['L*','a*','b*']:            

            fitted_coord = self.compute_fitting(coordinate=coord, plot=False, return_data=True, dose_unit=dose_unit, equation=equation,initial_params=initial_params, bounds=bounds,x_range=(light_doses[0], light_doses[-1]+1, 0.1))[1].loc[light_doses]
            
            list_extrapolated_Lab.append(fitted_coord.T.values)
                    
        
        # Run the plotting function for each file
        for i in range(0, len(self.files)):
            wanted_Lab = pd.DataFrame([x[i] for x in list_extrapolated_Lab]).T.values
            
            plotting.swatches_circle(data=[wanted_Lab], data_type='Lab', orientation=orientation, light_doses=light_doses, dose_unit=dose_unit, dE=dE, museum_exposure=museum_exposure, fontsize=fontsize, save=save, title=title, path_fig=path_fig, circle_h=circle_h)        
      

    def plot_swatches_rectangle(self, swatches:Optional[tuple] = ('i',1), labels:Optional[list] = 'default', bottom_scale:Optional[str] = 'JND', top_label:Optional[str] = 'Hv', colorbar:Optional[bool] = False, fontsize:Optional[int] = 24, title:Optional[str] = None, save:Optional[bool] = False, path_fig:Optional[str] = 'cwd'):

        # Adapt bottom scale for JND
        if bottom_scale == 'JND' and isinstance(swatches[1], (int,float)):
            bottom_scale = 'dE00'
            swatches = (swatches[0], np.round(swatches[1]*1.3,2))
        
        # Doses dic
        doses_dic = {'He': 'MJ/m2', 'Hv':'Mlxh'}


        # Define the dose_unit
        if bottom_scale == 'He' or bottom_scale == 'Hv':
            dose_unit = bottom_scale

        elif top_label == 'He' or top_label == 'Hv':
            dose_unit = top_label
        
        
        # Retrieve the analyses light dose values
        doses = [x for x in self.get_doses(dose_unit=dose_unit, max_doses=True, concat=False)]
        dose_min = np.min(doses)
        
        
        # Define the Lab values for the top colour swatches
        if swatches[0] == 'i':
            dose_value_top = 0
            top_text = 'Initial'

        elif isinstance(swatches[0], (int, float)):
            if swatches[0] > dose_min:
                print(f'Please, choose an initial dose value lower or equal to the final experimental light dose ({np.round(dose_min,2)} {doses_dic[dose_unit]}).')
                return
            else:
                dose_value_top = swatches[0] 
                top_text = f'{swatches[0]} {doses_dic[dose_unit]}'  
        else:
            print('Enter valid values for the swatches parameter, ie. a tuple of integer or float.')
            return
                
        Lab_top = [x.values[0] for x in self.get_cielab(coordinates=['L*','a*', 'b*'], dose_unit=dose_unit, dose_values=dose_value_top, concat=False)]
        
                
        # Define the Lab values for the bottom colour swatches
        
        if swatches[1] == 'f':                          # Select last measured values
            Lab_bottom = [x.iloc[-1].values for x in self.get_cielab(coordinates=['L*','a*', 'b*'], dose_unit=dose_unit, concat=False)]
            bottom_text = 'Final'
            wanted_dose = [x for x in self.get_doses(dose_unit=dose_unit, max_doses=True, concat=False)]

        elif isinstance(swatches[1], (int,float)):      # Select the values according to a dE or H value

            Lab_bottom = []

            if bottom_scale in ['He','Hv']:             # According to a dose value (He or Hv)
            
                for coord in ['L*','a*', 'b*']:               

                    coord_bottom = self.compute_fitting(plot=False, return_data=True,coordinate=coord,dose_unit=dose_unit, x_range=(0,swatches[1]+1,0.1))[1].loc[swatches[1]].values
                    Lab_bottom.append(coord_bottom) 

                Lab_bottom = pd.DataFrame(Lab_bottom).T.values  

            
            elif bottom_scale in ['dE76','dE00','dR_vis']:    # According to a dE or dR value
                
                max_doses = {'He':2000.1, 'Hv':200.1}
                dE_fitted = self.compute_fitting(plot=False, return_data=True,coordinate=bottom_scale,dose_unit=dose_unit, x_range=(0,max_doses[dose_unit],0.1))[1]                

                wanted_doses = []
                for col in dE_fitted.columns:

                    dE_data = dE_fitted[col]
                    

                    if dE_data.values[-1] > swatches[1]:
                        wanted_doses.append(interp1d(dE_data.values, dE_data.index)([swatches[1]])[0])
                    
                    else:
                        wanted_doses.append(dE_data.index[-1])

                for i, wanted_dose in enumerate(wanted_doses):
                    for coord in ['L*','a*', 'b*']:
                        coord_bottom = self.compute_fitting(plot=False, return_data=True,coordinate=coord,dose_unit=dose_unit, x_range=(0,wanted_dose+0.1,0.1))[1].values[-1][i]
                        
                        
                        Lab_bottom.append(coord_bottom)

                Lab_bottom = pd.DataFrame(Lab_bottom).T.values[0]
                Lab_bottom = Lab_bottom.reshape(len(wanted_doses),-1)
                
            
            bottom_text = f'{swatches[1]} {labels_eq[bottom_scale]}'
                
        else:
            print('Enter valid values for the swatches parameter, ie. a tuple of integer or float.')
            return

                
        # Pair the top and bottom Lab values
        wanted_data = [(x,y) for x,y in zip(Lab_top,Lab_bottom)]
        

        # Define the labels
        if labels == 'default':
            labels = list(self.get_metadata('meas_id').values)

        elif labels == 'none':
            labels = []


        # Define the top label values
        if top_label in ['He','Hv']:           

            top_labels = {top_label: np.round(wanted_doses,3)}

        if top_label in ['dE76','dE94','dE00']:
            methods_dE = {'dE76': 'CIE 1976', 'dE94': 'CIE 1994', 'dE00': 'CIE 2000'}
            top_label_values = [np.round(colour.delta_E(x[0],x[1], method=methods_dE[top_label]),2) for x in wanted_data]
            top_labels = {top_label:top_label_values}

        
        # Define the side annotations
        side_annotations = (top_text, bottom_text)

        # Whether to save the figure
        if save == True:
            if path_fig == 'cwd':
                path_fig = f'{os.getcwd()}/MFT_{"-".join(self.get_meas_ids)}_SW-rect.png'  


        # Run the plotting function
        plotting.swatches_rectangle(data=wanted_data, data_type='Lab', labels=labels, bottom_scale=bottom_scale, top_labels=top_labels, fontsize=fontsize, side_annotations=side_annotations, colorbar=colorbar, title=title, save=save, path_fig=path_fig)

    
    def plot_delta(
            self,
            coordinates:Union[list, str] = ['dE00'],
            stdev:Optional[bool] = True, 
            data_settings:Optional[dict] = {},
            figure_settings:Optional[dict] = {},
            legend_settings:Optional[dict] = {},
            lines_settings:Optional[dict] = {},
            text_settings:Optional[dict] = {},            
            save:Optional[bool] = False, 
            path_fig:Optional[str] = 'cwd'):
        """Plot the delta values of choosen colorimetric coordinates related to the microfading analyses.

        Parameters
        ----------
        
        coordinates : Union[list, str], optional
            List of colorimetric coordinates, by default ['dE00']
            Any of the following coordinates can be added to the list: 'dE76', 'dE00', 'dR_vis' , 'L*', 'a*', 'b*', 'C*', 'h'.

        stdev : bool, optional
            Whether to display the standard deviation values if any, by default True.
        
        data_settings : dict, optional
            Adjust settings related to the data, by default {}.
            Enter key:value inside the dictionary. The following keys are valid : 'dose_unit', 'dose_values', 'derivation', 'smoothing'.

            'dose_unit' corresponds to the unit of the light energy dose, by default 'He'. 
            Any of the following units can be used: 'He', 'Hv', 't'. Where 'He' corresponds to radiant energy (MJ/m2), 'Hv' to exposure dose (Mlxh), and 't' to times (sec)

            'dose values' selects the light dose valules for which the colourimetric delta values will be returned, by default 'all'.
            When 'all', it returns the colourimetric values for all the dose values available in the given input data files.
            A single dose value (an integer or a float number) can be entered.
            A list of dose values, as integer or float, can also be entered.
            A tuple of three values (min, max, step) will be used in a numpy.arange() function to return an array of dose values.

            'derivation' defines whether to compute to first derivative values, by default False.
            When True, it will return and plot the derivative values of the colourimetric delta values.

            'smoothing' defines whether to smooth the data, by default (1,0).
            It takes a tuple of two integers as value which is used as input for the Savitzky-Golay filter. The first value corresponds to the window_length and the second to the polyorder value.
        
        figure_settings : dict, optional
            Adjust the settings related to the figure, by default {}.
            Enter key:value inside the dictionary. The following keys are valid : 'figsize', 'title', 'xlabel', 'ylabel', 'xlim', 'ylim', 'fontsize', 'fontsize_title'.

            'figsize [tuple] defines the dimension of the figure, by default (15,9).

            'title' [str] defines the suptitle of the figure, by default None.

            'xlabel' [str] defines the x-axis label of the figure, by default, it takes the value based on the dose_unit (see data_settings). Nevertheless, you can also enter a value as a string and it will overrun the default behaviour.

            'ylabel' [str] defines the y-axis label of the figure, by default the label is based on the colorimetric coordinates being plotted. Nevertheless, you can also enter a value as a string and it will overrun the default behaviour.

            'xlim' [tuple] defines the limits of the x-axis, by default 0.
            Enter a tuple of two numerical values (start, end).

            'ylim' [tuple] defines the limits of the y-axis, by default None.
            Enter a tuple of two numerical values (start, end).

            'fontsize' [int] defines the fontsize of the axes labels and ticks, by default 18.

            'fontsize_title' [int] defines the fontsize of the title if any, by default 20.

        legend_settings : dict, optional
            Adjust the settings related to the legend, by default {}.
            Enter key:value inside the dictionary. The following keys are valid : 'fontsize','labels', 'ncols', 'position', 'title'.

            'fontsize' [int] defines the fontsize of the legend, by default 14. 

            'labels' [str, list] defines the labels displayed inside the legend, by default 'default'. If you enter an empy list [] or an empty string '', the legend won't be displayed. When set to 'default', each label is made of the measurement id and the spot description. You can also enter a list of strings, as long as the number of string elements inside the list is equal to the number of measurements being displayed. Finally, you can enter a template string based on the parameters available in the info tab (metadata) of the measurement files. The parameters have to be inserted inside square brackets [], e.g: 'id: [meas_id] - [object_type]'. For more information about it, please consult the online documentation (https://g-patin.github.io/microfading/).

            'ncols' [int] defines the number of columns inside the legend, by default 1.

            'position' [str] defines the position of the legend inside the figure, by default 'in'.
            When 'in' the legend is displayed inside the plot, when 'out' the legend is located outside the plot.

            'title' [str] defines whether to add a title to the legend, by default None.

        lines_settings : dict, optional
            Adjust the settings related to the plot lines, by default {}.
            Enter key:value inside the dictionary. The following keys are valid : 'colors', 'ls', 'lw'.
            
            'colors' [str, list] defines the colors of the markers, by default None.
            When 'sample', it will compute the initial color the sample on which the measurement was performed and use it a color for the marker. A single color value as string can be entered and will then be applied to all the measurements. A list of string can be entered to individually define the color related to each measurement. Valid values for the string are based on the matplotlib color values. 

            'ls' [str, list] defines the style of the lines, by default '-'.
            When 'random', it will applied different line styles. A single style as a string can be entered and will be applied to all the lines. A list of string can be entered to individually define the linestyle related to each measurement. Valid values for the line styles are based on the matplotlib library.

            'lw' [int, list] defines the width of the lines, by default 2.
            A single width value can be entered and will be applied to all the lines. A list of integers can be entered to individually define the width related to each measurement.       

        save : bool, optional
            Whether to save the figure, by default False

        path_fig : str, optional
            Absolute path required to save the figure, by default 'cwd'
            When 'cwd', it will save the figure in the current working directory.
        """
        
        # Extract the data settings           
        dose_unit = data_settings.get('dose_unit', 'He')
        dose_values = data_settings.get('dose_values', 'all') 
        derivation = data_settings.get('derivation', False)
        smoothing = data_settings.get('smoothing', (1,0))

        
        # Extract the legend settings
        legend_labels = legend_settings.get('labels', 'default')    
        initial_values = legend_settings.get('initial_values', False)

        # Retrieve the info dataframe
        df_info = self.get_metadata()

        
        # Define the colour of the curves
        colors = lines_settings.get('colors', None)
        
        if colors == 'sample':
            colors = list(self.get_sRGB(dose_values=0, clip=True).T.values)
        
        lines_settings['colors'] = colors
        

        # Define the labels legend
        if len(coordinates) == 1:

            if legend_labels == 'default':           

                if 'spot_description' in df_info.index:                
                    spot_descriptions = df_info.loc['spot_description'].values

                else:
                    spot_descriptions = [''] * len(self.files)
                
                legend_labels = [f'{x}-{y}' for x,y in zip(self.get_meas_ids,spot_descriptions)]
                legend_title = 'Measurement $n^o$'

            elif legend_labels == None or legend_labels == 'none':
                legend_labels = []

            elif isinstance(legend_labels, str):
                index_info = [x.strip() for x in legend_labels.split(',')]
                
                if 'meas_nb' in index_info:                
                 
                    df_info.T['meas_nb'] = [x.split('.')[-1] for x in df_info['meas_id']]

                legend_labels = [', '.join(x) for x in df_info[index_info].values]

            legend_settings['labels'] = legend_labels

        else:
            if legend_labels == 'default':

                legend_labels = coordinates * len(self.files)                
                legend_labels = [labels_eq[x] for x in legend_labels]
                
                legend_settings['labels'] = legend_labels
        
        

        '''
        # set the labels of the legend
        #if len(legend_labels) == 0:
        #    legend_labels = ['none'] * len(data)

        if len(coordinates) == 1:
            legend_labels = [[x] for x in legend_labels]
            list_ls = [[None]] * len(data)
            coordinates = [f'd{x}' if x in ['L*','a*','b*','C*','h'] else x for x in coordinates]
        
        else:
            list_ls = [[ls_dic[x] for x in coordinates]] * len(data)
        
        if len(initial_values) > 0:            
            
            dy_unit = [f'd{x}' if x in ['L*','a*','b*','C*','h'] else x for x in coordinates]
            dy_unit = [labels_eq[x] for x in dy_unit]
            #y_unit = [f'{x} ({x[1:]} init$ = {i})' for x,i in zip(y_unit, initial_values)]
            dy_unit = [f'{x} (${c[0]}^*_i$ = {i})' for x,c,i in zip(dy_unit,coordinates, initial_values)]

            #dy_unit = [f'{x} (${c[0]}^*_i$ = {i})' if x in ['L*','a*','b*','C*','h'] else x for x in zip(initial_values.keys(), initial_values.values())]
            dy_unit = [f'{labels_eq[x]} (${x[1]}^*_i$ = {np.round(initial_values[x[1:]],1)})' if x in ['dL*','da*','db*','dC*','dh'] else labels_eq[x] for x in coordinates]

        else:
            dy_unit = [f'd{x}' if x in ['L*','a*','b*','C*','h'] else x for x in coordinates]        
            dy_unit = [labels_eq[x] for x in dy_unit]

        legend_labels = [dy_unit] * len(data)
        '''
       
        
        
        # Retrieve the data
        data = self.compute_delta(coordinates=coordinates, dose_unit=dose_unit, dose_values=dose_values, derivation=derivation, concat=True)

                
        #  Smooth the data
        data = pd.DataFrame(data=savgol_filter(data,smoothing[0],smoothing[1], axis=0), index=data.index, columns=data.columns)

        
        # Add the initial values of the colorimetric coordinates
        '''
        if initial_values:  
            initial_values = {}          
            for coord in coordinates:
                if coord in ['dL*', 'da*', 'db*', 'dC*', 'dh']:
                    initial_value = self.get_cielab(coordinates=[coord[1:]])[0][coord[1:]].iloc[0,:].values[0]
                    initial_values[coord[1:]] = initial_value
        else:
            initial_values = {}  
        
        
        if len(meas_nbs) > 1:
            initial_values = {}
        '''
               

        # Define the saving folder in case the figure should be saved
        filename = ''
        if save:
            if path_fig == 'default':
                path_fig = self.get_dir(folder_type='figures') / filename                

            if path_fig == 'cwd':
                path_fig = f'{os.getcwd()}/{filename}' 
        
        
        plotting.delta(
            data=data,
            stdev=stdev,
            data_settings=data_settings,
            figure_settings=figure_settings,
            legend_settings=legend_settings,
            lines_settings=lines_settings,
            text_settings=text_settings,
            save=save,
            path_fig=path_fig
        )
        
        

    def plot_sp(
            self, 
            spectra:Optional[str] = 'i',
            stdev:Optional[bool] = False, 
            data_settings:Optional[dict] = {},
            figure_settings:Optional[dict] = {},
            legend_settings:Optional[dict] = {},
            lines_settings:Optional[dict] = {},
            text_settings:Optional[dict] = {},
            save:Optional[bool] = False, 
            path_fig:Optional[str] = 'cwd',
            report:Optional[bool] = False,
        ):
        """Plot the reflectance spectra corresponding to the associated microfading analyses.

        Parameters
        ----------        

        spectra : Optional[str], optional
            Define which spectra to display, by default 'i'
            'i' for initial spectral, 
            'f' for final spectra,
            'i+f' for initial and final spectra, 
            'all' for all the spectra, 
            a tuple of two values (a, b) can be entered to plot spectra for specific dose values. The first parameter ("a") indicates the dose_unit ('He', 'Hv', 't'). The second parameter ("b") corresponds to the dose values, it can be a single integer or float, a list of integers or floats, or a tuple of three integers (start, end, step). When a single value is given, it will plot the spectrum related to the given dose value. When a list of values is given, it will plot as much spectra as provided values. When a tuple is given, it will plot the requested amount of spectra. For more information and examples, please consult the online documentation (https://g-patin.github.io/microfading/).           

        stdev : bool, optional
            Whether to show the standard deviation values, by default False

        data_settings : dict, optional
            Adjust settings related to the data, by default {}.
            Enter key:value inside the dictionary. The following keys are valid : 'mode', 'derivation, 'dose_unit', 'smoothing', 'wl_range'

            'mode' [string] defines the type or mode of the measurement (absorbance or refectance), by default 'R'.
            When 'R', it returns reflectance spectra. When 'A', it returns absorption spectra using the following equation: A = -log(R).

            'derivation' defines whether to compute to first derivative values, by default False.
            When True, it will return and plot the derivative values of the colourimetric delta values.
            
            'dose_unit' corresponds to the unit of the light energy dose, by default 'He'. 
            Any of the following units can be used: 'He', 'Hv', 't'. Where 'He' corresponds to radiant energy (MJ/m2), 'Hv' to exposure dose (Mlxh), and 't' to times (sec)            
            
            'smoothing' defines whether to smooth the data, by default (1,0).
            It takes a tuple of two integers as value which is used as input for the Savitzky-Golay filter. The first value corresponds to the window_length and the second to the polyorder value.

            'wl_range' [tuple] defines the wavelength range with a two-values integer tuple corresponding to the lowest and highest wavelength values, by default None

        figure_settings : dict, optional
            Adjust the settings related to the figure, by default {}.
            Enter key:value inside the dictionary. The following keys are valid : 'figsize', 'title', 'xlabel', 'ylabel', 'xlim', 'ylim', 'fontsize', 'fontsize_title'.

            'figsize [tuple] defines the dimension of the figure, by default (15,9).

            'title' [str] defines the suptitle of the figure, by default None.

            'xlabel' [str] defines the x-axis label of the figure, by default, it takes the value based on the dose_unit (see data_settings). Nevertheless, you can also enter a value as a string and it will overrun the default behaviour.

            'ylabel' [str] defines the y-axis label of the figure, by default the label is based on the colorimetric coordinates being plotted. Nevertheless, you can also enter a value as a string and it will overrun the default behaviour.

            'xlim' [tuple] defines the limits of the x-axis, by default 0.
            Enter a tuple of two numerical values (start, end).

            'ylim' [tuple] defines the limits of the y-axis, by default None.
            Enter a tuple of two numerical values (start, end).

            'fontsize' [int] defines the fontsize of the axes labels and ticks, by default 18.

            'fontsize_title' [int] defines the fontsize of the title if any, by default 20.
        
        legend_settings : dict, optional
            Adjust the settings related to the legend, by default {}.
            Enter key:value inside the dictionary. The following keys are valid : 'fontsize','labels', 'ncols', 'position', 'title'.

            'fontsize' [int] defines the fontsize of the legend, by default 14. 

            'labels' [str, list] defines the labels displayed inside the legend, by default 'default'. If you enter an empy list [] or an empty string '', the legend won't be displayed. When set to 'default', each label is made of the measurement id and the spot description. You can also enter a list of strings, as long as the number of string elements inside the list is equal to the number of measurements being displayed. Finally, you can enter a template string based on the parameters available in the info tab (metadata) of the measurement files. The parameters have to be inserted inside square brackets [], e.g: 'id: [meas_id] - [object_type]'. For more information about it, please consult the online documentation (https://g-patin.github.io/microfading/).

            'ncols' [int] defines the number of columns inside the legend, by default 1.

            'position' [str] defines the position of the legend inside the figure, by default 'in'.
            When 'in' the legend is displayed inside the plot, when 'out' the legend is located outside the plot.

            'title' [str] defines whether to add a title to the legend, by default None.
        
        lines_settings : dict, optional
            Adjust the settings related to the plot lines, by default {}.
            Enter key:value inside the dictionary. The following keys are valid : 'colors', 'ls', 'lw'.
            
            'colors' [str, list] defines the colors of the markers, by default None.
            When 'sample', it will compute the initial color the sample on which the measurement was performed and use it a color for the marker. A single color value as string can be entered and will then be applied to all the measurements. A list of string can be entered to individually define the color related to each measurement. Valid values for the string are based on the matplotlib color values. 

            'ls' [str, list] defines the style of the lines, by default '-'.
            When 'random', it will applied different line styles. A single style as a string can be entered and will be applied to all the lines. A list of string can be entered to individually define the linestyle related to each measurement. Valid values for the line styles are based on the matplotlib library.
            
        save : bool, optional
            Whether to save the figure, by default False

        path_fig : str, optional
            Absolute path required to save the figure, by default 'cwd'
            When 'cwd', it will save the figure in the current working directory.       

        Returns
        -------
        _type_
            It returns a figure that can be save as a png file.
        """

        # Apply the report characteristics
        if report:
            save = True
            colors = 'sample'
            spectra = 'i+f'
            fontsize = 30

        # Extract the data settings 
        dose_unit = data_settings.get('dose_unit', 'He')        
        derivation = data_settings.get('derivation', False)
        smoothing = data_settings.get('smoothing', (1,0))
        data_mode = data_settings.get('mode', 'R')     
        wl_range = data_settings.get('wl_range', None)

        # Extract the legend settings    
        legend_labels = legend_settings.get('labels', 'default')
        legend_title = legend_settings.get('title', 'default')

        # Extract the lines settings
        lw = lines_settings.get('lw', 'default')
        ls = lines_settings.get('ls', 'default')
        colors = lines_settings.get('colors', 'none')


        # Define the wanted light dose values

        max_doses = self.get_doses(dose_unit=dose_unit, max_doses=True).values[0]

        if spectra == 'i':
            wanted_doses = 0
        
        elif spectra == 'f':
            wanted_doses = max_doses

        elif spectra == 'i+f':
            pass 
        
        elif isinstance(spectra, tuple) and len(spectra)==2:
            wanted_doses = spectra[1]
        
        
        # Retrieve the metadata
        info = self.get_metadata()

        if 'spot_description' in info.index:                
            spot_descriptions = info.loc['spot_description'].values

        else:
            spot_descriptions = [''] * len(self.files)

        
        # Define the labels
        if legend_labels == 'none':
            legend_settings['labels'] = []

        elif legend_labels == 'default' and spectra in ['i', 'f', 'i+f']:
            legend_labels = sorted([f'{x}-{y}' for x,y in zip(self.get_meas_ids,spot_descriptions)])
            legend_title = 'Measurement $n^o$'     
        
        elif isinstance(legend_labels, str) and not 'default':
            index_info = [x.strip() for x in legend_labels.split(',')]
            df_metadata = self.get_metadata().T

            if 'meas_nb' in index_info:                
                df_metadata['meas_nb'] = [x.split('.')[-1] for x in df_metadata['meas_id']]

            legend_labels = [', '.join(x) for x in df_metadata[index_info].values]

        legend_settings['labels'] = legend_labels
                
        
        # Retrieve the spectral data
        
        if spectra == 'i':
            
            data_sp = self.get_spectra(wl_range=wl_range, dose_unit=dose_unit, dose_values=wanted_doses, spectral_mode=data_mode,derivation=derivation,smoothing=smoothing, concat=True)

            text = 'Initial spectra'
            text_settings['text'] = text

        elif spectra == 'f':
            data_sp_all = self.get_spectra(wl_range=wl_range, dose_unit=dose_unit,dose_values='all', spectral_mode=data_mode,derivation=derivation,smoothing=smoothing, concat=True)        
            
            result_columns = []

            for meas_id, dose in zip(self.get_meas_ids, wanted_doses):
               
                # Select columns for this meas_id and max dose
                mask = (
                    (data_sp_all.columns.get_level_values('meas_id') == meas_id) &
                    (data_sp_all.columns.get_level_values(1).isin([dose]))
                )
                result_columns.extend(data_sp_all.columns[mask])

            # Select the desired columns
            data_sp = data_sp_all.loc[:, result_columns]
            
            text = 'Final spectra'
            text_settings['text'] = text
        
        
        elif spectra == 'i+f':
            data_sp_all = self.get_spectra(wl_range=wl_range, dose_unit=dose_unit,dose_values='all', spectral_mode=data_mode,derivation=derivation,smoothing=smoothing, concat=True)            
            #data_sp = [x[x.columns.get_level_values(0).unique()[0]][x.columns.get_level_values(1)[[0]+[-1]]] for x in data_sp_all]
                       
            result_columns = []

            for meas_id, max_dose in zip(self.get_meas_ids, max_doses):
                
                # Select columns for this meas_id and first/last doses
                mask = (
                    (data_sp_all.columns.get_level_values('meas_id') == meas_id) &
                    (data_sp_all.columns.get_level_values(1).isin([0, max_dose]))
                )
                result_columns.extend(data_sp_all.columns[mask])

            # Select the desired columns
            data_sp = data_sp_all.loc[:, result_columns]

            # Retrieve the number of curves
            num_curves = (data_sp.loc[:, data_sp.columns.get_level_values('data_type') != 'std']).shape[1] 

            ls = ['-', '--'] * num_curves
            lw = [3,2] * num_curves
            black_lines = ['k'] * len(data_sp)    
            colors_start = self.get_sRGB(dose_values=0).T.values        
            colors = list(itertools.chain.from_iterable(zip(colors_start, black_lines)))  
            text = 'Initial and final spectra (black dashed lines)'

            lines_settings['ls'] = ls
            lines_settings['lw'] = lw
            lines_settings['colors'] = colors
            text_settings['text'] = text

            none_labels = [None] * len(legend_labels)
            new_legend_labels = [x for y in zip(legend_labels, none_labels) for x in y]
            legend_settings['labels'] = new_legend_labels

        
        elif isinstance(spectra, tuple) and len(spectra)==2:
            dose_unit = spectra[0]
            dose_values = wanted_doses           

            data_sp = self.get_spectra(wl_range=wl_range, dose_unit=dose_unit, dose_values=dose_values, spectral_mode=data_mode,derivation=derivation,smoothing=smoothing, concat=True)
            
            

            if ls == 'default':
                lines_settings['ls'] = 'random'

            if lw == 'lw':
                lines_settings['lw'] = 2

            if isinstance(dose_values, tuple):
                dose_values = np.arange(dose_values[0], dose_values[1], dose_values[2])
            
            if isinstance(dose_values, (int, float)) and legend_title == 'Measurement $n^o$':
                legend_settings['title'] = f'Light dose {dose_unit} = {dose_values} {labels_eq[dose_unit]}'
            
            elif legend_labels == 'default' and isinstance(dose_values, (list, tuple)):                
                
                legend_settings['labels'] = dose_values
                legend_settings['title'] = f'Light dose {dose_unit} ({labels_eq[dose_unit]})'

                if colors == 'sample':
                    colors = list(self.get_sRGB(dose_values=dose_values, clip=True).T.values)
        
        

        # Determine the number of curves
        data_sp_nominal = (data_sp.loc[:, data_sp.columns.get_level_values('data_type') != 'std'])
        num_curves = data_sp_nominal.shape[1]  

        
        # Define the colour of the curves
        if colors == 'none':
            colors = [None] * num_curves        

        elif spectra == 'i+f':
            pass

        elif colors == 'sample':
            if spectra == 'f':
                wanted_doses = 0
            
            colors = list(self.get_sRGB(dose_values=wanted_doses, clip=True).T.values)

        elif isinstance(colors, str):
            colors = [colors] * num_curves

          
        lines_settings['colors'] = colors
           
        
        return plotting.spectra(
            data=data_sp,
            stdev=stdev,
            data_settings=data_settings,
            figure_settings=figure_settings,
            legend_settings=legend_settings,
            lines_settings=lines_settings,
            text_settings=text_settings,
            save=save,
            path_fig=path_fig
        )
        
        '''
        # Select the spectral data
        if spectra == 'i':            
            #data_sp_all = self.get_spectra(wl_range=wl_range, smoothing=smoothing, concat=False)
            #data_sp = [x[x.columns.get_level_values(0)[0]] for x in data_sp_all]     
            data_sp = self.get_spectra(wl_range=wl_range, dose_values=0, spectral_mode=data_mode, smoothing=smoothing, concat=True)       

            text = 'Initial spectra'

        elif spectra == 'f':
            data_sp_all = self.get_spectra(wl_range=wl_range, smoothing=smoothing)
            data_sp =[x[x.columns.get_level_values(0)[-1]] for x in data_sp_all] 

            text = 'Final spectra'

        elif spectra == 'i+f':
            data_sp_all = self.get_spectra(wl_range=wl_range, smoothing=smoothing)
            data_sp = [x[x.columns.get_level_values(0)[[0]+[-1]]] for x in data_sp_all]            
            
            ls = ['-', '--'] * len(data_sp)
            lw = [3,2] * len(data_sp)
            black_lines = ['k'] * len(data_sp)            
            colors = list(itertools.chain.from_iterable(zip(colors, black_lines)))            
            

            if legend_labels == 'default':
                meas_labels = [f'{x}-{y}' for x,y in zip(self.get_meas_ids,spot_descriptions)]
            else:
                meas_labels = legend_labels
            none_labels = [None] * len(meas_labels)
            legend_labels = [item for pair in zip(meas_labels, none_labels) for item in pair]

            text = 'Initial and final spectra (black dashed lines)'

        elif spectra == 'doses':
            data_sp = self.get_spectra(wl_range=wl_range, dose_unit=dose_unit,dose_values=dose_values, smoothing=smoothing)

            
            dose_units = {'He': 'MJ/m2', 'Hv': 'Mlxh', 't': 'sec'}
            legend_title = f'Light dose values'
            legend_labels = [f'{str(x)} {dose_units[dose_unit]}' for x in dose_values] * len(data_sp)

            text = f'Light dose = {dose_values} {dose_units[dose_unit]}'
            
            ls_list = ['-','--','-.',':','-','--','-.',':','-','--','-.',':',]
            ls = ls_list[:len(dose_values)] * len(data_sp)        
            srgb_i = self.get_sRGB().iloc[0,:].values.reshape(-1, 3)            
            colors = np.repeat(srgb_i, data_sp[0].shape[1], axis=0).clip(0,1)          

        else:
            print(f'"{spectra}" is not an adequate value. Enter a value for the parameter "spectra" among the following list: "i", "f", "i+f", "doses".')
            return           
        '''                        
        # whether to compute the absorption spectra
        #if spectral_mode == 'A':
            #data_sp = [np.log(x) * (-1) for x in data_sp]
        
        # Reset the index
        #data = [x.reset_index() for x in data_sp]
        
        # Whether to compute the first derivative
        #if derivation:
        #    data_sp = pd.DataFrame(np.gradient(data_sp)[0], columns=data_sp.columns, index=data_sp.index)
            #data = [pd.concat([x.iloc[:,0], pd.DataFrame(np.gradient(x.iloc[:,1:], axis=0))], axis=1) for x in data]

        # Compile the spectra to plot inside a list
        wanted_data = []  
        wanted_std = []

        # Set the wavelength column as index
        #data = [x.set_index(x.columns.get_level_values(0)[0]) for x in data]          
             
        #return data_sp
        # Add the std values
        '''
        if stdev:            
            try:     
                
                values_data = [x.T.iloc[::2].values for x in data]
                values_wl = [x.index for x in data]
                for el1, wl in zip(values_data, values_wl):
                    for el2 in el1:
                        wanted_data.append((wl,el2))

                values_std = [x.T.iloc[1::2].values for x in data]                
                for el1 in values_std:
                    for el2 in el1:
                        wanted_std.append(el2)
            except IndexError:
                wanted_std = []
            
        else:
            for el in data:                
                data_values = [ (el.index,x) for x in el.T.values]
                wanted_data = wanted_data + data_values 
            wanted_std = []
        '''
        #return wanted_data
        
        
        
        #return plotting.spectra(data=wanted_data, stds=wanted_std, spectral_mode=spectral_mode, legend_labels=legend_labels, title=title, fontsize=fontsize, legend_fontsize=fontsize_legend, legend_title=legend_title, legend_position=legend_position, x_range=wl_range, colors=colors, lw=lw, ls=ls, text=text, text_xy=text_xy, save=save, path_fig=path_fig, derivation=derivation)
       

    def plot_sp_delta(self,spectra:Optional[tuple] = ('i','f'), dose_unit:Optional[str] = 'Hv', legend_labels:Union[str,list] = 'default', title:Optional[str] = None, fontsize:Optional[int] = 24, legend_fontsize:Optional[int] = 24, legend_title='', wl_range:Union[int,float,list,tuple] = 'default', colors:Union[str,list] = None, spectral_mode:Optional[str] = 'dR', derivation:Optional[bool] = False, smoothing:Optional[tuple] = (1,0), save:Optional[bool] = False, path_fig:Optional[str] = 'cwd', report:Optional[bool] = False):

        # Set the wavelength range       
        if wl_range == 'default':

            device_info = sorted(set(self.get_metadata('device')))
            
            
            if len(device_info) == 1:                
                device_id = device_info[0].split('_')[0]

            else:
                device_id = device_info[0].split('_')[0]


            if device_id in list(get_config()['devices'].keys()):
                wl_range = get_config()['devices'][device_id] ['wl_range']

                if wl_range != None:
                    wl_range = tuple(wl_range)

            else:
                wl_ranges = []

                wl_range = tuple(np.min(wl_ranges), np.max(wl_ranges))
                            
                
        # Set the report parameters
        if report:
            pass
        
        if spectra == ('i','f'):

            sp_data = [x.iloc[:,[0,-1]] for x in self.get_spectra(wl_range=wl_range, spectral_mode=spectral_mode, smoothing=smoothing)]
            sp_delta = [x.iloc[:,1] - x.iloc[:,0] for x in sp_data]
            wanted_data = [(x.index, x.values) for x in sp_delta]

        elif spectra[0] == 'i':
            
            sp1 = [x.iloc[:,0] for x in self.get_spectra(wl_range=wl_range, spectral_mode=spectral_mode, smoothing=smoothing)]
            sp2 = [x.values.flatten() for x in self.get_spectra(dose_unit=dose_unit, dose_values=float(spectra[1]),wl_range=wl_range, spectral_mode=spectral_mode)]
            
            wanted_data = [(x.index,np.array(y)-np.array(x)) for x,y in zip(sp1,sp2)]

        elif spectra[1] == 'f':

            sp1 = [x.values.flatten() for x in self.get_spectra(dose_unit=dose_unit, dose_values=float(spectra[0]), wl_range=wl_range, spectral_mode=spectral_mode)]            
            sp2 = [x.iloc[:,-1] for x in self.get_spectra(wl_range=wl_range, spectral_mode=spectral_mode)]            
            
            wanted_data = [(y.index,np.array(y)-np.array(x)) for x,y in zip(sp1,sp2)]
        
        else:

            wavelengths = self.get_wavelength.T.values
            sp1 = [x.values.flatten() for x in self.get_spectra(dose_unit=dose_unit, dose_values=float(spectra[0]),wl_range=wl_range, spectral_mode=spectral_mode)]
            sp2 = [x.values.flatten() for x in self.get_spectra(dose_unit=dose_unit, dose_values=float(spectra[1]),wl_range=wl_range, spectral_mode=spectral_mode)]
            
            wanted_data = [(w,np.array(y)-np.array(x)) for w,x,y in zip(wavelengths,sp1,sp2)]   
                 
        # Retrieve the metadata
        info = self.get_metadata()

        if 'group_description' in info.index:                
            group_descriptions = info.loc['group_description'].values

        else:
            group_descriptions = [''] * len(self.files)        
        
        
        # Define the colour of the curves
        if colors == 'sample':
            colors = self.get_sRGB().iloc[0,:].values.clip(0,1).reshape(len(self.files),-1)

        elif isinstance(colors, str):
            colors = [colors] * len(self.files)

        elif colors == None:
            colors = [None] * len(self.files)

        # Define the labels
        if legend_labels == 'default':
            legend_labels = [f'{x}-{y}' for x,y in zip(self.get_meas_ids,group_descriptions)]
            legend_title = 'Measurement $n^o$'
             
        # Whether to compute the first derivative
        if derivation:
            pass  # to implement in future versions
            #wanted_data = [x.reset_index() for x in wanted_data]
            #wanted_data = [pd.concat([x.iloc[:,0], pd.DataFrame(np.gradient(x.iloc[:,1:], axis=0))], axis=1) for x in wanted_data]
            #wanted_data = [x.set_index(x.columns.get_level_values(0)[0]) for x in wanted_data] 

        
        #return wanted_data
        plotting.spectra(data=wanted_data, spectral_mode=spectral_mode, x_range=wl_range, colors=colors, fontsize_legend=legend_fontsize, legend_labels=legend_labels, legend_title=legend_title, title=title, fontsize=fontsize, save=save, path_fig=path_fig, derivation=derivation)
      
     
    def make_report(self, folder_figures, folder_report:Optional[str] = 'cwd', type:Optional[str] = 'single', authors:Optional[str] = 'default'):

        # Set the folder to a Path object
        folder_figures = Path(folder_figures)
        
        # Retrieve all the filgures in the folder
        all_figure_files = os.listdir(folder_figures)          

        # Define the folder where the report should be saved
        if folder_report == 'cwd':
            folder_report = Path(os.getcwd())  
        else:
            if not Path(folder_report).exists():
                print(f'The folder report you entered ({folder_report}) is not valid.')
                return  
            else:
                folder_report = Path(folder_report) 

        # Define some functions
        def generate_latex_table(df):
            table_rows = []
            for _, row in df.iterrows():
                table_rows.append(' & '.join(map(str, row.values)) + ' \\\\ ') 
            return '\n'.join(table_rows)
        

        def combine_images(sp_report_path, swv_circles_report_path, dlch_report_path, output_path):

            # Open the images
            sp_report = Image.open(sp_report_path)
            swv_circles_report = Image.open(swv_circles_report_path)
            dlch_report = Image.open(dlch_report_path)

            # Define the desired width for the images in the left column
            desired_width_left = 1100  # Adjust as needed
            desired_width_right = 400  # Adjust as needed

            # Calculate the scaling factors
            sp_scaling_factor = desired_width_left / sp_report.width
            swv_scaling_factor = desired_width_right / swv_circles_report.width
            dlch_scaling_factor = desired_width_left / dlch_report.width

            # Calculate the new sizes while maintaining aspect ratio
            sp_new_size = (int(sp_report.width * sp_scaling_factor), int(sp_report.height * sp_scaling_factor))
            swv_new_size = (int(swv_circles_report.width * swv_scaling_factor), int(swv_circles_report.height * swv_scaling_factor))
            dlch_new_size = (int(dlch_report.width * dlch_scaling_factor), int(dlch_report.height * dlch_scaling_factor))

            # Resize the images
            sp_report_resized = sp_report.resize(sp_new_size, Image.LANCZOS)
            swv_circles_report_resized = swv_circles_report.resize(swv_new_size, Image.LANCZOS)
            dlch_report_resized = dlch_report.resize(dlch_new_size, Image.LANCZOS)

            # Calculate the total width and height for the combined image
            total_width = desired_width_left + desired_width_right            
            total_height = sp_new_size[1] + dlch_new_size[1]            

            # Create a new blank image with white background
            combined_image = Image.new('RGB', (total_width, total_height), 'white')

            # Paste the resized images into the combined image
            combined_image.paste(sp_report_resized, (0, 0))
            combined_image.paste(swv_circles_report_resized, (desired_width_left, 0))            
            combined_image.paste(dlch_report_resized, (0, sp_new_size[1]))
            
            # Save the combined image
            combined_image.save(output_path)




        if type == 'single':

            for file, id in zip(self.files, self.get_meas_ids):

                                
                figure1 = [file for file in all_figure_files if id in file and 'CIELAB-report' in file][0]                
                figure_SP = [f'{folder_figures}/{file}' for file in all_figure_files if f'{id}' in file and 'SP-report' in file][0]
                figure_dLCh = [f'{folder_figures}/{file}' for file in all_figure_files if f'{id}' in file and 'dLCh-report' in file][0]
                figure_SW = [f'{folder_figures}/{file}' for file in all_figure_files if f'{id}' in file and 'SWVcircles-report' in file][0]
                im_combined_path = Path(folder_figures) / f'{id}_report_SP-dLCh-SW.png'

                # Combine the images
                combine_images(figure_SP, figure_SW, figure_dLCh, im_combined_path)
                
                metadata = self.get_metadata()[id]

                if authors == 'default':
                    authors = metadata['authors'].replace('_','-')

                host_institution = metadata['host_institution']
                if '_' in host_institution:
                    host_institution_name = host_institution.split('_')[1]
                    host_institution_department = host_institution.split('_')[1]

                else:
                    host_institution_name = host_institution
                    host_institution_department = ''
                

                BWSE = metadata['BWSE']
                if np.isnan(BWSE):
                    BWSE = 'undefined'
                else:
                    BWSE = str(BWSE)

                spot_materials = metadata['spot_components']
                
                

                try:
                    if '_' in spot_materials:
                        spot_materials = spot_materials.replace('_','-')

                except TypeError:            
                    if np.isnan(spot_materials):
                        spot_materials = 'undefined' 
                    

                info_object = """
                    \\textbf{Analysis ID} & [analysisId] \\\\
                    \\textbf{Analysis date} & [analysisDate] \\\\
                    \\textbf{Object ID} & [objectId] \\\\                
                    \\textbf{Institution} & [institution] \\\\
                    \\textbf{Name object} & [objectName] \\\\
                    \\textbf{Artist} & [artist] \\\\
                    \\textbf{Date} & [objectDate] \\\\
                    \\textbf{Techniques} & [techniques] \\\\                                    
                    \\textbf{MFT group} & [MFTgroup] \\\\
                    \\textbf{MFT spot} & [spot_description] \\\\
                    \\textbf{Materials} & [spot_materials] \\\\
                    \\textbf{BWSE} & [BWSE] \\\\
                    & \\\\
                    \\textbf{MFT device} & [device] \\\\
                    \\textbf{MFT lamp} & [lamp] \\\\
                    \\textbf{MFT spot size} & [spotSize] \\\\
                    \\textbf{Illuminance} & [ill] \\\\
                    \\textbf{Irradiance} & [irr] \\\\
                    \\textbf{Exposure dose} & [Hv] \\\\
                    \\textbf{Radiant energy} & [He] \\\\
                    \\textbf{Duration} & [duration] \\\\                 
                """

                
                # define the mapping table
                mapping_table_object = {
                    '[analysisId]': id,
                    '[analysisDate]': str(metadata['datetime_analysis']),
                    '[objectId]': metadata['object_id'],                
                    '[institution]': metadata['institution'],
                    '[objectName]': metadata['object_name'], 
                    '[artist]' : metadata['object_creator'],   
                    '[objectDate]': str(metadata['object_date']),
                    '[techniques]' : metadata['object_technique'].replace('_','-'),
                    '[spot_materials]': spot_materials,
                    '[NbAnalyses]': str(metadata['measurements_N']),  
                    '[MFTgroup]': metadata['spot_group'], 
                    '[ill]': f'{metadata["illuminance_Ev_Mlx"]} Mlx',
                    '[irr]': f'{metadata["irradiance_Ee_W/m^2"]} W/m2',
                    '[Hv]': f'{metadata["exposureDose_Hv_Mlxh"]} Mlxh',
                    '[He]': f'{metadata["radiantExposure_He_MJ/m^2"]} MJ/m2',
                    '[duration]': f'{np.int32(metadata["duration_min"])} min', 
                    '[device]' : metadata['device'].replace('_','-'),
                    '[lamp]': metadata['lamp_fading'].replace('_','-'),
                    '[spot_description]': metadata['spot_description'],      
                    '[spotSize]': f'{metadata["FWHM_micron"]} microns',
                    '[BWSE]': BWSE,
                    }
                #print(mapping_table_object).values()
                for x in mapping_table_object.keys():                                 
                    info_object = info_object.replace(x, mapping_table_object[x])            
                

                table_data = {'info_object': info_object}
                
                figure_paths = {
                    'figure1': folder_figures / figure1,
                    'figure2': im_combined_path,                                 
                }

                with open(Path(__file__).parent / 'report_templates' / 'MFT_report_single.tex', 'r') as template_file:
                    template = template_file.read()

                # Fill in placeholders with actual values
                filled_template = template.replace('[PROJECTID]',metadata['project_id'])
                filled_template = filled_template.replace('[ANALYSISID]', id)
                filled_template = filled_template.replace('[INSTITUTION]', host_institution_name)
                #filled_template = filled_template.replace('[DEPARTMENT]', host_institution_department)
                filled_template = filled_template.replace('[YOURNAME]', authors)
                filled_template = filled_template.replace('[TABLE1DATA]', table_data['info_object'])            
                filled_template = filled_template.replace('[FIGURE1PATH]', str(figure_paths['figure1']))
                filled_template = filled_template.replace('[FIGURE2PATH]', str(figure_paths['figure2']))                
                

                # Write filled template to .tex file
                with open('temp_report.tex', 'w') as temp_file:
                    temp_file.write(filled_template)

                # Compile .tex file into PDF
                subprocess.run(['pdflatex', 'temp_report.tex'])

                # Move generated PDF to output file                
                subprocess.run(['mv', 'temp_report.pdf', f'{folder_report}/{metadata["project_id"]}_MFT_rapport-analysis_{id}.pdf'])

                # Clean up temporary .tex and auxiliary files
                subprocess.run(['rm', 'temp_report.tex', 'temp_report.aux', 'temp_report.log'])

        
        if type == 'object':

            object_ids = sorted(set(list(self.get_metadata('object_id').values)))
            metadata = self.get_metadata()
            
            
            for object_id in object_ids:

                                
                figure_spots = [f'{folder_figures}/{file}' for file in all_figure_files if object_id in file and 'MFT-spots' in file][0]                
                figure_dE = [f'{folder_figures}/{file}' for file in all_figure_files if f'{object_id}' in file and 'dE-curves-report' in file][0]
                figure_SW = [f'{folder_figures}/{file}' for file in all_figure_files if f'{object_id}' in file and 'SW-rect-report' in file][0]

                
                metadata_object = metadata.loc[:, metadata.loc['object_id'] == object_id]
                project_id = list(set(metadata.loc['project_id'].values))[0]

                if authors == 'default':
                    authors = metadata['authors'].replace('_','-')

                host_institution = metadata.loc['host_institution'][0]
                if "_" in host_institution:
                    host_institution = host_institution.split('_')[0]

                info_object = """
                    \\textbf{Object ID} & [objectId] \\\\                
                    \\textbf{Institution} & [institution] \\\\
                    \\textbf{Object name} & [objectName] \\\\
                    \\textbf{Artist} & [artist] \\\\
                    \\textbf{Date} & [objectDate] \\\\
                    \\textbf{Techniques} & [technique] \\\\
                    \\textbf{Materials} & [objectMaterial] \\\\
                    & \\\\
                    \\textbf{N\\textsuperscript{o} MFT analyses} & [NbAnalyses] \\\\
                    \\textbf{N\\textsuperscript{o} MFT groups} & [NbGroups] \\\\
                    \\textbf{Illuminance} & [ill] \\\\
                    \\textbf{Exposure dose} & [Hv] \\\\
                    \\textbf{Duration} & [duration] \\\\                 
                """

                
                BWSE = """                
                    [nb01] & [BWSE01] \\\\
                    [nb02]  & [BWSE02] \\\\  
                    [nb03] & [BWSE03] \\\\                                   
                """
                
                nb_analyses = str(metadata_object.shape[1])
                nb_groups = str(len(set(metadata_object.loc['spot_group'].values)))
                ill = np.round(np.mean(metadata_object.loc['illuminance_Ev_Mlx'].values),2)
                Hv = np.round(np.mean(metadata_object.loc['exposureDose_Hv_Mlxh'].values),2)

                object_materials = list(set(metadata.loc['object_material'].values))[0]
                if "_" in object_materials:
                    object_materials = object_materials.replace("_",', ')

                object_technique = list(set(metadata.loc['object_technique'].values))[0]
                if "_" in object_technique:
                    object_technique = object_technique.replace("_",', ')

                # define the mapping table
                mapping_table_object = {
                    '[objectId]': object_id,                
                    '[institution]': list(set(metadata.loc['institution'].values))[0],
                    '[objectName]': list(set(metadata.loc['object_name'].values))[0], 
                    '[artist]' : list(set(metadata.loc['object_creator'].values))[0],   
                    '[objectDate]': list(set(metadata.loc['object_date'].values))[0],
                    '[technique]' : object_technique,
                    '[objectMaterial]': object_materials,
                    '[NbAnalyses]': nb_analyses,  
                    '[NbGroups]': nb_groups, 
                    '[ill]': f'{ill} Mlx (Avg)',
                    '[Hv]': f'{Hv} Mlxh (Avg)',
                    '[duration]': '20 min' # f'{(metadata.loc["duration_min"].values)} min',            
                    }           
                
            
                for x in mapping_table_object.keys():
                    info_object = info_object.replace(x, mapping_table_object[x])    

            
                table_data = {'info_object': info_object, 'BWSE': BWSE}


                figure_paths = {
                    'figure1': folder_figures / figure_spots,
                    'figure2': folder_figures / figure_dE,
                    'figure3': folder_figures / figure_SW,                                 
                }

                BWSE = metadata_object.loc['BWSE'].values                
                simplified_BWSE = []

                for i in BWSE:
                    i = float(i)
                    
                    if i >0.8 and i<=1.2:
                        new_i = '1'
                    if i >1.2 and i<=1.8:
                        new_i = '1-2'
                    if i >1.8 and i<=2.2:
                        new_i = '2'
                    if i >2.2 and i<=2.8:
                        new_i = '2-3'
                    if i >2.8 and i<=3.2:
                        new_i = '3'
                    if i >3.2 and i<=3.8:
                        new_i = '3'
                    if i >3.8 and i<=4.2:
                        new_i = '4'
                    if i >4.2 and i<=4.8:
                        new_i = '4-5'
                    if i >0.8 and i<=1.2:
                        new_i = '1'
                    if i >5.2 and i<=5.8:
                        new_i = '5-6'
                    if i >5.8 and i<=6.2:
                        new_i = '6'
                    if i >6.2 and i<=6.8:
                        new_i = '6-7'
                    if i >6.8 and i<=7.2:
                        new_i = '7'
                    
                    if math.isnan(i):
                        pass
                    else:
                        simplified_BWSE.append(new_i)

                
                nb_MFT = [x.split('.')[2] for x in metadata_object.loc['meas_id'].values]
                
                df = pd.DataFrame(data={
                    #'Description':group_description,
                    #'Groups': group,
                    'MFT': nb_MFT,
                    'BWSE': simplified_BWSE,
                })

                table_data2 = generate_latex_table(df)              
                

                with open(Path(__file__).parent / 'report_templates' / 'MFT_report_object.tex', 'r') as template_file:
                    template = template_file.read()

                # Fill in placeholders with actual values
                filled_template = template.replace('[PROJECTID]',project_id)
                filled_template = filled_template.replace('[OBJECTID]', object_id)
                filled_template = filled_template.replace('[HOST_INSTITUTION]', host_institution)
                filled_template = filled_template.replace('[YOURNAME]', authors)
                filled_template = filled_template.replace('[TABLE1DATA]', table_data['info_object'])  
                filled_template = filled_template.replace('% TABLE_DATA2', table_data2)      
                filled_template = filled_template.replace('[FIGURE1PATH]', str(figure_paths['figure1']))
                filled_template = filled_template.replace('[FIGURE2PATH]', str(figure_paths['figure2'])) 
                filled_template = filled_template.replace('[FIGURE3PATH]', str(figure_paths['figure3'])) 
                


                # Write filled template to .tex file
                with open('temp_report.tex', 'w') as temp_file:
                    temp_file.write(filled_template)

                # Compile .tex file into PDF
                subprocess.run(['pdflatex', 'temp_report.tex'])

                # Move generated PDF to output file                
                subprocess.run(['mv', 'temp_report.pdf', f'{folder_report}/{project_id}_MFT_rapport-object_{object_id}.pdf'])

                # Clean up temporary .tex and auxiliary files
                subprocess.run(['rm', 'temp_report.tex', 'temp_report.aux', 'temp_report.log'])
                
        
        
        if type == 'project':

            all_metadata = self.get_metadata()
            project_ids = all_metadata.loc['project_id'].values
            db_name = config.get_config_info()['databases']['db_name']
            db =  msdb.DB(db_name)
            db_projects = db.get_projects().set_index('project_id')
            db_users = db.get_users().set_index('initials')



            for project_id in sorted(set(project_ids)):

                metadata = all_metadata.loc[:,all_metadata.loc['project_id'] == project_id]
                project_info = db_projects.loc[project_id]

                project_leader_initials = project_info['project_leader']
                project_leader_info = db_users.loc[project_leader_initials]
                project_leader_name = ' '.join(project_leader_info[['name','surname']].values)

                start_date = project_info['start_date']

                institution = project_info['institution']
                
                host_institution = metadata.loc['host_institution'].values[0]
                if "_" in host_institution:
                    host_institution = host_institution.split('_')[0]
                
                
                keywords = project_info['keywords']

                methods = project_info['methods']
                if "_" in methods:
                    methods = methods.replace('_','-')

                device = sorted(set(metadata.loc['device'].values))[0]
                if "_" in device:
                    device = device.replace('_', '-')

                lamp = sorted(set(metadata.loc['lamp_fading'].values))[0]
                if "_" in lamp:
                    lamp = lamp.replace('_', '-')
                nb_analyses = str(metadata.shape[1])
                nb_objects = str(len(sorted(set(metadata.loc['object_id'].values))))

                

                figure_BWSE_hist = [f'{folder_figures}/{file}' for file in all_figure_files if project_id in file and 'BWSE-hist-report' in file][0]                
                figure_BWSE_bars = [f'{folder_figures}/{file}' for file in all_figure_files if project_id in file and 'BWSE-bars-report' in file]

                if len(figure_BWSE_hist) == 0:
                    print(f'The BWSE histogram figure cannot be found in the folder {folder_figures}.')
                    print(f'Make sure that the filename of the BWSE histogram figure contains the project ID ({project_id}) and the expression "BWSE-hist-report".')
                    return

                
                if len(figure_BWSE_bars) == 0:
                    print(f'The BWSE bars figure cannot be found in the folder {folder_figures}.')
                    print(f'Make sure that the filename of the BWSE bars figures contain the project ID ({project_id}) and the expression "BWSE-bars-report".')
                    return
                
                elif len(figure_BWSE_bars) == 1:
                    figure_BWSE_bars_01 = figure_BWSE_bars[0]
                
                elif len(figure_BWSE_bars) == 2:
                    figure_BWSE_bars_01 = figure_BWSE_bars[0]
                    figure_BWSE_bars_02 = figure_BWSE_bars[1]



                info_project = """
                    \\textbf{Project id} & [projectId] \\\\
                    \\textbf{Project leader} & [projectLeader] \\\\
                    \\textbf{Institution} & [institution] \\\\   
                    \\textbf{Start date} & [startDate] \\\\             
                    \\textbf{Keywords} & [keywords] \\\\
                    & \\\\
                    \\textbf{MFT device} & [MFTdevice] \\\\
                    \\textbf{MFT lamp} & [MFTlamp] \\\\
                    \\textbf{N\\textsuperscript{o} of analyses} & [NbAnalyses] \\\\
                    \\textbf{N\\textsuperscript{o} of objects} & [NbObjects] \\\\ 
                """
                info_analysis = """
                    \\textbf{MFT device} & [MFTdevice] \\\\
                    \\textbf{N\\textsuperscript{o} of analyses} & [NbAnalyses] \\\\
                    \\textbf{N\\textsuperscript{o} of objects} & [NbObjects] \\\\                
                """

                # define the mapping table
                mapping_table_project = {
                    '[projectId]': project_id,
                    '[projectLeader]': project_leader_name,
                    '[institution]': institution,                
                    '[keywords]' : keywords,  
                    '[methods]' : methods, 
                    '[startDate]' : start_date,
                    '[MFTdevice]': device,
                    '[MFTlamp]' : lamp,
                    '[NbAnalyses]': nb_analyses,
                    '[NbObjects]': nb_objects,             
                    }
                
                
                mapping_table_analyses = {
                    '[MFTdevice]': device,
                    '[NbAnalyses]': nb_analyses,
                    '[NbObjects]': nb_objects,                                
                    }

                
                
                for x in mapping_table_project.keys():
                    info_project = info_project.replace(x, mapping_table_project[x])    

                for x in mapping_table_analyses.keys():
                    info_analysis = info_analysis.replace(x, mapping_table_analyses[x])         
                

                table_data = {'info_project': info_project, 'info_analysis': info_analysis}

                if len(figure_BWSE_bars) == 1: 
                    figure_blank_square = Path(__file__).parent / 'blank_rectangle.png'             
                    figure_paths = {
                        'figure1': figure_BWSE_hist,
                        'figure2': figure_BWSE_bars_01,
                        'figure3': figure_blank_square                    
                    }

                else: 
                    figure_paths = {
                        'figure1': figure_BWSE_hist,
                        'figure2': figure_BWSE_bars_01,  
                        'figure3': figure_BWSE_bars_02,                  
                    }
                

                with open(Path(__file__).parent / 'report_templates' / 'MFT_report_project.tex', 'r') as template_file:
                    template = template_file.read()

                # Fill in placeholders with actual values
                filled_template = template.replace('[PROJECTID]', project_id)
                filled_template = filled_template.replace('[INSTITUTION]', host_institution)
                filled_template = filled_template.replace('[YOURNAME]', authors)
                filled_template = filled_template.replace('[TABLE1DATA]', table_data['info_project'])                
                filled_template = filled_template.replace('[FIGURE1PATH]', str(figure_paths['figure1']))
                filled_template = filled_template.replace('[FIGURE2PATH]', str(figure_paths['figure2']))
                filled_template = filled_template.replace('[FIGURE3PATH]', str(figure_paths['figure3']))

                

                if len(figure_BWSE_bars) == 2:                
                    filled_template = filled_template.replace('[FIGURE3PATH]', str(figure_paths['figure3']))

                # Write filled template to .tex file
                with open('temp_report.tex', 'w') as temp_file:
                    temp_file.write(filled_template)

                # Compile .tex file into PDF
                subprocess.run(['pdflatex', 'temp_report.tex'])

                # Move generated PDF to output file                
                subprocess.run(['mv', 'temp_report.pdf', f'{folder_report}/{project_id}_MFT_rapport-project.pdf'])                

                # Clean up temporary .tex and auxiliary files
                subprocess.run(['rm', 'temp_report.tex', 'temp_report.aux', 'temp_report.log'])       


    def make_table(self, parameters:Optional[list] = ['BWSE'], sort_by:Optional[str] = 'meas_id', title:Optional[str] = None, subtitle:Optional[str] = None):
        """Create a table showing values from the 'info' sheets.

        Parameters
        ----------
        parameters : Optional[list], optional
            Select which parameters of the info sheet to display, by default ['BWSE']

        sort_by : Optional[str], optional
            Select the parameters on which to sort the rows of the table, by default 'meas_id'

        title : Optional[str], optional
            Whether to add a title above the table, by default None

        subtitle : Optional[str], optional
            Whether to add a subtitle below the title, by default None

        Returns
        -------
        _type_
            _description_
        """

        wanted_parameters = ['meas_id'] + parameters

        df_info = self.get_metadata(wanted_parameters).T.sort_values(by=[sort_by])
                
        my_table = (
        GT(df_info)
        .tab_header(
            title=title,
            subtitle=subtitle,            
        )
        .tab_style(
            style=style.text(weight='bold', size='18px'),
            locations=loc.column_header(),
        ) 
        .cols_align(align='center')      
        )

        return my_table
    
    
    def read_files(self, sheets:Union[list,str] = ['info', 'CIELAB', 'spectra']):
        """Read the data files given as argument when defining the instance of the MFT class.

        Parameters
        ----------
        sheets : Union[list,str], optional
            Name of the excel sheets to be selected, by default ['info', 'CIELAB', 'spectra']
            If you just want to retrieve a single sheet, you can enter it as a string, e.g: 'CIELAB'. Other enter the name of the sheets inside a list.

        Returns
        -------
        A list of list of pandas dataframes
            The content of each input data file is returned as a list pandas dataframes (3 dataframes maximum, one dataframe per sheet). Ultimately, the function returns a list of list, so that when there are several input data files, each list - related a single file - corresponds to a single element of a list.            
        """
        
        files = []  

        if isinstance(sheets, str):
            sheets = [sheets]      
                
        for file in self.files:
            
            df_info = pd.read_excel(file, sheet_name='info')
            df_sp = pd.read_excel(file, sheet_name='spectra', header=[0,1], index_col=0)
            df_cl = pd.read_excel(file, sheet_name='CIELAB', header=[0,1])                      


            if sheets == ['info', 'CIELAB', 'spectra']:
                files.append([df_info, df_cl, df_sp])

            elif sheets == ['info']:
                files.append([df_info])

            elif sheets == ['CIELAB']:
                files.append([df_cl])

            elif sheets == ['spectra']:
                files.append([df_sp])

            elif sheets == ['spectra', 'CIELAB']:
                files.append([df_sp, df_cl])

            elif sheets == ['CIELAB','spectra']:
                files.append([df_cl, df_sp])

            elif sheets == ['info','CIELAB']:
                files.append([df_info, df_cl])

            elif sheets == ['info','spectra']:
                files.append([df_info, df_sp])

        return files
                

    