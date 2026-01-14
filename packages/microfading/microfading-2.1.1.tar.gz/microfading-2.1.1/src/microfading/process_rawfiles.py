import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
import colour
from math import pi
from pathlib import Path
from typing import Optional, Union
from scipy import ndimage
import scipy.interpolate as sip
from scipy.interpolate import RegularGridInterpolator
from io import StringIO
from datetime import date, datetime
import imageio
import msdb
import h5py
import locale

from . import config
from . import MFT_info_dictionaries
from . import MFT_info_templates


def parse_datetime(date_string, language):

    try:
        locale.setlocale(locale.LC_TIME, language)

        # Parse the date string according to the locale
        parsed_datetime = datetime.strptime(date_string, '%a %b %d %H:%M:%S %Y')
        parsed_datetime = pd.to_datetime(parsed_datetime.strftime('%Y-%m-%d %H:%M:%S'))

        return parsed_datetime, parsed_datetime.date()
    
    except ValueError as e:
        parsed_datetime = date_string.split(' ')
        parsed_datetime_string = f'{parsed_datetime[-1]}-{parsed_datetime[1]}-{parsed_datetime[-3]} {parsed_datetime[-2]}'

        print('The algorithm is not able to process the date time correctly. Please set the parameter "language" of the function "process_rawdata" according to the language used in the Fotonowy raw file to register the date time info.')
        return parsed_datetime_string, f'{parsed_datetime[-1]}-{parsed_datetime[1]}-{parsed_datetime[-3]}' 


