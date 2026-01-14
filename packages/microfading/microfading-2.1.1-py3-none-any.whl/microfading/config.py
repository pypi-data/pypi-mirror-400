import pandas as pd
from pathlib import Path
from typing import get_origin, get_args, Union, Optional
import json
import os
from ipywidgets import Layout
import ipywidgets as ipw
from IPython.display import display, clear_output
import msdb
import inspect
import importlib


style = {"description_width": "initial"}
config_file = Path(__file__).parent / 'config_info.json'


def delete_device_info(key:Optional[str] = None):

    # Retrieve the devices config info
    config_info = get_config_info()
    config_info_device = config_info['devices']


    
    if key == None:
        wg_key = ipw.Dropdown(
            description='Devices',
            options=config_info_device.keys()
        )

        deleting = ipw.Button(
            description='Delete device info',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',            
        )

        button_record_output = ipw.Output()

        def button_record_pressed(b):
            """
            Save the lamp info in the db_config.json file.
            """

            button_record_output.clear_output(wait=True)

            # Remove the keys from the dictionary
            del config_info_device[wg_key.value]

            # Update the config info file
            config_info['devices'] = config_info_device
            
            # Save the updated config back to the JSON file
            with open(config_file, "w") as f:
                json.dump(config_info, f, indent=4)

            # Print output message
            with button_record_output:
                print(f'Device {wg_key.value} successfully deleted !')

        deleting.on_click(button_record_pressed)
        display(wg_key)
        display(ipw.HBox([deleting,button_record_output]))

    
    else:

        # Remove the keys from the dictionary
        del config_info_device[key]

        # Update the config info file
        config_info['devices'] = config_info_device
        
        # Save the updated config back to the JSON file
        with open(config_file, "w") as f:
            json.dump(config_info, f, indent=4)


def get_colorimetry_info(message:Optional[bool] = True):

    # Retrieve the config info
    config_info = get_config_info()    

    # Check if the 'colorimetry' key exists in the config
    if "colorimetry" in config_info:
        colorimetry_info = config_info["colorimetry"]

        # Return nothing if no colorimetric info registered
        if len(colorimetry_info) == 0:
            if message:
                print("The colorimetric information have not been registered. Please register using the 'set_colorimetry_info' function.")
            return None
        
        # Convert the colorimetric info to a DataFrame and return it
        df = pd.DataFrame.from_dict(colorimetry_info, orient="index", columns=["value"])
        return df
    
    else:
        print("The dictionary named 'colorimetry' has been removed from the config_info.json file. Re-insert it as an empty dictionary or re-install the package.")
        return None
    

def get_comments_info(message:Optional[bool] = True):

    # Retrieve the config info
    config_info = get_config_info()    

    # Check if the 'comments' key exists in the config
    if "comments" in config_info:
        comments_info = config_info["comments"]

        # Return nothing if no colorimetric info registered
        if len(comments_info) == 0:
            if message:
                print("The comments information have not been registered. Please register using the 'set_comments_info' function.")
            return None
        
        # Convert the comments info to a DataFrame and return it
        df = pd.DataFrame.from_dict(comments_info, orient="columns")
        return df

    else:
        print("The dictionary named 'comments' has been removed from the config_info.json file. Re-insert it as an empty dictionary or re-install the package.")
        return None
    

def get_config_info(key:Optional[str] = 'all'):

    # Load folder path from JSON file if it exists
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            config = json.load(file)

            if key != 'all':
                return config[key]
            else:
                return config
        
    else:
        print('The config_info.json has been deleted ! Please re-install the reflectance package.')
        return None 
    
    
def get_config_path():    

    return config_file


def get_databases_info():

    # Retrieve the config info 
    config_info = get_config_info()

    # Check if the 'databases' key exists in the config
    if "databases" in config_info:
        databases_info = config_info["databases"]

        # Return nothing if no devices info registered
        if len(databases_info) == 0:
            print("The databases information have not been registered. Please register using the 'set_databases_info' function.")
            return None
        
        # Convert the devices info to a DataFrame and return it
        df = pd.DataFrame.from_dict(databases_info, orient="columns")
        return df

    else:
        print("The dictionary named 'databases' has been removed from the config_info.json file. Re-insert it as an empty dictionary or re-install the package.")
        return None


def get_devices_info():
    
    # Retrieve the config info 
    config_info = get_config_info()
    
    # Check if the 'exposure' key exists in the config
    if "devices" in config_info:
        devices_info = config_info["devices"]

        # Return nothing if no devices info registered
        if len(devices_info) == 0:
            print("The devices information have not been registered. Please register using the 'set_devices_info' function.")
            return None
        
        # Convert the devices info to a DataFrame and return it
        df = pd.DataFrame.from_dict(devices_info, orient="columns")
        return df

    else:
        print("The dictionary named 'devices' has been removed from the config_info.json file. Re-insert it as an empty dictionary or re-install the package.")
        return None


def get_exposure_conditions():
    
    # Retrieve the config info
    config_info = get_config_info() 
    
    # Check if the 'exposure' key exists in the config
    if "exposure" in config_info:
        exposure_info = config_info["exposure"]

        # Return nothing if no exposure conditions registered
        if len(exposure_info) == 0:
            print("The exposure conditions have not been registered. Please register using the 'set_exposure_conditions' function.")
            return None

        hours_per_years = int(exposure_info['hours_per_day'] * exposure_info['days_per_year'])
        yearly_Hv = hours_per_years * exposure_info['illuminance_lux']

        exposure_info['hours_per_year'] = hours_per_years
        exposure_info['yearly_Hv_klxh'] = int(yearly_Hv / 1e3)
            
        # Convert the exposure conditions to a DataFrame and return them
        df = pd.DataFrame.from_dict(exposure_info, orient="index", columns=["value"])
        return df
    
    else:
        print("The dictionary named 'exposure' has been removed from the config_info.json file. Re-insert it as an empty dictionary or re-install the package.")
        return None  


def get_institution_info():

    # Retrieve the config info
    config_info = get_config_info() 
    
    # Check if the 'institution' key exists in the config
    if "institution" in config_info:
        institution_info = config_info["institution"]

        # Return nothing if no institution info registered
        if len(institution_info) == 0:
            print("The institution info have not been registered. Please register using the 'set_institution_info' function.")
            return None
        
        # Convert the institution info to a DataFrame and return them
        df = pd.DataFrame.from_dict(institution_info, orient="index", columns=["value"])
        return df
        
    else:
        print("The dictionary named 'institution' has been removed from the config_info.json file. Re-insert it as an empty dictionary or re-install the package.")
        return None


def get_lamps_info():

    # Retrieve the config info
    config_info = get_config_info() 
    
    # Check if the 'light_dose' key exists in the config
    if "light_dose" in config_info:
        light_dose_info = config_info["lamps"]

        # Convert the lamps info to a DataFrame
        df = pd.DataFrame.from_dict(light_dose_info, orient="index", columns=["value"])
        return df
    else:
        print("The lamps info have not been registered. Please register using the 'set_lamp_info' function.")
        return None


def get_light_dose_info():
    
    # Retrieve the config info
    config_info = get_config_info() 
    
    # Check if the 'light_dose' key exists in the config
    if "light_dose" in config_info:
        light_dose_info = config_info["light_dose"]

        # Return nothing if no institution info registered
        if len(light_dose_info) == 0:
            print("The light dose info have not been registered. Please register using the 'set_light_dose_info' function.")
            return None

        # Convert the light dose info to a DataFrame
        df = pd.DataFrame.from_dict(light_dose_info, orient="index", columns=["value"])
        return df
    
    else:
        print("The dictionary named 'light_dose' has been removed from the config_info.json file. Re-insert it as an empty dictionary or re-install the package.")
        return None