def MFT_fotonowy(files: list, filenaming:Optional[str] = 'none', folder_output:Optional[str] = '.', db:Optional[bool] = False, comment:Optional[str] = '', device_nb:Optional[str] = 'none', authors:Optional[str] = 'XX', white_standard:Optional[bool] = 'default', rounding:Optional[int] = None, interpolation:Optional[bool] = True, dose_unit:Optional[str] = 'He', step:Optional[float | int] = 0.1, average:Optional[int] = 'undefined', observer:Optional[str] = 'default', illuminant:Optional[str] = 'default', background:Optional[str] = 'black', language:Optional[str] = None, output_format:Optional[str] = 'excel', delete_files:Optional[bool] = True, return_filename:Optional[bool] = True):
    """Process the microfading rawdata obtained from the Fotonowy device.

    Parameters
    ----------
    files : list of strings
        Path of the microfading rawdata files
    
    filenaming : Optional[str], optional
        _description_, by default 'none'
    
    folder_output : Optional[str], optional
        Path of the folder to save the output file, by default '.'
    
    db : Optional[bool], optional
        Whether to make use of the info registered in the database files, by default False
    
    comment : Optional[str], optional
        Whether to insert a comment about the microfading analyses, by default ''
    
    device_nb : Optional[str], optional
        ID number of the microfading, by default 'default'
    
    authors : Optional[str], optional
        Person(s) that performed the analyses, by default 'XX'
    
    white_standard : Optional[bool], optional
        ID number of the white standard reference used to perform the microfading analyses, by default 'default'
        When 'default', it will search for the registered values in the config_info.json file. If you have not registered any values, it assumes that you used the Fotolon provided by Fotonowy.
    
    rounding : Optional[int, tuple], optional
        Rounding the spectral and colorimetric coordinates, by default (4,3)
        It represents the number of digits after the comma
        When an integer is provided, it is applied to both the spectral and colorimetric value
        When a tuple is provided, the first value relates to the spectral values while the second relates to the colorimetric values

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
    
    step : Optional[float  |  int], optional
        Interpolation step related to the scale previously mentioned ('He', 'Hv', 't'), by default 0.1
    
    average : Optional[int], optional
        Average of the measurements, by default 'undefined'
        If you use always the same average value, you can save it up in the config_info.json file (use the set_devices_info() function). Then enter 'default' as  value for the average parameter in order to retrieve the average value savied in the config file.
    
    observer : str, optional
        Reference CIE *observer* in degree ('10deg' or '2deg'). by default 'default'.
        When 'default', it fetches the observer value recorded in the db_config.json file of the package. If no value has been recorded, then it sets the observer value to '10deg'. 

    illuminant : (str, optional)  
        Reference CIE *illuminant*. It can be any value of the following list: ['A', 'B', 'C', 'D50', 'D55', 'D60', 'D65', 'D75', 'E', 'FL1', 'FL2', 'FL3', 'FL4', 'FL5', 'FL6', 'FL7', 'FL8', 'FL9', 'FL10', 'FL11', 'FL12', 'FL3.1', 'FL3.2', 'FL3.3', 'FL3.4', 'FL3.5', 'FL3.6', 'FL3.7', 'FL3.8', 'FL3.9', 'FL3.10', 'FL3.11', 'FL3.12', 'FL3.13', 'FL3.14', 'FL3.15', 'HP1', 'HP2', 'HP3', 'HP4', 'HP5', 'LED-B1', 'LED-B2', 'LED-B3', 'LED-B4', 'LED-B5', 'LED-BH1', 'LED-RGB1', 'LED-V1', 'LED-V2', 'ID65', 'ID50']. by default 'default'.
        When 'default', it fetches the illuminant value recorded in the db_config.json file of the package. If no value has been recorded, then it sets the illuminant value to 'D65'.
    
    background : Optional[str], optional
        The background under the object, by default 'black'

    language : Optional[str], optional
        The language of the computer used to perform the microfading analyses, by default None
        When None, English is assumed to be the language that was used.
        If you are working on a Windows computer, you can use of the following languages (non-exhaustive list) : 'en', 'fr', 'it', 'nl', 'de', 'es'.
        If you are working on a Linux OS, open a terminal, enter " locale -a ", and choose one language among the returned list.
        For more information, consult the online documentation (https://g-patin.github.io/microfading/language-setting/).
    
    output_format : str, optional
        Output file format for the interim files, by default 'xlsx'.
        By default, the interim files will be saved as '.xlxs' (excel). When 'ods', it will save the output files as '.ods', which is the open source version of excel.
    
    delete_files : Optional[bool], optional
        Whether to delete the raw files, by default True
    
    return_filename : Optional[bool], optional
        Whether to return the filename of the created excel file that contains the microfading data and metadata, by default True

    Returns
    -------
    str
        _description_
    """

            
    # check whether the objects and projects databases have been created    
    if db:  
        databases_info = config.get_config_info()['databases']

        if len(databases_info) == 0:
            return 'The databases have not been created or registered. To register the databases, use the function set_DB(). To create the databases files use the function create_DB(). For more information about databases, consult the online documentation: https://g-patin.github.io/microfading/'
        
        else:   
            db_name = config.get_config_info()['databases']['db_name']
            databases = msdb.DB(db_name)  
            db_projects = databases.get_projects()
            db_objects = databases.get_objects()
    
    else:
        filenaming = 'none'
   
    
    # define observer and illuminant values used for the colorimetric calculations
    observers = {        
        '10deg': 'cie_10_1964',
        '2deg' : 'cie_2_1931',
    }
    
    cmfs_observers = {
        '10deg': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1964 10 Degree Standard Observer"],
        '2deg': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1931 2 Degree Standard Observer"] 
    }

    if illuminant == 'default':
        if isinstance(databases.get_colorimetry_info(), str):
            illuminant = 'D65'
        else:
            illuminant = databases.get_colorimetry_info().loc['illuminant']['value']

    if observer == 'default':
        if isinstance(databases.get_colorimetry_info(), str):
            observer = '10deg'
        else:
            observer = databases.get_colorimetry_info().loc['observer']['value']

    illuminant_SDS = colour.SDS_ILLUMINANTS[illuminant]
    illuminant_CCS = colour.CCS_ILLUMINANTS[observers[observer]][illuminant]
    cmfs = cmfs_observers[observer]
    
    
    # rounding values for spectral and colorimetric values
    if isinstance(rounding, int):
        rounding_sp = rounding
        rounding_cl = rounding

    elif isinstance(rounding, (tuple,list)):
        rounding_sp = rounding[0]
        rounding_cl = rounding[1]

    
    # wanted wavelength range
    wanted_wl = pd.Index(np.arange(380,781), name='wavelength_nm')
    
    
    # retrieve counts spectral files to be processed
    raw_files_counts = [Path(file) for file in files if 'spect_convert.txt' in Path(file).name]    
     
    # process each spectral file
    for raw_file_counts in raw_files_counts:

                
        # retrieve the corresponding colorimetric file
        raw_file_cl = Path(str(raw_file_counts).replace('-spect_convert.txt', '.txt'))
        stemName = raw_file_cl.stem.replace(" ", "_")                                 

        # upload raw files into dataframes
        raw_df_counts = pd.read_csv(raw_file_counts, sep='\t', skiprows = 1)
        raw_df_cl = pd.read_csv(raw_file_cl, sep='\t', skiprows = 8)        

        # round up the first and last wavelength values
        raw_df_counts.rename(index={380.024:380},inplace=True)
        raw_df_counts.rename(index={779.910:780},inplace=True)

        # select white and dark spectral references (first and second columns respectively)
        white_ref = raw_df_counts.iloc[:,0].values
        dark_ref = raw_df_counts.iloc[:,1].values
        
        # remove the white and dark ref        
        df_counts = raw_df_counts.iloc[:,2:-1]  
        df_counts.columns = raw_df_counts.columns[3:] 

        # rename the index column
        df_counts.index.name = 'wavelength_nm'               

        # create an empty dataframe for the spectral reflectance values        
        raw_df_sp = pd.DataFrame(index=raw_df_counts.index)
        raw_df_sp.index.name = 'wavelength_nm'        

        # drop the before last column of df_counts
        df_counts = df_counts.drop(df_counts.iloc[:,-2].name,axis=1)
        
        # compute the reflectance values
        for col in df_counts.columns:  
            counts = df_counts[col].values
            sp = pd.Series(counts / white_ref, index=df_counts.index, name=col[15:])
            raw_df_sp = pd.concat([raw_df_sp,sp], axis=1)   
                
        # retrieve the times and energy values        
        times = raw_df_cl['#Time']
        interval_sec = int(np.round(times.values[3] - times.values[2],0))
        numDataPoints = len(times)        
        duration_min = np.round(times.values[-1] / 60, 2)
        He = raw_df_cl['Watts']       # radiant exposure values in MJ/m²
        Hv = raw_df_cl['Lux']         # exposure dose values in Mlxh
        total_He = He.values[-1]
        total_Hv = Hv.values[-1]
        ill = (60 * total_Hv) / (times.values[-1]/60)
        irr = (total_He*1e6) / times.values[-1]
        
        
        # interpolate the data
        if interpolation == False:   
            df_sp = np.round(raw_df_sp, rounding_sp)
            df_sp.columns = [float(col[:-3]) for col in df_sp.columns]


            df_cl = np.round(raw_df_cl, rounding_cl)
            df_cl = df_cl[['Watts', 'Lux', '#Time', 'L','a','b','dE76','dE2000']]
            df_cl.columns = ['He_MJ/m2', 'Hv_Mlxh','t_sec', 'L*', 'a*','b*', 'dE76', 'dE00']  

            LCh = np.round(colour.Lab_to_LCHab(df_cl[['L*','a*','b*']].values).T,3)

            df_cl['C*'] = LCh[1]
            df_cl['h'] = LCh[2]

            df_cl = df_cl[['He_MJ/m2', 'Hv_Mlxh','t_sec', 'L*','a*','b*','C*','h','dE76','dE00']]
                          
        else:
            # define abscissa units
            abs_scales = {'He': He, 'Hv': Hv, 't': times}
            abs_scales_name = {'He': 'He_MJ/m2', 'Hv': 'Hv_Mlxh', 't': 't_sec'}           

            #  define the abscissa range according to the choosen step value
            wanted_x = np.arange(0, abs_scales[dose_unit].values[-1], step)            
                          
            # create a dataframe for the energy and time on the abscissa axis        
            df_abs = pd.DataFrame({'t_sec':times, 'He_MJ/m2': He,'Hv_Mlxh': Hv})
            df_abs = df_abs.set_index(abs_scales_name[dose_unit])

            # create an interp1d function for each column of df_abs
            abs_interp_functions = [sip.interp1d(df_abs.index, df_abs[col], kind='linear', fill_value='extrapolate') for col in df_abs.columns]            

            # interpolate all columns of df_abs simultaneously
            interpolated_abs_data = np.round(np.vstack([f(wanted_x) for f in abs_interp_functions]).T, 4)
            
            # Create a new DataFrame with the interpolated data
            interpolated_df = pd.DataFrame(interpolated_abs_data, index=wanted_x, columns=df_abs.columns)

            interpolated_df.index.name = abs_scales_name[dose_unit]
            interpolated_df = interpolated_df.reset_index()

            # insert a row at the top with the word 'nominal' as input
            df_value = pd.DataFrame({'He_MJ/m2':'nominal','t_sec':'nominal','Hv_Mlxh':'nominal'}, index=['nominal'])
            interpolated_df = pd.concat([df_value, interpolated_df])
            interpolated_df = interpolated_df.reset_index().drop('index', axis=1)          
            
            # modify the columns names according to the choosen abscissa unit
            raw_df_sp.columns = abs_scales[dose_unit]
            
            # interpolate the reflectance values according to the wavelength and the abscissa range
            interp = RegularGridInterpolator((raw_df_sp.index,raw_df_sp.columns), raw_df_sp.values)

            pw, px = np.meshgrid(wanted_wl, wanted_x, indexing='ij')     
            interp_data = interp((pw, px))    
            df_sp_interp = pd.DataFrame(np.round(interp_data, rounding_sp), index=wanted_wl, columns=wanted_x)
                   

            # empty list to store XYZ values
            XYZ = []

            # calculate the LabCh values
            for col in df_sp_interp.columns:
                sd = colour.SpectralDistribution(df_sp_interp[col], wanted_wl)
                XYZ.append(colour.sd_to_XYZ(sd, cmfs, illuminant=illuminant_SDS))        

            XYZ = np.array(XYZ)

            Lab = np.array([colour.XYZ_to_Lab(d / 100, illuminant_CCS) for d in XYZ])
            LCh = np.array([colour.Lab_to_LCHab(d) for d in Lab])
                    
            L = ['nominal']
            a = ['nominal']
            b = ['nominal']
            C = ['nominal']
            h = ['nominal']

            [L.append(np.round(i[0], rounding_cl)) for i in Lab]
            [a.append(np.round(i[1], rounding_cl)) for i in Lab]
            [b.append(np.round(i[2], rounding_cl)) for i in Lab]
            [C.append(np.round(i[1], rounding_cl)) for i in LCh]
            [h.append(np.round(i[2], rounding_cl)) for i in LCh]

                
            # compute the delta E values
            dE76 = ['nominal'] + list(np.round(np.array([colour.delta_E(Lab[0], d, method="CIE 1976") for d in Lab]), rounding_cl))
            dE00 = ['nominal'] + list(np.round(np.array([colour.delta_E(Lab[0], d) for d in Lab]), rounding_cl))

            # calculate dR_VIS and dR
            dR_vis = ['nominal']                                    # empty list to store the dRvis values                                   
            df_sp_vis = df_sp_interp.loc[400:740]                   # reflectance spectra in the visible range
            sp_initial = (df_sp_vis.iloc[:,0].values) * 100         # initial spectrum
        
            for col in df_sp_vis.columns:
                sp = df_sp_vis[col]
                dR_val = np.sum(np.absolute(sp*100-sp_initial)) / len(sp_initial)           
                dR_vis.append(np.round(dR_val, rounding_cl))      
                        
            # create the colorimetric dataframe
            df_cl = pd.DataFrame({'L*': L,
                                'a*': a,
                                'b*': b,
                                'C*': C,
                                'h': h,
                                'dE76': dE76,
                                'dE00': dE00,
                                'dR_vis': dR_vis
                                })                
            
            # concatenate the energy values with df_cl
            df_cl = pd.concat([interpolated_df,df_cl], axis=1, ignore_index=False)
                        
            # add a new row 'nominal' at the top which
            df_value = pd.DataFrame(df_sp_interp.shape[1] * ['nominal'], columns=['data_type']).T
            df_value.index.name = 'wavelength_nm'            
            df_value.columns = df_sp_interp.columns
            df_sp_interp = pd.concat([df_value, df_sp_interp]) 
            
            # name the columns
            df_sp_interp.columns.name = abs_scales_name[dose_unit]  
            
            # rename spectral dataframe
            df_sp = df_sp_interp
            
        
        ###### CREATE INFO DATAFRAME ####### 

        # retrieve the information about the analysis        
        lookfor = '#Time'
        file_raw_cl = open(raw_file_cl).read()

        infos = file_raw_cl[:file_raw_cl.index(lookfor)].splitlines()
        dic_infos = {}

        for i in infos:             
            key = i[2:i.index(':')]
            value = i[i.index(':')+2:]              
            dic_infos[key]=[value]

        dic_infos.pop('Illuminant') # remove the Illuminant info
        dic_infos['meas_id'] = f'{dic_infos["Object"][0]}_{dic_infos["Sample"][0]}'
        df_info = pd.DataFrame.from_dict(dic_infos).T 

        # retrieve light info
        LED_nb = df_info.loc['LED'].values[0]
        LED_ID = f'LED{LED_nb}'
        LED_info = f'{LED_ID}_{MFT_info_dictionaries.LEDs_info[LED_nb]}'

        # retrieve light energy info
        current = int(df_info.loc['Curr'].values[0].split(' ')[0]) 
        fwhm = MFT_info_dictionaries.beam_FWHM[LED_nb]
        area = pi * (((fwhm/1e6)/2)**2)
        power = np.round((irr * area) * 1e3, 3)
        lum = np.round(area * (ill * 1e6),3)        
        
        # retrieve the integration times
        int_time_sample = int(df_info.loc['Sample integration time [ms]'].values[0])
        int_time_whitestandard = int(df_info.loc['White standard integration time [ms]'].values[0])

        # specular component info
        spec_comp = 'SCE_excluded'

        # retrieve the dates
        date_time_string = df_info.loc['Date'].values[0]

        try:
            date_time_analysis = pd.to_datetime(date_time_string)
            date = date_time_analysis.date()

        except ValueError:
            date_time_analysis,date = parse_datetime(date_string=date_time_string, language=language)

        date_time_processing = datetime.now()

        
        # retrieve the white standard info
        if db == False:
            if white_standard == 'default':
                white_standard_info = 'undefined'
            else:
                white_standard_info = white_standard
        else:            
            # Retrieve the white standard information
            df_WR = databases.get_white_standards()
            if white_standard in df_WR['ID'].values:
                df_WR = df_WR.set_index('ID')
                WR_nb = white_standard
                WR_description = df_WR.loc[white_standard]['description']
            elif white_standard == 'default':
                WR_nb = 'none'
                WR_description = 'Fotonowy fotolon PTFE'
            elif white_standard == 'unknown':
                WR_nb = 'none'
                WR_description = 'unknown'
            else:
                print(f'The white reference you entered ({white_standard}) has not been registered. Please, consult the online documentation for more information about registering information (https://g-patin.github.io/microfading/).')
                return
            white_standard_info = f'{WR_nb}_{WR_description}'
        
        # retrieve the institution info
        config_info = config.get_config_info()
        if len(config_info['institution']) > 0:
            institution_info = config.get_institution_info()['value']
            host_institution_name = institution_info['name']
            host_institution_department = institution_info['department']

            if len(host_institution_department) > 0:
                host_institution = f'{host_institution_name}_{host_institution_department}'
            else:
                host_institution = host_institution_name
        else:
            host_institution = 'undefined'
            print('You might want to register the info of your institution in the config_info.json file -> mf.set_institution_info().')

        
        # retrieve device ID info
        if db == False:
            if device_nb == 'none':
                device = 'Fotonowy'
            else:
                device = device_nb
        
        else:
            df_devices = databases.get_devices()
            if device_nb in df_devices['ID'].values:
                df_devices = df_devices.set_index('ID')                    
                device_name = df_devices.loc[device_nb]['name']
                device_description = df_devices.loc[device_nb]['description']

            elif device_nb == 'default' or device_nb.lower() == 'fotonowy':
                device_nb = 'none'
                device_name = 'unnamed'
                device_description = 'Fotonowy-MFT'

            else:
                print(f'The device you entered ({device_nb}) has not been registered. Please first register the device, by using the function mf.set_devices_info().')
                return
            
            device = f'{device_nb}_{device_name}_{device_description}'

        # device info
        device_info = [
            "",
            device, 
            'none',
            'none',
            'none',
            '0° : 45°',
            'unknown',
            'unknown',
            'none',
            'none',
            'Thorlabs, FT030',
            f'{LED_info}',
            'none',
            'none',
            'none',
            white_standard_info
        ]

        # results info
        results_info = ["", "ND", "ND"]
        
            
        if db == False: 

            info_parameters = MFT_info_templates.head_info + MFT_info_templates.device_info + MFT_info_templates.analysis_info + MFT_info_templates.spot_info + MFT_info_templates.beam_info + MFT_info_templates.results_info      

                        
            df_info.loc['numDataPoints'] = numDataPoints                
            
            # define meas_id
            meas_id = df_info.loc['meas_id'].values[0]        
            
            # define authors
            if authors == 'XX':
                authors = 'unknown'
            
            # head info
            head_info = [
                "SINGLE MICROFADING ANALYSIS",
                authors,
                host_institution,
                date_time_analysis,
                date_time_processing,
                comment,                
            ]
            
            
            # analysis info 
            analysis_info = [
                " ",
                meas_id,                
                spec_comp,
                int_time_sample,
                int_time_whitestandard,
                average, 
                int(duration_min), 
                interval_sec,
                1,
                illuminant,
                observer,
            ]
            
            # spot info         
            spot_info = [
                "",
                "ND",                 # group 
                "ND",                 # group_description
                "ND",                 # spot_color
                "ND",                 # spot_components
                "ND",                 # background
                "ND",                 # spot_image
                "ND",                 # other_analyses
            ]

            # beam info               
            beam_info = [
                "",
                'ND',
                'ND',
                fwhm,
                current,
                power,
                lum,
                int(irr),
                np.round(ill, 4),
                np.round(total_He, 3),
                np.round(total_Hv, 3),                   
            ]            
            
            info_values = head_info + device_info + analysis_info + spot_info + beam_info + results_info            
            

        else:
                
            if 'project_id' in db_objects.columns:
                db_objects = db_objects.drop('project_id', axis=1)
                
            info_parameters = MFT_info_templates.head_info + ["[PROJECT INFO]"] + list(db_projects.columns) + ["[OBJECT INFO]"] + list(db_objects.columns) + MFT_info_templates.device_info + MFT_info_templates.analysis_info + MFT_info_templates.spot_info + MFT_info_templates.beam_info + MFT_info_templates.results_info

            df_authors = databases.get_users()

            if authors == 'XX':
                authors_names = 'unknown'

            elif '-' in authors or ' - ' in authors:                     
                list_authors = []
                for x in authors.split('-'):
                    x = x.strip()
                    if x in df_authors['initials'].values:                        
                        df_author = df_authors[df_authors['initials'] == x]                    
                        list_authors.append(f"{df_author['surname'].values[0]}, {df_author['name'].values[0]}")   
                    else:
                        print(f'The user ("{x}") has not been registered in the database file.')
                        list_authors.append(x)                    
                authors_names = '_'.join(list_authors)
                    
            else: 
                if authors in df_authors['initials'].values:
                    df_author = df_authors[df_authors['initials'] == authors]
                    authors_names = f"{df_author['surname'].values[0]}, {df_author['name'].values[0]}"
                
                else:
                    print(f'The author name "{authors}" has not been registered in the databases. Please, consult the online documentation for more information about registering information (https://g-patin.github.io/microfading/).')
                    authors_names = authors
                     

            project_id = raw_file_cl.stem.split(' ')[0]
            object_id = raw_file_cl.stem.split(' ')[1]
            group = raw_file_cl.stem.split(' ')[2]
            group_description = raw_file_cl.stem.split(' ')[3].split('_')[0]            
            project_info = list(db_projects.query(f'project_id == "{project_id}"').values[0])
            object_info = list(db_objects.query(f'object_id == "{object_id}"').values[0])


            # Retrieve the device info values
            LED_nb = df_info.loc['LED'].values[0]
            LED_ID = f'LED{LED_nb}'
            df_LEDs = databases.get_lamps().set_index('ID')
            existing_LEDs = list(df_LEDs.index)

            if LED_ID in existing_LEDs:
                LED_description = df_LEDs.loc[LED_ID]['description']
                LED_info = f'{LED_ID}_{LED_description}'

            else:
                LED_info = LED_ID
                print(f'The LED_ID ({LED_ID}) related to your analysis is not present in the registered lamps ({existing_LEDs}). Please make sure to register it.')
                 
             
            # Retrieve the analysis info values
                
            meas_nb = raw_file_cl.stem.split('_')[1]
            meas_id = f'MF.{object_id}.{meas_nb}'                       
                              
                           
            analysis_info = [
                "",
                meas_id,                
                spec_comp,
                int_time_sample,
                int_time_whitestandard,
                average, 
                int(duration_min), 
                interval_sec,
                1,
                illuminant,
                observer,
            ]


            # spot info
            spot_image = "ND"
            other_analyses = "ND"
            spot_color = "ND"
            spot_components = "ND"

            spot_info = [
                "",
                group, 
                group_description,
                spot_color,
                spot_components,
                background,
                spot_image,
                other_analyses,
            ]


            # beam info               
            beam_info = [
                "",
                'ND',
                'ND',
                fwhm,
                current,
                power,
                lum,
                int(irr),
                np.round(ill, 3),
                np.round(df_cl['He_MJ/m2'].values[-1], 4),
                np.round(df_cl['Hv_Mlxh'].values[-1], 4),                   
            ]

            info_values = [
                "SINGLE MICROFADING ANALYSIS",
                authors_names,
                host_institution,
                date_time_analysis,
                date_time_processing,
                comment,
                " "] + project_info + [" "] + object_info + device_info + analysis_info + spot_info + beam_info + results_info

        df_info = pd.DataFrame({'parameter':info_parameters})
        df_info["value"] = pd.Series(info_values)            
            
        
        df_info = df_info.set_index('parameter')

        # define the output filename
        if filenaming == 'none':
            filename = stemName

        elif filenaming == 'auto':
            group = stemName.split('_')[2]
            group_description = stemName.split('_')[3]
            object_type = df_info.loc['object_type']['value']
            filename = f'{project_id}_{meas_id}_{group}_{group_description}_{object_type}_{date}'

        elif isinstance(filenaming, list):

            if 'date' in filenaming:
                new_df_info = df_info.copy()
                new_df_info.loc['date'] = str(date)              
                filename = "_".join([new_df_info.loc[x]['value'].split("_")[0] if "_" in new_df_info.loc[x]['value'] else new_df_info.loc[x]['value'] for x in filenaming])                    

            else:                                  
                filename = "_".join([df_info.loc[x]['value'].split("_")[0] if "_" in df_info.loc[x]['value'] else df_info.loc[x]['value'] for x in filenaming])
               
               
        # export the dataframes to an excel file
        if not Path(folder_output).exists():
            print(f'The output folder you entered {folder_output} does not exist. Please make sure the output folder has been created.')
            return 
            
        with pd.ExcelWriter(Path(folder_output) / f'{filename}.{output_format}') as writer:

            df_info.to_excel(writer, sheet_name='info', index=True)
            df_cl.to_excel(writer, sheet_name="CIELAB", index=False)

            if interpolation == 'none':
                df_sp.to_excel(writer, sheet_name="spectra", index=True, index_label=f'wl-nm_t-sec')

            else:
                df_sp.to_excel(writer, sheet_name="spectra", index=True, index_label=f'wl-nm_{abs_scales_name[dose_unit].replace("_", "-")}')

            
        ###### DELETE FILE #######        
        
        if delete_files:

            meas_raw_files = [x for x in raw_file_counts.parent.iterdir() if raw_file_counts.name.replace('-spect_convert.txt', '') in str(x)]                      
            [os.remove(file) for file in meas_raw_files]
            
        
        ###### FINAL PRINT STATEMENT #######
        
        print(f'{raw_file_cl} has been successfully processed !')
            

        ###### RETURN FILENAME #######
        if return_filename:
            return Path(folder_output) / f'{filename}.xlsx'
            