def reset_config(keys:Union[str, list] = 'all'):
    """Reset the config_info.json to its initial state, i.e. all empty dictionaries.
    """

    config_info = get_config_info()

    if keys == 'all':
    
        for key in config_info.keys():
            config_info[key] = {}

            if key == 'functions':
                config_info[key] = {
                    "linear_1p": {
                        "expression": "c0*x",
                        "bounds": "[(-np.inf),(np.inf)]"
                    },
                    "linear_2p": {
                        "expression": "c0*x+c1",
                        "bounds": "[(-np.inf,-np.inf),(np.inf,np.inf)]"
                    },
                    "power_2p": {
                        "expression": "c0*(x**c1)",
                        "bounds": "[(-np.inf,0),(np.inf,1)]"
                    },
                    "power_3p": {
                        "expression": "c0*(x**c1)+c2",
                        "bounds": "[(-np.inf,0,-np.inf),(np.inf,1,np.inf)]"
                    },
                    "sigmoid_2p": {
                        "expression": "(c0/(1+np.exp(c1*x)))",
                        "bounds": "[(-np.inf,-np.inf),(np.inf,np.inf)]"
                    },
                    "sigmoid_3p": {
                        "expression": "(c0/(1+np.exp(c1*x)))+c2",
                        "bounds": "[(-np.inf,-np.inf,-np.inf),(np.inf,np.inf,np.inf)]"
                    }
                }

        # Save the updated config back to the JSON file
        with open(config_file, "w") as f:
            json.dump(config_info, f, indent=4)

            print(f'The {config_file.name} file has been successfully and fully reset.')

    else:
        print(keys)
        if isinstance(keys, str) and keys in config_info.keys():
            keys = [keys]

        for key in keys:
            config_info[key] = {}

        # Save the updated config back to the JSON file
        with open(config_file, "w") as f:
            json.dump(config_info, f, indent=4)

            print(f'The {config_file.name} file has been successfully reset.')
    

def set_colorimetry_info():           

    # define some widgets
    wg_observer = ipw.Dropdown(
        description = 'Observer (deg)',
        value = '10',
        options = ['2', '10'],
        style = style
    )

    wg_illuminant = ipw.Dropdown(
        description = 'Illuminant',
        value = 'D65',
        options = ['A', 'B', 'C', 'D50', 'D55', 'D60', 'D65', 'D75', 'E', 'FL1', 'FL2', 'FL3', 'FL4', 'FL5', 'FL6', 'FL7', 'FL8', 'FL9', 'FL10', 'FL11', 'FL12', 'FL3.1', 'FL3.2', 'FL3.3', 'FL3.4', 'FL3.5', 'FL3.6', 'FL3.7', 'FL3.8', 'FL3.9', 'FL3.10', 'FL3.11', 'FL3.12', 'FL3.13', 'FL3.14', 'FL3.15', 'HP1', 'HP2', 'HP3', 'HP4', 'HP5', 'LED-B1', 'LED-B2', 'LED-B3', 'LED-B4', 'LED-B5', 'LED-BH1', 'LED-RGB1', 'LED-V1', 'LED-V2', 'ID65', 'ID50'],
        style = style
    )
    
    recording = ipw.Button(
        description='Save',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Click me',            
    )
    button_record_output = ipw.Output()
    
    # define the function to record the widgets values
    def button_record_pressed(b):
        """
        Save the colorimetry info in the config_info file.
        """

        button_record_output.clear_output(wait=True)
        
        # Retrieve the config info
        config_info = get_config_info() 
        
        # Update config with the colorimetric info
        config_info["colorimetry"] = {
            "observer": f'{wg_observer.value}deg',
            "illuminant": wg_illuminant.value,                             
        }
        # Save the updated config back to the JSON file
        with open(config_file, "w") as f:
            json.dump(config_info, f, indent=4)
        
        with button_record_output:
            print(f'Colorimetric conditions info recorded in the {config_file.name} file.')
    
    # link the button to the aforementioned function
    recording.on_click(button_record_pressed)

    # display the widgets
    display(ipw.VBox([wg_observer, wg_illuminant]))
    display(ipw.HBox([recording, button_record_output]))


def set_config_info():

    config_info = get_config_info()
    keys = [x for x in config_info.keys() if x not in ['colorimetry','comments','databases','devices']]


    wg_keys = ipw.Dropdown(
        description='Keys',
        placeholder='Select a key',
        options=keys,
        style=style
    )

    wg_ID = ipw.Text(
        description='ID',
        placeholder='Enter an ID number',
        style=style
    )

    wg_description = ipw.Text(
        description='Description',
        placeholder='Item information',
        style=style
    )

    recording = ipw.Button(
        description='Save',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Click me',            
    )

    button_record_output = ipw.Output()


    def button_record_pressed(b):
        """
        Save the info in the config_info.json file.
        """

        button_record_output.clear_output(wait=True)

        with open(config_file, "r") as f:
            config = json.load(f)
            existing_config = config[wg_keys.value]

            
        existing_config[wg_ID.value] = wg_description.value                    
        config[wg_keys.value] = existing_config                 
            
        # Save the updated config back to the JSON file
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)

            
        with button_record_output:
            print(f'The info have been saved in the config_info.json file.')

        
    recording.on_click(button_record_pressed)

    display(ipw.VBox([wg_keys,wg_ID, wg_description]))
    display(ipw.HBox([recording, button_record_output]))


def set_db(folder_path:Optional[str] = '', use:Optional[bool] = True, msdb_config:Optional[bool] = True):

    # retrieve the databases names
    existing_db_names = msdb.get_db_names()
    
    # define some widgets
    wg_name = ipw.Combobox(
        description = 'db_name',
        placeholder='Enter a new database name or select a database registered in the msdb package',
        value = '',
        options = existing_db_names,
        style = style,
        layout=Layout(width="50%", height="30px"),
    ) 

    wg_folder = ipw.Text(
        description = 'db_path',
        placeholder = 'Location of the database folder on your computer',
        value = folder_path,
        style = style, 
        layout=Layout(width="50%", height="30px"),
    )

    wg_use = ipw.Dropdown(
        description = 'Use',
        value = use,
        options = [True, False],
        style = style,
        layout=Layout(width="10%", height="30px"),
    )  

    recording = ipw.Button(
        description='Save',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Click me',            
    )

    button_record_output = ipw.Output()
    
    # define the function to record the widgets values
    def button_record_pressed(b):
        """
        Save the databases info in the db_config.json file.
        """
        button_record_output.clear_output(wait=True)
        with open(config_file, "r") as f:
            config = json.load(f)
        # update config with user data
        config["databases"] = {
            "db_name": wg_name.value,
            "path_folder": wg_folder.value,
            "usage": wg_use.value,
                          
        }
        # save the updated config back to the JSON file
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)

        with button_record_output:
            print(f'Database ({wg_name.value}) info recorded in the config_info.json file of the microfading package.')

        # save the datareflectancebase info inside the db_config.json fo the msdb package
        if wg_name.value not in existing_db_names:
            msdb.set_db(db_name=wg_name.value,path_folder=wg_folder.value, widgets=False)
            with button_record_output:
                
                print(f'Database ({wg_name.value}) recorded in the db_config.json file of the msdb package.')
        
    
    # define function when the database is already existing
    def change_db_name(change):
        if change.new in existing_db_names:
            wg_folder.value = msdb.get_config_file()['databases'][change.new]['path_folder']

    
    # link the button to the aforementioned function
    recording.on_click(button_record_pressed)
    wg_name.observe(change_db_name)

    # display the widgets
    display(ipw.VBox([wg_name,wg_folder, wg_use]))
    display(ipw.HBox([recording, button_record_output]))