def photo_beam(files: list, filenaming:Optional[str] = 'none', folder:Optional[str] = '.', db:Optional[bool] = False, fontsize:Optional[int] = 28, fontsize_label:Optional[int] = 22, sigma:Optional[int] = 10, gain:Optional[int] = 0, profile_line:Optional[str] = 'horizontal', resolution:Optional[float] = None, power_beam:Union[str,int,float] = None, authors:Optional[str] = 'XX'):


    for file in files:

        ########## LOAD THE IMAGE ##########

        # load the image and remove the alpha channel
        im = imageio.imread(file)[...,:3] 

        # remove the text in the top left and bottom right corner on the beam photo
        #if camera == 'C01':
        #    bad = im.max(axis=2) > 250
        #    fix = ndimage.grey_opening(im, size=3)
        #    im[bad] = fix[bad]

        # obtain a black and white image
        im_bw = im.mean(axis=2)

        # blurr the image
        bim_bw = ndimage.gaussian_filter(im_bw, sigma) 


        ########## BS-FOTO WITH FHFM ##########

        fig1, ax1 = plt.subplots(1, 1, figsize=(15, 10))

        # plot the photo of the beam scaled with microns
        ax1.imshow(im, extent=(0, res * im.shape[1], res * im.shape[0], 1))
        
        # insert a scale bar
        scalebar = ScaleBar(
            dx=1.0, units="µm", length_fraction=0.3, fixed_value=400, sep = 4, box_color="white"
        )
        plt.gca().add_artist(scalebar)

        # plot the various contour plots based on the FHFM
        Y, X = (np.indices(im.shape[:2])*res) # generate scaled 2D arrays of x and y coordinates
        labels = {0.1: "FW0.1M", 0.5: "FWHM", 0.8: "FW0.8M"}
        cont = ax1.contour(
            X, Y, ndimage.gaussian_filter(im[..., 1] / im[..., 1].max(), sigma),
            levels=[0.1, 0.5, 0.8],
            colors="yellow",
            alpha=0.5,
        )
        ax1.clabel(cont, inline=1, fontsize=fontsize_label, fmt=labels, inline_spacing=10)
    
        # sets the labels and title
        ax1.set_xlabel("$x$ (microns)", fontsize=fontsize)
        ax1.set_ylabel("$y$ (microns)", fontsize=fontsize)
        #ax1.set_title(f'{date}, Fading beam spot N° {nb}, {lamp}, ' + '$d_{ill}$' + f' = {distance} mm', fontsize=fontsize+2)
        
        ax1.xaxis.set_tick_params(labelsize=fontsize)
        ax1.yaxis.set_tick_params(labelsize=fontsize)

        ax1.grid(False)  

        # place a text box in upper left in axes coords
        textstr = '\n'.join((
            f'camera: {camera} ',
            f'gain: {gain}',
            f'exp: {exp}ms'))

        props = dict(boxstyle='round', facecolor='white', alpha=0.8)

        ax1.text(0.02, 0.97, textstr, transform=ax1.transAxes, fontsize=fs-4,verticalalignment='top', bbox=props)     

        fig1.tight_layout()
        #fig1.savefig(folder_figures + name_file + "_FOTO.png", dpi = 300, facecolor='white')
        plt.show()