def set_devices_info():

    # Retrieve the name of the process rawdata functions (via the __init__.py file)
    init_file = (Path(__file__).parent / '__init__.py')  

    with open(init_file, 'r') as file:
        init = file.read()

    process_functions = ['Select a function'] + [x.strip() for x in init[init.index('from .process_rawfiles import ')+ len('from .process_rawfiles import '):].splitlines()[0].split(',')]
        

    # get the databases name and create an instance of the DB class
    db_config = get_config_info()['databases']
    if len(db_config) == 0:
        device_ids = ()
        white_standard_ids = ()
    else:
        db_name = db_config['db_name']
        db = msdb.DB(db_name)
        device_ids = tuple(db.get_devices()['ID'].values)
        white_standard_ids = tuple(db.get_white_standards()['ID'].values)
    
    # define the ipywidgets
    wg_id = ipw.Combobox(        
        placeholder='Enter or select a device',
        options=device_ids,
        description='Device ID',
        ensure_option=True,
        disabled=False,
        layout=Layout(width="30%", height="30px"),
        style=style
    )

    wg_process_functions = ipw.Dropdown(
        description='Process rawdata function',
        value='Select a function',
        options=process_functions,
        layout=Layout(width="30%", height="30px"),
        style = style
    )

    wg_white_standard = ipw.Combobox(        
        placeholder='Enter or select a white standard ID',
        options=white_standard_ids,
        description='White standard',
        ensure_option=True,
        disabled=False,
        layout=Layout(width="30%", height="30px"),
        style=style
    )

    wg_average = ipw.BoundedIntText(
        value=10,
        min=0,
        max=100,
        step=1,
        description='Average',        
        disabled=False,
        layout=Layout(width="30%", height="30px"),
        style=style,
        
    )

    wg_delete_rawfiles = ipw.Dropdown(
        description='Delete rawfiles',
        options=[True, False],
        value=True,
        disabled=False,
        layout=Layout(width="30%", height="30px"),
        style=style
    )

    wg_if_wavelengths = ipw.Checkbox(
        value=False,
        description='Set wavelengths',
        disabled=False,
        indent=False,
        layout=Layout(width="10%", height="30px")
    )
        
    wg_wavelengths = ipw.IntRangeSlider(
        value=[100, 3000],
        min=100,
        max=3000,
        step=1,
        description='Wavelength range (nm)',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='d',
        style=style,
        layout=Layout(width="500px", height="30px")
    )

    recording = ipw.Button(
        description='Record info',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Click me',            
    )

    button_record_output = ipw.Output()
    wavelength_range_output = ipw.Output()

    
    # define function to set wavelength range
    def change_if_wl(change):
        if change.new == True:
            with wavelength_range_output:
                wavelength_range_output.clear_output(wait=True)                    
                display(wg_wavelengths)

        else:
            with wavelength_range_output:
                wavelength_range_output.clear_output(wait=True) 


    # define the function to record the widgets values
    def button_record_pressed(b):
        """
        Save the device info in the db_config.json file.
        """

        button_record_output.clear_output(wait=True)

        # Retrieve the config info
        config_info = get_config_info()            
        existing_info = config_info["devices"]

        # Retrieve the wavelength range if any
        if wg_if_wavelengths.value == False:
            wl_range = None
        else:
            wl_range = wg_wavelengths.value
            
        # Update config with the device info
        if len(existing_info) == 0:
            existing_info[wg_id.value] = {
                'average': wg_average.value,
                'delete_rawfiles':wg_delete_rawfiles.value,
                'process_function': wg_process_functions.value,
                'white_standard': wg_white_standard.value,                
                'wl_range': wl_range
                }  

        elif wg_id.value in list(existing_info.keys()):
                
            device_dic = existing_info[wg_id.value]
            device_dic['average'] = wg_average.value
            device_dic['delete_rawfiles'] = wg_delete_rawfiles.value
            device_dic['process_function'] = wg_process_functions.value
            device_dic['white_standard'] = wg_white_standard.value
            device_dic['wl_range'] = wl_range
          
        else:                      
            existing_info[wg_id.value] = {
                'average': wg_average.value,
                'delete_rawfiles':wg_delete_rawfiles.value,
                'process_function': wg_process_functions.value,
                'white_standard': wg_white_standard.value,
                'wl_range': wl_range
                }
            
        # Save the updated config back to the JSON file
        with open(config_file, "w") as f:
            json.dump(config_info, f, indent=4)

            
        with button_record_output:
            print(f'Device info ({wg_id.value}) recorded in the {config_file.name} file.')


    # link the widgets to the aforementioned functions  
    recording.on_click(button_record_pressed)
    wg_if_wavelengths.observe(change_if_wl, names='value')


    # display the widgets
    display(ipw.VBox([wg_id, wg_process_functions, wg_average, wg_white_standard, wg_delete_rawfiles, ipw.HBox([wg_if_wavelengths, wavelength_range_output])]))
    display(ipw.HBox([recording, button_record_output]))


def set_exposure_conditions():

    # define some widgets
    wg_illuminance = ipw.IntText(
        description = 'Illuminance (lux)',
        value = 100,
        style = style, 
    )

    wg_hours_per_day = ipw.IntText(
        description = 'Exposure hours per day',
        value = 10,
        style = style, 
    )

    wg_days_per_year = ipw.IntText(
        description = 'Exposure days per year',
        value = 365,
        style = style, 
    )

    recording = ipw.Button(
        description='Save',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Click me',            
    )

    button_record_output = ipw.Output()


    # define the function to record the widgets values
    def button_record_pressed(b):
        """
        Save the exposure conditions info in the config_info.json file.
        """

        button_record_output.clear_output(wait=True)

        # Retrieve the config info
        config_info = get_config_info()            
        
        # Update config with exposure conditions info
        config_info["exposure"] = {
            "illuminance_lux": wg_illuminance.value,
            "hours_per_day": wg_hours_per_day.value,
            "days_per_year": wg_days_per_year.value,                
        }

        # Save the updated config back to the JSON file
        with open(config_file, "w") as f:
            json.dump(config_info, f, indent=4)

            
        with button_record_output:
            print(f'Exposure conditions info recorded in the {config_file.name} file.')

    # link the button widget to the aforementioned function  
    recording.on_click(button_record_pressed)

    # display the widgets
    display(ipw.VBox([wg_illuminance, wg_hours_per_day,wg_days_per_year]))
    display(ipw.HBox([recording, button_record_output]))


def set_lamp_info(self):
    """Register a lamp inside config_info.json file.
    """
        
    wg_id = ipw.Text(
        description = 'Lamp ID',
        placeholder = 'Enter an ID',            
        style = style,
        layout=Layout(width="95%", height="30px"),
    )

    wg_description = ipw.Text(
        description = 'Description',
        placeholder = 'Enter info about the lamp',            
        style = style,
        layout=Layout(width="95%", height="30px"),
    )

    wg_size = ipw.Text(
        description = 'Beam size (micron)',
        placeholder = 'Enter a beam size (if applicable)',            
        style = style,
        layout=Layout(width="95%", height="30px"),
    )        

    recording = ipw.Button(
        description='Save',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Click me',            
    )

    button_record_output = ipw.Output()

    def button_record_pressed(b):
        """
        Save the lamp info in the db_config.json file.
        """

        button_record_output.clear_output(wait=True)

        with open(self.config_file, "r") as f:
            config = json.load(f)

        # Update config with user data
        config["lamps"] = {
            wg_id.value: {'description': wg_description.value, 'beam_size_um':wg_size.value}                                             
        }
        # Save the updated config back to the JSON file
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=4)

            
        with button_record_output:
            print('The lamp info have been recorded in the db_config.json file.')


    recording.on_click(button_record_pressed)

    display(ipw.VBox([wg_id, wg_description]))
    display(ipw.HBox([recording, button_record_output]))
    
    
def set_light_dose():

    # define some widgets
    wg_dose_unit = ipw.Dropdown(
        description = 'Dose unit',
        placeholder = 'Select a unit',
        options = ['He_MJ/m2', 'Hv_Mlxh', 't_sec'],
        style = style
    )

    recording = ipw.Button(
        description='Save',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Click me',            
    )

    button_record_output = ipw.Output()

    # define the function to record the widgets values
    def button_record_pressed(b):
        """
        Save the light dose unit in the config_info.json file.
        """

        button_record_output.clear_output(wait=True)

        # Retrieve the config info
        config_info = get_config_info() 

        # Update config with light dose info
        config_info["light_dose"] = {
            "unit": wg_dose_unit.value,                                
        }

        # Save the updated config back to the JSON file
        with open(config_file, "w") as f:
            json.dump(config_info, f, indent=4)

            
        with button_record_output:
            print(f'The unit of the light dose has been recorded in the {config_file.name} file.')


    # link the button widget to the aforementioned function  
    recording.on_click(button_record_pressed)

    # display the widgets
    display(ipw.VBox([wg_dose_unit]))
    display(ipw.HBox([recording, button_record_output]))


def set_institution_info():

    # define some widget
    wg_name = ipw.Text(
        description = 'Institution name',
        placeholder = 'Enter a name',            
        style = style,
        layout=Layout(width="50%", height="30px"),
    )

    wg_acronym = ipw.Text(
        description = 'Institution acronym',
        placeholder = 'Enter an acronym (optional)',            
        style = style,
        layout=Layout(width="50%", height="30px"),
    )

    wg_department = ipw.Text(
        description = 'Department',
        placeholder = 'Enter a department (optional)',            
        style = style,
        layout=Layout(width="50%", height="30px"),
    )

    wg_address = ipw.Text(
        description = 'Institution address',
        placeholder = 'Enter an address (optional)',            
        style = style,
        layout=Layout(width="50%", height="30px"),
    )

    recording = ipw.Button(
        description='Save',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Click me',            
    )

    button_record_output = ipw.Output()

    
    # define the function to record the widgets values
    def button_record_pressed(b):
        """
        Save the institution info in the config_info.json file.
        """

        button_record_output.clear_output(wait=True)

        # Retrieve the config info
        config_info = get_config_info() 

        # Update config with user data
        config_info["institution"] = {
            "name": wg_name.value,
            "acronym": wg_acronym.value,
            "department": wg_department.value,
            "address": wg_address.value,                                
        }
        # Save the updated config back to the JSON file
        with open(config_file, "w") as f:
            json.dump(config_info, f, indent=4)

            
        with button_record_output:
            print(f'The institution info have been recorded in the {config_file.name} file.')


    # link the button widget to the aforementioned function  
    recording.on_click(button_record_pressed)

    # display the widgets
    display(ipw.VBox([wg_name, wg_acronym, wg_department, wg_address]))
    display(ipw.HBox([recording, button_record_output]))


def set_report_figures():

    # Dynamically import the module
    module_mf = importlib.import_module('microfading')

    # Get the class from the module
    cls = getattr(module_mf, 'MFT', None)
    if cls is None or not inspect.isclass(cls):
        print(f"Class MFT not found in module microfading.")
        return
        
    # Get all methods in the class
    methods = inspect.getmembers(cls, predicate=inspect.isfunction)        
    plot_methods = [x[0] for x in methods if 'plot_' in x[0]]
    
        
    # Mapping from Python types to ipywidgets
    type_to_widget = {
        bool: ipw.Checkbox,
        int: ipw.IntText,
        float: ipw.FloatText,
        str: ipw.Text,
    }
        
    # Create a dictionary to hold the widgets
    widgets_dict = {}
        
        
    # Iterate over each method and get its parameters
    methods_dic = {}
    for method_name, method in methods:            
        
        if method_name in plot_methods:
            sig = inspect.signature(method) 
                      
            params = list(sig.parameters.keys())[1:]
            methods_dic[method_name] = params
            
            
            param_type = [x[1].annotation for x in sig.parameters.items()]
            #param_type = sig.parameters.items()[1].annotation
            #param_name =  sig.parameters.items()[0]
            param_name = [x[0] for x in sig.parameters.items()]

            # Resolve Optional and Union types
            """
            if get_origin(param_type) is Union:
                args = get_args(param_type)
                if type(None) in args:  # Handle Optional
                    args = tuple(arg for arg in args if arg is not type(None))
                if len(args) == 1:
                    param_type = args[0]
                else:
                    # For Union types with multiple possibilities, choose a default
                    param_type = args[0]  # You can customize this logic

            if param_type in type_to_widget:
                widget_class = type_to_widget[param_type]
                widgets_dict[param_name] = widget_class(description=param_name)
            else:
                # Default to Text widget if type is not mapped
                widgets_dict[param_name] = ipw.Text(description=param_name)
            """

    wg_functions = ipw.Dropdown(
        description= 'Plot functions',
        value=plot_methods[0],
        options=plot_methods,
        style=style,
        layout=Layout(width="20%", height="30px"),
    )

    wg_parameter = ipw.Dropdown(
        description='Parameters',
        value=methods_dic[wg_functions.value][0],
        options=methods_dic[wg_functions.value],
        style=style,
    )

    output_parameter_value = ipw.Output()
        
    wg_parameter_value = ipw.Text(
        placeholder='Enter a value for the parameter',
        style=style
    )

                
    recording = ipw.Button(
        description='Save configuration',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Click me',            
    )

    button_record_output = ipw.Output()

    def change_function(change):
        wg_parameter.options = methods_dic[change.new]
        wg_parameter.value = methods_dic[change.new][0]

    def change_parameter(change):

        with output_parameter_value:
            output_parameter_value.clear_output()
            param_name = change['new']            
            display(widgets_dict[param_name])
        
    def button_record_pressed(b):
        """
        Save the light dose unit in the db_config.json file.
        """

        button_record_output.clear_output(wait=True)

    wg_functions.observe(change_function, names="value")
    recording.on_click(button_record_pressed)

    display(ipw.VBox([wg_functions]))
    display(ipw.HBox([wg_parameter, output_parameter_value]))
    display(ipw.HBox([recording, button_record_output]))


def set_lamps_info():

    # define some widgets
    wg_ID = ipw.Text(
        description='ID',
        placeholder='ID number of the lamp',
        style=style, 
        layout=Layout(width="30%", height="30px")
    )
    wg_description = ipw.Text(
        description='Description',
        placeholder='Description of the lamp',
        style=style, 
        layout=Layout(width="30%", height="30px")
    )
    recording = ipw.Button(
        description='Save',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Click me',            
    )
    button_record_output = ipw.Output()
    
    # define the function to record the widgets values
    def button_record_pressed(b):
        """
        Save the lamp info in the config_info.json file.
        """
        button_record_output.clear_output(wait=True)
        with open(config_file, "r") as f:
            config = json.load(f)
            existing_info = config['lamps']

        existing_info[wg_ID.value] = wg_description.value            
        config["lamps"] = existing_info                                      
        
        # Save the updated config back to the JSON file
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)
        
        with button_record_output:
            print(f'The lamp info have been saved in the {config_file.name} file.')
    
    # link the button to the aforementioned function
    recording.on_click(button_record_pressed)

    # display the widgets
    display(ipw.VBox([wg_ID, wg_description]))
    display(ipw.HBox([recording, button_record_output]))


