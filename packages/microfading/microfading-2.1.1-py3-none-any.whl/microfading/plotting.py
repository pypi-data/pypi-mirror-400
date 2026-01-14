import matplotlib.patches
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import colour
from typing import Optional, Union
import imageio
from pathlib import Path
from scipy.signal import savgol_filter
import os
import random

####### DEFINE GENERAL PARAMETERS #######

plt.rcParams["font.family"] = "serif"
D65 = colour.CCS_ILLUMINANTS["cie_10_1964"]["D65"]

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
    'Hv': 'Exposure dose $H_v$ (Mlxh)',  
    'He': 'Radiant Exposure $H_e$ (MJ/m²)',  
    't' : 'Exposure duration (seconds)'     
}


x_labels = {
    'Hv': 'Exposure dose $H_v$ (Mlxh)',
    'He': 'Radiant Exposure $H_e$ ($MJ/m^2$)',
    't': 'Exposure duration (sec)',
    't_s': 'Exposure duration (sec)',
    't_m': 'Exposure duration (min)'
}

x_labels_short = {
    'Hv': '$H_v$ (Mlxh)',
    'He': '$H_e$ ($MJ/m^2$)',
    't': '$t$ (sec)',
    't_s': '$t$ (sec)',
    't_m': '$t$ (min)'
}


ls_dic = {
        'dE76': '--',
        'dE00': '-',
        'dE94': ':',
        'dR_vis': '-.',  
        'L*' : '--',
        'a*' : ':',
        'b*' : '-.', 
        'C*' : '-.', 
        'h' : ':', 
        'dL*' : '-.',
        'da*' : '--',
        'db*' : '-.',
        'dC*' : ':', 
        'dh' : '-', 
        'none' : '-',     
    }


lw_dic = {
        'dE76': 2,
        'dE00': 3,
        'dE94': 1,
        'dR_vis': 2,  
        'L*' : 2,
        'a*' : 2,
        'b*' : 2, 
        'C*' : 1, 
        'h' : 1, 
        'dL*' : 2,
        'da*' : 2,
        'db*' : 2,
        'dC*' : 1, 
        'dh' : 1, 
        'none' : 2,     
    }


colors_dic = {
        'dE76': 'limegreen',
        'dE00': 'blue',
        'dE94': 'yellow',
        'dR_vis': 'green',
        'dL*': 'b',
        'da*': 'red',
        'db*': 'orange', 
        'dC*' : 'brown',
        'dh' : 'grey', 
        'L*' : 'b',
        'a*' : 'red',
        'b*' : 'orange', 
        'C*' : 'grey', 
        'h' : 'brown',        
        'none' : 'k',     
    }


####### THE FUNCTIONS #######

def bars(data, stds=None, coordinate='dE00', colors=None, fontsize=24, legend_labels=[], title=None, title_fontsize=24, save=False, path_fig='cwd'):

    sns.set_theme(font='serif')
    fig, ax = plt.subplots(1,1, figsize=(15,8))

    ax.xaxis.set_tick_params(labelsize=fontsize)
    ax.yaxis.set_tick_params(labelsize=fontsize)

    ax.set_xlabel('Microfading analyses numbers', fontsize=fontsize)
    ax.set_ylabel(labels_eq[coordinate], fontsize=fontsize)

    ax.xaxis.grid() # horizontal lines only


    plt.tight_layout()
    plt.show()


def BWSE(data, frequency=False, bins=[1,2,3,4,5], figsize=(10,10), colors:Union[str, list] = None, fontsize=24, title=None, title_fontsize=24, rotate_xlabels:Optional[int] = 0, position_xlabels:Optional[str] = 'center', save=False, path_fig='cwd'):
    
    # set the aesthetics of the figure
    sns.set_theme(font='serif', style='darkgrid', context='paper', palette='colorblind', font_scale=1)
    
    # create the figure
    fig, ax = plt.subplots(1,1, figsize=figsize)

    if frequency:
        
        ax.hist(data[1], bins=bins, align='left')

        ax.set_xlabel('BWS', fontsize=fontsize)
        ax.set_ylabel('Number of MFT analyses', fontsize=fontsize)

        
        ax.set_xticks(bins)
    
    else:

        measurement_ids = data[0]
        measurement_values = data[1]
        objects = sorted(set([x.split('.')[1] for x in measurement_ids]))

        colors = [[x] for x in colors]       
        df_data = pd.DataFrame({'MeasurementID': measurement_ids, 'Value': measurement_values, 'Color': colors})

        # Extract object IDs and measurement IDs
        df_data['ObjectID'] = df_data['MeasurementID'].apply(lambda x: x.split('.')[1])
        df_data['MeasID'] = df_data['MeasurementID'].apply(lambda x: x.split('.')[2])

        
        i = 1
        x_ticks = []
        labels = []

        for obj in objects:
            obj_meas = df_data.query(f'ObjectID == "{obj}"')
            bwse_values = obj_meas['Value'].values
            meas_ids = obj_meas['MeasID'].values
            srgb_values = obj_meas['Color'].values
            
            labels_obj = []
            N = len(meas_ids)    
            obj_tick = str(int(np.cumsum(np.arange(1,1+N))[-1] / N)).zfill(2)
            
            for ID, value, srgb in zip(meas_ids, bwse_values, srgb_values):
                
                ax.bar(i, value, width=1, color=srgb[0], ec="none")
                
                labels_obj.append(str(ID))
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
        print(labels)
        # Add labels, title, and legend
        ax.set_xlabel('Analyses numbers per object', fontsize=fontsize)
        ax.set_ylabel('BWSE values', fontsize=fontsize)
        
        # Set the x-ticks and xlabels
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(labels)
               
        # Display the legend
        handles, labels = ax.get_legend_handles_labels()
        unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
        ax.legend(*zip(*unique),fontsize=fontsize-4)
      

    # Set the title
    ax.set_title(title, fontsize=title_fontsize)
    
    # Set the size of the axis-ticklabels
    ax.xaxis.set_tick_params(labelsize=fontsize)
    ax.yaxis.set_tick_params(labelsize=fontsize)
    

    ax.xaxis.grid() # horizontal lines only

    plt.tight_layout()

    # Save the figure
    if save == True:
        if path_fig == 'cwd':
            path_fig = f'{os.getcwd()}/BWSE.png'                
                
        fig.savefig(path_fig,dpi=300, facecolor='white')  

    # Display the figure
    plt.show()


def CIELAB(
        data: pd.DataFrame,
        stdev: Optional[bool] = True,
        data_settings: Optional[dict] = {},
        figure_settings: Optional[dict] = {},
        legend_settings: Optional[dict] = {},
        lines_settings: Optional[dict] = {},        
        colors=None, fontsize=24, legend_labels=[], title=None, title_fontsize=24, line=False, legend_position='in', legend_fontsize=20, legend_title='', save=False, path_fig='cwd', start_value=True, dE=False, obs_ill=None, return_data=False, *args, **kwargs):
    """Plot the CIELAB coordinates of one or several datasets.

    Parameters
    ----------
    data : list
        A list of data points, where each data point is a numpy array. 

    stdev : list, optional
        A list of standard variation values respective to each element given in the data parameter, by default []

    legend_labels : list, optional
        A list of labels respective to each element given in the data parameter that will be shown in the legend. When the list is empty there is no legend displayed, by default []
    
    title : str, optional
        Add a title, by default None
    
    colors : str, optional
        Color of the data points. When 'sample' is passed as an argument, the color will correspond to the srgb values of the sample. A list of colors - respective to each element given in the data parameter - can be passed, by default None
    
    fontsize : int, optional
        Fontsize of the plot (ticks and labels), by default 24
    
    fontsize_title : int, optional
        Fontsize of the title, by default 24
    
    line : bool, optional
        Add a gray dash line to a time-series of Lab values, by default False
    
    save : bool, optional
        _description_, by default False
    
    path_fig : str, optional
        _description_, by default 'cwd'
    """

    # Extract the data settings
    dose_unit = data_settings.get('dose_unit', 'He')
        
    # Extract the legend settings    
    legend_labels = legend_settings.get('labels', [])
    legend_fontsize = legend_settings.get('fontsize', 14)
    legend_position = legend_settings.get('position', 'in')
    legend_title = legend_settings.get('title', None)
    legend_ncols = legend_settings.get('ncols', 1)
    legend_obs_ill = legend_settings.get('obs_ill', None)

    # Extract the lines settings
    mss = lines_settings.get('size', 6)
    markers = lines_settings.get('markers', 'o')
    marker_colors = lines_settings.get('colors', None)
    alphas = lines_settings.get('alpha', 1)

    # Extract the figure settings
    title = figure_settings.get('title', None)
    xlabel = figure_settings.get('xlabel', x_labels_short[dose_unit])
    ylabel = figure_settings.get('ylabel', 'CIE $\Delta E_{00}$')    
    fontsize = figure_settings.get('fontsize', 18)
    fontsize_title = figure_settings.get('fontsize_title', 20)
    
    # Retrieve the measurement ids
    meas_ids = data.columns.get_level_values('meas_id').unique()
        
    # Fetch the colour circle image
    if dE == False:
        im_colour_circle = imageio.imread(Path(__file__).parent / 'colour_circle.png')

    # Set the aesthetics of the figure
    sns.set_theme(font='serif', style='darkgrid', context='paper', palette='colorblind', font_scale=1)

    # Create the figure
    figure_sizes = {'in': (10,10), 'out': (12,10)}
    fig, ax = plt.subplots(2,2, figsize=figure_sizes[legend_position], gridspec_kw=dict(width_ratios=[1, 2], height_ratios=[2, 1]))
    Lb, ab, AB, aL = ax[0, 0], ax[0, 1], ax[1, 0], ax[1, 1]
    
    
    # Define the color of the lines
    if marker_colors == None:
        colors = [None] * len(meas_ids)

    elif marker_colors == 'sample':
        colors = ['sample'] * len(meas_ids)

    elif isinstance(marker_colors, str):
        colors = [marker_colors] * len(meas_ids)

    elif isinstance(marker_colors, list):
        if len(marker_colors) < len(meas_ids):
            colors = marker_colors * len(meas_ids)

        else:
            colors = marker_colors
        
   
    # Define labels 
    if legend_labels == None:
        legend_labels = ['none'] * len(meas_ids)        
    elif legend_labels == 'none':        
        legend_labels = ['none'] * len(meas_ids)    
    elif len(legend_labels) == 0:
        legend_labels = ['none'] * len(meas_ids)
        
    # Define the markers
    if markers == 'random':
        markers = ['o','s','X','>','D','^','v','P','<','*'] * 5

    elif isinstance(markers, str):
        markers = markers * len(meas_ids)

    elif isinstance(markers, list):
        if len(markers) < len(meas_ids):
            markers = markers * len(meas_ids)

    elif markers == None:
        markers = ['o'] * len(meas_ids)

    # Define the size of the markers
    if mss == 'random':
        mss = [4,3,6,10,7,8,11,2,5,9] * 5

    elif isinstance(mss, int):
        mss = [mss] * len(meas_ids)

    elif isinstance(markers, list):
        if len(mss) < len(meas_ids):
            mss = mss * len(meas_ids)

    elif mss == None:
        mss = [20] * len(meas_ids)

    # Define the opacity of the markers
    if isinstance(alphas, (int,float)):
        alphas = [alphas] * len(meas_ids)

    elif isinstance(alphas, list):
        if len(alphas) < len(meas_ids):
            alphas = alphas * len(meas_ids)

    # whether to show the CIELAB colour space

    if dE == False:

        AB.imshow(im_colour_circle, extent=(-110,110,-110,110))                 
        AB.axhline(0, color="black", lw=0.5)
        AB.axvline(0, color="black", lw=0.5)
    
    # plot the data
    for meas_id, color, label, marker, ms, alpha in zip(meas_ids,colors, legend_labels, markers, mss, alphas):
                
        
        data_meas = data[meas_id].dropna(axis=0)


        L_n = data_meas['L*'].iloc[:,0].values
        a_n = data_meas['a*'].iloc[:,0].values
        b_n = data_meas['b*'].iloc[:,0].values

        if 'std' in data_meas.columns.get_level_values('data_type'):
            L_s = data_meas['L*']['std'].values
            a_s = data_meas['a*']['std'].values
            b_s = data_meas['b*']['std'].values

        else:
            L_s = np.zeros(len(L_n))
            a_s = np.zeros(len(a_n))
            b_s = np.zeros(len(b_n))

        
        if color == 'sample':
            Lab = np.array([L_n, a_n, b_n]).transpose()            
            srgb = colour.XYZ_to_sRGB(colour.Lab_to_XYZ(Lab), D65).clip(0, 1)
            color = srgb[0] 
        
        if start_value:
            
            Lb.errorbar(L_n[1:], b_n[1:], yerr=b_s[1:], xerr=L_s[1:], fmt=marker, ms=ms, color=color, ecolor='0.7', alpha=alpha, mew=0, **kwargs)
            ab.errorbar(a_n[1:], b_n[1:], yerr=b_s[1:], xerr=a_s[1:], fmt=marker, ms=ms, color=color, ecolor='0.7', alpha=alpha, mew=0, label=label, **kwargs)
            aL.errorbar(a_n[1:], L_n[1:], yerr=L_s[1:], xerr=a_s[1:], fmt=marker, ms=ms, color=color, ecolor='0.7', alpha=alpha, mew=0, **kwargs)

            Lb.scatter(L_n[0], b_n[0], marker = 'x', color='k', s=120, **kwargs)
            ab.scatter(a_n[0], b_n[0], marker = 'x', color='k', s=120, **kwargs)
            start_aL = aL.scatter(a_n[0], L_n[0], marker = 'x', color='k', s=120, **kwargs)

        else:
            Lb.errorbar(L_n, b_n, yerr=b_s, xerr=L_s, fmt=marker, ms=ms, color=color, alpha=alpha, mew=0, **kwargs)
            ab.errorbar(a_n, b_n, yerr=b_s, xerr=a_s, fmt=marker, ms=ms, color=color, alpha=alpha, mew=0, **kwargs)
            aL.errorbar(a_n, L_n, yerr=L_s, xerr=a_s, fmt=marker, ms=ms, color=color, alpha=alpha, mew=0, **kwargs)


        if dE:
            H = data_meas.index
            dE00 = data_meas['dE00'].iloc[:,0].values

            AB.plot(H,dE00, color=color)

            if 'std' in data_meas.columns.get_level_values('data_type'):                
                dE00_s =  data_meas['dE00']['std'].values
                AB.fill_between(H,dE00+dE00_s, dE00-dE00_s, alpha=0.5, color='0.75', ec='none')

        else:
            AB.scatter(a_n,b_n, color='0.5', marker='o') 


    if dE:
        AB.set_xlim(0)
        AB.set_ylim(0) 

        AB.set_xlabel(xlabel, fontsize=fontsize)
        AB.set_ylabel(ylabel, fontsize=fontsize) 

    else:
        AB.grid(False) 
        AB.set_xlim(-110, 110)
        AB.set_ylim(-110, 110)  

        AB.set_xlabel("CIE $a^*$", fontsize=fontsize)
        AB.set_ylabel("CIE $b^*$", fontsize=fontsize)       
                     
    Lb.set_xlabel("CIE $L^*$", fontsize=fontsize)
    Lb.set_ylabel("CIE $b^*$", fontsize=fontsize)    
    aL.set_xlabel("CIE $a^*$", fontsize=fontsize)
    aL.set_ylabel("CIE $L^*$", fontsize=fontsize) 

    for axis in [Lb, aL, AB, ab]:
        axis.xaxis.set_tick_params(labelsize=fontsize)
        axis.yaxis.set_tick_params(labelsize=fontsize)


    if title != None:
        plt.suptitle(title, fontsize=fontsize_title)

    if legend_labels[0] != 'none' and len(legend_labels) < 19:
        if legend_position == 'in':
            ab.legend(loc = 'best', fontsize=legend_fontsize, title=legend_title, title_fontsize=legend_fontsize)

        elif legend_position == 'out':            
            ab.legend(loc='upper left',fontsize=legend_fontsize, title=legend_title, bbox_to_anchor=(1, 1), title_fontsize=legend_fontsize)

    if legend_obs_ill == None:
        aL.legend([start_aL], [f'Start'], fontsize=legend_fontsize)
    else:
        aL.legend([start_aL], [f'Start\n{legend_obs_ill}'], fontsize=legend_fontsize-2)

    plt.tight_layout()
    
    if save == True:
        if path_fig == 'cwd':
            path_fig = f'{os.getcwd()}/CIELAB.png'                
                
        fig.savefig(path_fig,dpi=300, facecolor='white') 

    plt.show()
    return







    for i, (el_data, label, std) in enumerate(zip(data, legend_labels, stds)):

        
        # compute dE values
        if dE:                   
            dE00 = np.round([colour.delta_E(el_data[1:].T[0],x) for x in el_data[1:].T],3)            
            L, a, b = el_data[1], el_data[2], el_data[3]

        else:
            L, a, b = el_data[0], el_data[1], el_data[2]

        # retrieve the light dose values
        H = el_data[0] if dE else None                       
        
               
        # define the colors and color_line of the markers        
        if colors == 'sample':
            Lab = np.array([L, a, b]).transpose()            
            srgb = colour.XYZ_to_sRGB(colour.Lab_to_XYZ(Lab), D65).clip(0, 1)
            color = srgb[0]            
            
        elif colors == None:
            color = None           

        elif isinstance(colors, str):            
            color = colors            

        else:
            color = colors[i]            
        
     
        # plot single colour points or grouped colour points
        if len(el_data.shape) == 1:  #.shape
            
            Lb.errorbar(L, b, yerr=std[2], xerr=std[0], fmt='o', color=color, **kwargs)
            ab.errorbar(a, b, yerr=std[2], xerr=std[1], fmt='o', color=color, **kwargs, label=label)
            aL.errorbar(a, L, yerr=std[2], xerr=std[0], fmt='o', color=color, **kwargs) 
                        
            AB.imshow(im_colour_circle, extent=(-110,110,-110,110))  
            AB.scatter(a,b, color='0.5', marker='o') 
            AB.axhline(0, color="black", lw=0.5)
            AB.axvline(0, color="black", lw=0.5)                       

        else:             
            Lb.errorbar(L[1:], b[1:], yerr=std[2], xerr=std[0], fmt='o', color=color, **kwargs)
            ab.scatter(a[1:], b[1:], color=color, label = label, **kwargs)            
            aL.scatter(a[1:], L[1:], color=color, **kwargs)

            Lb.scatter(L[0], b[0], marker = 'x', color='k', s=120, **kwargs)
            ab.scatter(a[0], b[0], marker = 'x', color='k', s=120, **kwargs)
            plot_aL = aL.scatter(a[0], L[0], marker = 'x', color='k', s=120, **kwargs) 
            
            if obs_ill == None:
                aL.legend([plot_aL], [f'Start'], fontsize=fontsize-5)
            else:
                aL.legend([plot_aL], [f'Start\n{obs_ill}'], fontsize=fontsize-5)

            # plot the dE values or the a*b* values
            if dE:
                AB.plot(H,dE00, color=color)
            else:
                               
                AB.imshow(im_colour_circle, extent=(-110,110,-110,110)) 
                AB.scatter(a,b, color='0.5', marker='o') 
                AB.axhline(0, color="black", lw=0.5)
                AB.axvline(0, color="black", lw=0.5)
                  
            # plot a line connecting colour points
            if line:
                Lb.plot(L,b, color='0.6', ls='--', lw=1)
                ab.plot(a,b, color='0.6', ls='--', lw=1)
                aL.plot(a,L, color='0.6', ls='--', lw=1)


    if dE:
        AB.set_xlim(0)
        AB.set_ylim(0) 

        AB.set_xlabel("Exposure dose $H_v$ (Mlxh)", fontsize=fontsize)
        AB.set_ylabel("$\Delta E^*_{00}$", fontsize=fontsize)  

    else:
        AB.grid(False) 
        AB.set_xlim(-110, 110)
        AB.set_ylim(-110, 110)  

        AB.set_xlabel("CIE $a^*$", fontsize=fontsize)
        AB.set_ylabel("CIE $b^*$", fontsize=fontsize)       
                     
    Lb.set_xlabel("CIE $L^*$", fontsize=fontsize)
    Lb.set_ylabel("CIE $b^*$", fontsize=fontsize)    
    aL.set_xlabel("CIE $a^*$", fontsize=fontsize)
    aL.set_ylabel("CIE $L^*$", fontsize=fontsize) 

    for axis in [Lb, aL, AB, ab]:
        axis.xaxis.set_tick_params(labelsize=fontsize)
        axis.yaxis.set_tick_params(labelsize=fontsize)
 

    if start_value:
        aL.set_title('x : start values', fontsize=title_fontsize)

    if title != None:
        plt.suptitle(title, fontsize=title_fontsize)

    

    if legend_labels[0] != 'none' and len(legend_labels) < 19:
        if legend_position == 'in':
            ab.legend(loc = 'best', fontsize=legend_fontsize, title=legend_title, title_fontsize=legend_fontsize)

        elif legend_position == 'out':            
            ab.legend(loc='upper left',fontsize=legend_fontsize, title=legend_title, bbox_to_anchor=(1, 1), title_fontsize=legend_fontsize)
         

    plt.tight_layout()
    
    if save == True:
        if path_fig == 'cwd':
            path_fig = f'{os.getcwd()}/CIELAB.png'                
                
        fig.savefig(path_fig,dpi=300, facecolor='white')  
    
    
    if return_data:    
        return plt, Lb,ab,aL
    
    else:
        plt.show()


def coordinates(data, std:Optional[bool] = True, fontsize=20, legend_labels=[], legend_fontsize=20, legend_position=0, legend_title=None, title=None, title_fontsize=22, ls=None, colors=None, figsize='default', save=False, path_fig='cwd',):

    
    coordinates = data.columns.get_level_values('coordinate').unique()    
    dose_name = data.index.name.split('_')[0]
    dose_label = x_labels[dose_name]
    
    # Set the aesthetics of the figure
    sns.set_theme(context='paper', font='serif', palette='colorblind') 

    # Set the size of the figure
    if figsize == 'default':
        figsize = (10,3.5*len(coordinates))

    elif isinstance(figsize, tuple) and len(figsize) == 2:
        pass
    else:
        print(f'Plotting aborted ! The figsize value you entered ({figsize}) is not valid. Please, enter a tuple of two integers (x,y) where x corresponds to the width and y to the height of the figure.')
        return
    
    # Create the figure
    fig, ax = plt.subplots(len(coordinates),1, figsize=figsize, sharex=True)

    # Define the linestyles
    if ls == None:
        ls = ['-'] * len(data)
    
    # Define labels 
    if legend_labels == None:
        legend_labels = ['none'] * len(data)        
    elif legend_labels == 'none':        
        legend_labels = ['none'] * len(data)    
    elif len(legend_labels) == 0:
        legend_labels = ['none'] * len(data)

    
    for i, coordinate in enumerate(coordinates):
    
        data_coordinate = data.xs(key=coordinate, level='coordinate', axis=1)    
        meas_ids = data.columns.get_level_values('meas_id').unique()
        
        x = data_coordinate.index    
        
        for j, meas_id in enumerate(meas_ids):
        
            d = data_coordinate[meas_id].dropna(axis=0)
            x = d.index
            y = d.iloc[:,0].values

            ax[i].plot(x,y, ls=ls[j], label=legend_labels[j])

            if 'std' in d.columns and std == True:
                    
                y_std = d['std'].values
                ax[i].fill_between(x, y+y_std, y-y_std, color='0.75', alpha=0.5, ec='none')


    ax[-1].set_xlabel(dose_label, fontsize=fontsize)
    ax[-1].xaxis.set_tick_params(labelsize=fontsize)

    
    for i, coord in enumerate(coordinates):

        ax[i].set_xlim(0)
        ax[i].yaxis.set_tick_params(labelsize=fontsize)
        ax[i].set_ylabel(f'CIE {labels_eq[coord]}', fontsize=fontsize)

        

    if title != None:
        plt.suptitle(title, fontsize=title_fontsize)

    

    if legend_labels[0] != 'none' and len(legend_labels) < 19:

        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles)) 
        
        if legend_position == 'out':           
        
            ax[0].legend(by_label.values(), by_label.keys(), loc='upper left', ncol=1, fontsize=legend_fontsize, title=legend_title, title_fontsize=legend_fontsize, bbox_to_anchor=(1, 1)) 
        
        else:
            ax[legend_position].legend(by_label.values(), by_label.keys(), loc = 'best', fontsize=legend_fontsize, title=legend_title, title_fontsize=legend_fontsize)
        

    plt.tight_layout()
    
    if save == True:
        if path_fig == 'cwd':
            path_fig = f'{os.getcwd()}/{"".join([x[0] for x in coordinates])}.png'                
                
        fig.savefig(path_fig,dpi=300, facecolor='white') 


    plt.show()


def delta(
        data: pd.DataFrame,        
        stdev: Optional[bool] = True,        
        data_settings: Optional[dict] = {},
        figure_settings: Optional[dict] = {},
        legend_settings: Optional[dict] = {},
        lines_settings: Optional[dict] = {},
        text_settings: Optional[dict] = {},
        save=False, 
        path_fig='cwd'
    ):
    """Plot the delta values of choosen colorimetric coordinates.

    Parameters
    ----------
    data : pd.DataFrame
        _description_
    
    stdev : Optional[bool], optional
        _description_, by default True
    
    data_settings : Optional[dict], optional
        _description_, by default {}
    
    figure_settings : Optional[dict], optional
        _description_, by default {}
    
    legend_settings : Optional[dict], optional
        _description_, by default {}
    
    lines_settings : Optional[dict], optional
        _description_, by default {}
    
    text_settings : Optional[dict], optional
        _description_, by default {}
    
    save : bool, optional
        _description_, by default False
    
    path_fig : str, optional
        _description_, by default 'cwd'

    Returns
    -------
    _type_
        _description_

    Raises
    ------
    ValueError
        _description_
    ValueError
        _description_
    ValueError
        _description_
    """

    # Extract the data settings
    dose_unit = data_settings.get('dose_unit', 'He')
        
    # Extract the legend settings    
    legend_labels = legend_settings.get('labels', [])
    legend_fontsize = legend_settings.get('fontsize', '22')
    legend_position = legend_settings.get('position', 'in')
    legend_title = legend_settings.get('title', None)
    legend_ncols = lines_settings.get('ncols', 1)

    # Extract the lines settings
    lines_widths = lines_settings.get('lw', 2)
    lines_styles = lines_settings.get('ls', '-')
    lines_colors = lines_settings.get('colors', None)

    # Extract the figure settings
    title = figure_settings.get('title', '')
    xlabel = figure_settings.get('xlabel', None)
    ylabel = figure_settings.get('ylabel', None)
    xlim = figure_settings.get('xlim', 0)
    ylim = figure_settings.get('ylim', None)
    fontsize = figure_settings.get('fontsize', 24)
    fontsize_title = figure_settings.get('fontsize_title', 26)
    figsize = figure_settings.get('figsize', (15,9))

    # Extract the text settings
    texts = text_settings.get('text', [])
    texts_xy = text_settings.get('xy', [])
    texts_fontsize = text_settings.get('fontsize', 22)
        

    # Define possible linestyles for random selection
    possible_linestyles = ['-', '--', '-.', ':', (0, (3, 1, 1, 1)), (0, (5, 5))] * 5

    # Whether to remove the std values
    if not stdev:
        data = data.loc[:, data.columns.get_level_values('data_type') != 'std']
    
    
    # Determine the number of curves
    num_curves = (data.loc[:, data.columns.get_level_values('data_type') != 'std']).shape[1]    
    meas_ids = data.columns.get_level_values('meas_id').unique()
        
    
    # Handle line styles
    if lines_styles == 'random':
        # Ensure we have enough unique linestyles
        if num_curves > len(possible_linestyles):
            raise ValueError("Number of curves exceeds the number of available linestyles.")
        # Randomly select unique linestyles
        selected_linestyles = random.sample(possible_linestyles, num_curves)
    elif isinstance(lines_styles, list):
        if len(lines_styles) < num_curves:
            raise ValueError("Length of 'ls' list must be greater or equal to the number of curves.")
        selected_linestyles = lines_styles    
    else:
        # Use the same linestyle for all curves
        selected_linestyles = [lines_styles] * num_curves
    
    # Handle line widths
    if isinstance(lines_widths, list):
        if len(lines_widths) < num_curves:
            raise ValueError("Length of 'lw' list must be greater or equal to the number of curves.")
        selected_lw = lines_widths
    else:
        # Use the same linewidth for all curves
        selected_lw = [lines_widths] * num_curves

    # Handle line colors
    if isinstance(lines_colors, list):
        
        lines_colors = lines_colors

    elif isinstance(lines_colors, str):
        lines_colors = [lines_colors] * num_curves
    
    elif lines_colors == None:
        lines_colors = [None] * num_curves
    
    
    
    # Set the observer and illuminant
    observer = colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1964 10 Degree Standard Observer"] 
    illuminant = colour.SDS_ILLUMINANTS['D65'] 
    d65 = colour.CCS_ILLUMINANTS["cie_10_1964"]["D65"]


    # Retrieve the colorimetric coordinates
    coordinates = data[meas_ids[0]].columns.get_level_values(level='coordinate').unique()
    
    
    # Apply the seaborn aesthetics
    sns.set_theme(context='paper', font='serif', palette='colorblind')


    # Create the figure
    fig, ax = plt.subplots(1,1, figsize=figsize)

    
    # Set the list of labels
    if len(legend_labels) == 0:
        legend_labels = ['none'] * num_curves
   
    elif len(legend_labels) != num_curves:
        print('The number of given legend labels is different than the number of curves. Please make sure that both are equal.')
        #return
    
        
    # Plot the spectra
    i = 0
    
    for meas_id in meas_ids:

        df_meas = data[meas_id].dropna(axis=0)
        
        for coordinate in coordinates:
            df_data = df_meas[coordinate]

            
            x = df_data.index
            y = df_data.iloc[:,0].values

            ax.plot(x,y, ls=selected_linestyles[i], lw=selected_lw[i], color=lines_colors[i], label=legend_labels[i])

            if 'std' in df_data.columns and stdev == True:
                y_std = df_data['std']

                ax.fill_between(x, y+y_std, y-y_std, color='0.75', alpha=0.5, ec='none')

            i = i + 1

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    
    # Set the size of axes tickslabels
    ax.xaxis.set_tick_params(labelsize=fontsize)
    ax.yaxis.set_tick_params(labelsize=fontsize)

    # Set the labels of the x and y axes
    if xlabel == None:
        ax.set_xlabel(x_labels[dose_unit], fontsize=fontsize)
    else:
        ax.set_xlabel(xlabel, fontsize=fontsize)

    if ylabel == None:

        if len(coordinates) == 1:
            ax.set_ylabel(labels_eq[coordinates[0]], fontsize=fontsize)

        else:
            ax.set_ylabel('Colorimetric differences ($\Delta$)', fontsize=fontsize)
    
    else:
        ax.set_ylabel(ylabel, fontsize=fontsize)
    
    # Define title
    if title != 'none':
        ax.set_title(title, fontsize=fontsize_title)
        

    # Create and define the legend    
    if legend_labels[0] != 'none' and len(legend_labels) < 19:

        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles)) 
        
        if legend_position == 'in':
                         
            ax.legend(by_label.values(), by_label.keys(), ncol=legend_ncols, fontsize=legend_fontsize, title=legend_title, title_fontsize=legend_fontsize, loc='upper left', framealpha=0.5)

        elif legend_position == 'out':
        
            ax.legend(by_label.values(), by_label.keys(), loc='upper left', ncol=1, fontsize=legend_fontsize, title=legend_title, title_fontsize=legend_fontsize, bbox_to_anchor=(1, 1)) 


    # Insert texts
    if isinstance(texts, str):
        texts = [texts]

    if isinstance(texts_xy, tuple):
        texts_xy = [texts_xy]

    if len(texts) > 0:
        if len(texts) == len(texts_xy):
            for text, xy in zip(texts, texts_xy):
                ax.annotate(text,xy, fontsize=texts_fontsize)

        else:
            print('Processed aborted. The number of text value should be equal to the number of text position.')
            return

    
    # Remove white margins
    plt.tight_layout()

    
    # Save the figure
    if save == True:
        if path_fig == 'cwd':
            path_fig = f'{os.getcwd()}/dE.png'                    
            
        fig.savefig(path_fig,dpi=300, facecolor='white', bbox_inches="tight") 

    
    # Display the figure
    plt.show()

    return





    '''
    # define y-std values
    if yerr is None:
        yerr = []
        for ele in data:
            yerr.append([np.zeros(len(x)) for x in ele])

    
    # define the color of the lines
    if colors is None:
        colors = [[colors] * len(coordinates)] * len(data)

    elif colors == 'default':
        colors = [[colors_dic[x] for x in coordinates]] * len(data)

    elif isinstance(colors, str):
        colors = [[colors] * len(coordinates)] * len(data)

    elif type(colors) == list:      
        if len(coordinates) == 1:
            colors = [len(coordinates)*[x] for x in colors] 
        else:
            colors = [colors] * len(data) 


    # define the width of the lines
    if lw == 'default':
        list_lw = [[lw_dic[x] for x in coordinates]] * len(data)  

    elif isinstance(lw, int):
        list_lw = [[lw] * len(coordinates)] * len(data)

    elif isinstance(lw, list):
        if len(coordinates) == 1:
            list_lw = [len(coordinates)*[x] for x in lw] 
        else:
            list_lw = [lw] * len(data)
    
    
    
    # check whether the length of the data matches the length of the dose_unit and coordinates lengths
    for d in data:
        if len(dose_unit + coordinates) != len(d):
            print('The length of each data objects should correspond to sum of the x and y units.')
            return       

        else:
            pass         
    
        
    # set the labels of the legend
    if len(legend_labels) == 0:
        legend_labels = ['none'] * len(data)

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
        

    
    # Set the aesthetics of the figure
    sns.set_theme(context='paper', font='serif', palette='colorblind') 
    
    # Plot with a single x-axis, ie. 1 light energy unit
    if len(dose_unit) == 1:

        # create an empty figure
        fig, ax1 = plt.subplots(1,1, figsize=figsize)

        
        # define the random linestyles
        if ls == 'random':
            plt.rcParams['axes.prop_cycle'] = ("cycler('ls', ['-', '--', ':', '-.'])")
            ax1.set_prop_cycle(ls = ["-","--","-.",":"])
        elif isinstance(ls, list):
            list_ls = [[x] for x in ls]
        
        for d,s,label,ls,lw,color in zip(data,yerr,legend_labels,list_ls,list_lw,colors):

            x = d[0]            
            
            for y,s_val,l,ls_val,lw_val,c in zip(d[1:],s,label,ls,lw,color):
                print(c)
               
                if ls == 'random':
                    ax1.plot(x, y, lw=lw_val, color=c, label=l)
                else:
                    ax1.plot(x, y, lw=lw_val, ls=ls_val, color=c, label=l)
                
                ax1.fill_between(x, y+s_val, y-s_val, alpha=0.5, color='0.75', ec='none')

        handles, list_labels = ax1.get_legend_handles_labels()        
        unique = [(h, l) for i, (h, l) in enumerate(zip(handles, list_labels)) if l not in list_labels[:i]]        
            
        ax1.legend(*zip(*unique), fontsize=legend_fontsize, title=legend_title, title_fontsize=legend_fontsize, loc='best', ncols=legend_columns)

        ax1.set_xlim(0)

        ax1.xaxis.set_tick_params(labelsize=fontsize)
        ax1.yaxis.set_tick_params(labelsize=fontsize)

        ax1.set_xlabel(x_labels[dose_unit[0]], fontsize=fontsize)

        if len(coordinates) == 1:
            ax1.set_ylabel(labels_eq[coordinates[0]], fontsize=fontsize)

        else:
            ax1.set_ylabel('Colorimetric differences ($\Delta$)', fontsize=fontsize)


        #ax1.annotate('BW1', (2.08,3.75), fontsize=fontsize-3)
        #ax1.annotate('BW2', (2.08,1.35), fontsize=fontsize-3)
        #ax1.annotate('BW3', (2.08,0.5), fontsize=fontsize-3)
    '''


        


 


    '''
        if legend == 'coordinates':
            
            list_objects = sorted(set(data.columns.get_level_values(0)))        

            for object in list_objects:
                d = data[object].dropna()            
                x = d.iloc[:,0]

                
                for col in d.iloc[:,1:].columns:
                    y = d[col]
                    
                    ax.plot(x,y, color=colors_dic[col], label=col)

            handles, labels = ax.get_legend_handles_labels()
            labels = [labels_eq[x] for x in labels]
            unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
            
            ax.legend(*zip(*unique), fontsize=fontsize)

        
        elif legend == 'objects':

            list_objects = sorted(set(data.columns.get_level_values(0)))
            


            for object in list_objects:
                d = data[object].dropna()
                coordinate = d.columns[1]

                x = d.iloc[:,0]
                y = d.iloc[:,1]

                ax.plot(x,y, label=object)

                ax.legend(fontsize=fontsize)        

        
    
    
        ax.xaxis.set_tick_params(labelsize=fontsize)
        ax.yaxis.set_tick_params(labelsize=fontsize)

        #ax.set_xlabel(x_labels[x_scale[0]], fontsize=fontsize)

        ax.set_xlim(0)

        
        #plt.legend()
        plt.tight_layout()
        plt.show()
    

    ax1.set_title(title, fontsize=fontsize)
    plt.tight_layout()
    
    if save == True:
        if path_fig == 'cwd':
            path_fig = f'{os.getcwd()}/dE.png'                    
            
        fig.savefig(path_fig,dpi=300, facecolor='white')         

    if len(dose_unit) == 1: 
        return plt, ax1
    else:
        return plt, ax1, ax2
    '''


def spectra(
        data: pd.DataFrame,        
        stdev:Optional[bool] = True,        
        data_settings: Optional[dict] = {},
        figure_settings: Optional[dict] = {},
        legend_settings: Optional[dict] = {},
        lines_settings: Optional[dict] = {},  
        text_settings: Optional[dict] = {},      
        remove_last_xtick:Optional[bool] = False, 
        text:Optional[str] = '',
        text_xy:Optional[tuple] = (0.02, 0.03), 
        save=False, 
        path_fig='cwd',
        *args, **kwargs):
    
    
    # Extract the data settings    
    derivation = data_settings.get('derivation', False)    
    data_mode = data_settings.get('mode', 'R')     
    
    
    # Extract the legend settings    
    legend_labels = legend_settings.get('labels', [])
    legend_fontsize = legend_settings.get('fontsize', '22')
    legend_position = legend_settings.get('position', 'in')
    legend_title = legend_settings.get('title', None)

    # Extract the lines settings
    lines_widths = lines_settings.get('lw', 2)
    lines_styles = lines_settings.get('ls', '-')
    lines_colors = lines_settings.get('colors', 'none')
    
    # Extract the figure settings
    title = figure_settings.get('title', '')
    xlabel = figure_settings.get('xlabel', 'Wavelength $\lambda$ (nm)')
    ylabel = figure_settings.get('ylabel', 'Reflectance factor')
    xlim = figure_settings.get('xlim', None)
    ylim = figure_settings.get('ylim', None)
    fontsize = figure_settings.get('fontsize', 24)
    fontsize_title = figure_settings.get('fontsize_title', 26)
    figsize = figure_settings.get('figsize', 'default')

    # Extract the text settings
    text = text_settings.get('text', '')
    text_fontsize = text_settings.get('fontsize', '13')
    text_xy = text_settings.get('xy', ())

    if text != '':
        text_xy = (0.01,0.03)
        
    
    # Define possible linestyles for random selection
    possible_linestyles = ['-', '--', '-.', ':', (0, (3, 1, 1, 1)), (0, (5, 5))] * 5


    # Determine the number of curves
    num_curves = (data.loc[:, data.columns.get_level_values('data_type') != 'std']).shape[1]  
    meas_ids = data.columns.get_level_values('meas_id').unique()
        
    
    # Handle line styles
    if lines_styles == 'random':
        # Ensure we have enough unique linestyles
        if num_curves > len(possible_linestyles):
            raise ValueError("Number of curves exceeds the number of available linestyles.")
        # Randomly select unique linestyles
        selected_linestyles = random.sample(possible_linestyles, num_curves)
    elif isinstance(lines_styles, list):
        if len(lines_styles) < num_curves:
            raise ValueError("Length of 'ls' list must be greater or equal to the number of curves.")
        selected_linestyles = lines_styles
    else:
        # Use the same linestyle for all curves
        selected_linestyles = [lines_styles] * num_curves
    
    # Handle line widths
    if isinstance(lines_widths, list):
        if len(lines_widths) < num_curves:
            raise ValueError("Length of 'lw' list must be greater or equal to the number of curves.")
        selected_lw = lines_widths
    else:
        # Use the same linewidth for all curves
        selected_lw = [lines_widths] * num_curves

    
    # Set the colour lines

    if lines_colors == 'none':
        lines_colors = [None] * num_curves

    elif lines_colors == 'sample':

        return data



    # Set the observer and illuminant
    observer = colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1964 10 Degree Standard Observer"] 
    illuminant = colour.SDS_ILLUMINANTS['D65'] 
    d65 = colour.CCS_ILLUMINANTS["cie_10_1964"]["D65"]
    
    # Apply the seaborn aesthetics
    sns.set_theme(context='paper', font='serif', palette='colorblind')
    
    # Set the figure size 
    if legend_position == 'out' and figsize == 'default':
        figsize = (20,8)

    elif legend_position == 'in' and figsize == 'default':
        figsize = (16,8)

    # Create the figure
    fig, ax = plt.subplots(1,1, figsize=figsize)
    
    # Define the wavelength range of the data
    if isinstance(xlim, tuple):
        data = data.loc[xlim[0]:xlim[1]]

    
    # Set the list of labels
    if len(legend_labels) == 0:
        legend_labels = ['none'] * len(data)
   
    elif len(legend_labels) < num_curves:
        print('The number of given legend labels is smaller than the number of curves. Please make sure that both are equal.')
        #return
    
        
    # Plot the spectra
    i = 0
    for meas_id in meas_ids:

        df_meas = data[meas_id]
        light_doses = sorted(set(df_meas.columns.get_level_values(0)))
        
        for light_dose in light_doses:
            df_data = df_meas[light_dose]

            wavelengths = df_data.index
            reflectance = df_data.iloc[:,0]
        
            # Drop NaN values
            valid_indices = ~reflectance.isna()
            wavelengths = wavelengths[valid_indices]
            reflectance = reflectance[valid_indices]

            if 'std' in df_data.columns:
                std_values = df_data['std']

            else:
                std_values = np.array([0] * len(wavelengths))

            
            label = legend_labels[i] if i < len(legend_labels) else None
            
            ax.plot(wavelengths, reflectance, lw=selected_lw[i], ls=selected_linestyles[i], color=lines_colors[i], label=label)

            if stdev:
                ax.fill_between(wavelengths, reflectance-std_values, reflectance+std_values, color='0.75', alpha=0.5, ec='none')

            i = i + 1

    
    # Define the axes limits
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    
    # Define x-axis label
    ax.set_xlabel(xlabel, fontsize=fontsize)

    
    # Define y-axis label
    if derivation == False and data_mode.upper() == 'R':
        ax.set_ylabel('Reflectance factor', fontsize=fontsize)
    elif derivation == False and data_mode.lower() == 'dr':
        ax.set_ylabel('Reflectance difference', fontsize=fontsize)
    elif derivation == False and data_mode.upper() == 'A':
        ax.set_ylabel('Absorbance', fontsize=fontsize)
    elif derivation == True and data_mode.upper() == 'A':
        ax.set_ylabel(r'$\frac{dA}{d\lambda}$', fontsize=fontsize+10)
    else:
        ax.set_ylabel(r'$\frac{dR}{d\lambda}$', fontsize=fontsize+10)
    
    
    # Set the size of axes tickslabels
    ax.xaxis.set_tick_params(labelsize=fontsize)
    ax.yaxis.set_tick_params(labelsize=fontsize)

    
    # Define title
    if title != 'none':
        ax.set_title(title, fontsize=fontsize_title)

    
    # Insert a text box
    if text != '' or text == 'none':
        props = dict(boxstyle='round', facecolor='white', alpha=0.7)
        ax.text(text_xy[0],text_xy[1],text,transform=ax.transAxes,fontsize=text_fontsize,verticalalignment='top', bbox=props)
    

    # Create and define the legend
    if len(legend_labels) > 6:
        ncols = 2
    else:
        ncols = 1

    if legend_labels[0] != 'none' and len(legend_labels) < 19:

        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles)) 
        
        if legend_position == 'in':
                         
            ax.legend(by_label.values(), by_label.keys(), ncol=ncols, fontsize=legend_fontsize, title=legend_title, title_fontsize=legend_fontsize)

        elif legend_position == 'out':
        
            ax.legend(by_label.values(), by_label.keys(), loc='upper left', ncol=1, fontsize=legend_fontsize, title=legend_title, title_fontsize=legend_fontsize, bbox_to_anchor=(1, 1)) 


    # Remove white margins
    plt.tight_layout()

    
    # Save the figure
    if save == True:
        if path_fig == 'cwd':
            path_fig = f'{os.getcwd()}/SP.png'                    
            
        fig.savefig(path_fig,dpi=300, facecolor='white', bbox_inches="tight") 

    text_settings = {}
    lines_settings = {}
    legend_settings = {}
    
    
    # Display the figure
    plt.show()

    
    
    return


    '''
    for i, column in enumerate(data.columns):
        wavelengths = data.index
        reflectance = data[column]
        
        # Drop NaN values
        valid_indices = ~reflectance.isna()
        wavelengths = wavelengths[valid_indices]
        reflectance = reflectance[valid_indices]

        label = legend_labels[i] if i < len(legend_labels) else None

        if derivation:
            # Compute derivation if needed
            derivation_data = np.gradient(reflectance) / np.gradient(wavelengths)
            ax.plot(wavelengths, derivation_data, label=label, linewidth=selected_lw[i], linestyle=selected_linestyles[i], color=colors[i] if isinstance(colors, list) else colors)
        else:
            ax.plot(wavelengths, reflectance, label=label, linewidth=selected_lw[i], linestyle=selected_linestyles[i], color=colors[i] if isinstance(colors, list) else colors)
    '''
    


    

    
    # Set the list of colors
    if isinstance(colors, list) or isinstance(colors, np.ndarray):        
        colors = colors        
        
    elif colors == None:
        colors = [None] * len(data)
    
    elif colors == 'sample':
        colors = ['sample'] * len(data)
    
    # Set the linestyle
    if isinstance(ls, str):
        ls = [ls] * len(data)

    # Set the linewidth
    if isinstance(lw, int):        
        lw = [lw] * len(data)
    
    # Set the std values
    if len(stds) == 0:        
        stds = [np.zeros(len(x[1])) for x in data]
        
         
    # Initiate a for loop to plot the data    
    for i, (d,s) in enumerate(zip(data,stds)):
        
        df_sp = pd.DataFrame(data=[d[1],s], columns=d[0], index=['sp','std']).T

        # Index data according the x_range values
        if x_range not in [(), None]:            
            df_sp = df_sp.loc[x_range[0]:x_range[1]]

        # Get the wavelengths and spectral values
        wl = df_sp.index.values
        sp = df_sp.iloc[:,0].values
        std = df_sp['std'].values        

        # Define color of the curve
        if isinstance(colors, list) or isinstance(colors, np.ndarray):
            color = colors[i]
        
        elif colors[i] == 'sample':                      
            sd = colour.SpectralDistribution(sp,wl)  
            XYZ = colour.sd_to_XYZ(sd,observer, illuminant=illuminant) 
            srgb = colour.XYZ_to_sRGB(XYZ / 100, illuminant=d65).clip(0, 1)
            color = np.array(srgb)            
        
               
        # Plot the data       
        ax.plot(wl,sp, color=color, lw=lw[i], ls=ls[i], label=legend_labels[i])
        ax.fill_between(wl, sp-std,sp+std, alpha=0.5, color='0.75', ec='none')
        

    
    
    # Define x-axis limits    
    if x_range not in [(), None]:
        ax.set_xlim(x_range[0],x_range[1])
        
    # Get current x-ticks
    xticks = plt.gca().get_xticks()
    
    # Remove the last tick if it exists
    if remove_last_xtick and len(xticks) > 0:
        xticks = xticks[:-1]
        plt.xticks(xticks)
       
    
    
             

    


def swatches_circle(data, data_type:Optional[str] = 'Lab', orientation:Optional[str] = 'horizontal', light_doses:Optional[list] = [0.5,1,2,5,15], JND:Optional[list] = [], dose_unit:Optional[str] = 'Hv', dE:Optional[bool] = True, museum_exposure:Optional[tuple] = (), fontsize: Optional[int] = 40, save:Optional[bool] = False, path_fig:Optional[str] = 'cwd', title:Optional[str] = None, background_grey: Optional [float] = 0.85, circle_h:Optional[float] = 0):

    if len(museum_exposure) != 0:
        museum_exposure_scales = {'h': f'Duration exposure (hours) ($E_v$ = {museum_exposure[0]} lux) ', 'd': 'Duration exposure (days)', 'y': 'Duration exposure (years)'} 
        xlabel = museum_exposure_scales[museum_exposure[1]]
        light_doses = ((np.array(light_doses) * 1e6) / museum_exposure[0]).astype(int)
    
    elif list(set([len(x) for x in data]))[0] == len(JND):
        xlabel = 'Just noticeable difference (JND)'

    elif list(set([len(x) for x in data]))[0] == len(light_doses):
        if dose_unit == "Hv":
            xlabel = 'Exposure dose $H_v$ (Mlxh)'
        elif dose_unit == "He":
            xlabel = 'Radiant exposure $H_e$ ($MJ/m^2$)'
    else:
        print('Plotting aborted ! The length of data values is not equal to the length of light_doses or JND values.')
        return
    
    if data_type.lower() == 'lab':          
        data_srgb = [colour.XYZ_to_sRGB(colour.Lab_to_XYZ(x), D65).clip(0, 1) for x in data]
    else:
        data_srgb = data
    
    if dE:
        if data_type.lower() == 'lab':
            dE_values = [np.round(colour.delta_E(x[0],x[1:]),1) for x in data]                      

        else:
            print('Plot aborted. Please provide the Lab values instead.')
            return None
    else:
        dE_values = [[''] * (len(light_doses)-1)] * len(data_srgb)

    if isinstance(title, list):
        title = title
    
    elif title == None:
        title = [''] * len(data_srgb)
    
    elif isinstance(title, str):
        title = [title] * len(data_srgb)   
    
    nb = 1

    for d_srgb,dE_val, title_value in zip(data_srgb, dE_values, title):

        N = len(d_srgb)

        if orientation == 'horizontal':

            fig, ax = plt.subplots(1,1, figsize=((N)*5,7))   
        
            ax.set_facecolor((background_grey,background_grey,background_grey))
            fig.patch.set_facecolor((background_grey, background_grey, background_grey))

            if isinstance(title, str):
                title_space = 0.05
            else:
                title_space = 0

            if dE:
                y = 1
                h = 0.7 + title_space + circle_h
            else:
                y =0.9
                h = 0.6 + title_space + circle_h

            cp_init = matplotlib.patches.Rectangle((0.05, 0.0), 0.9, y, edgecolor='None', fc=d_srgb[0], lw=2)
            ax.add_patch(cp_init)

            i = 0
            for d in d_srgb[1:]:
                cp = matplotlib.patches.Ellipse(xy=(1/N + i, 0.5), width=0.6/(N-1), height=h, edgecolor='None', fc=d, lw=2)
                ax.add_patch(cp)
                i = i + (1/N)

            ax.xaxis.set_ticks_position(position='bottom')
            ax.set_xticks(np.linspace(0,1,N+1)[1:-1])        
            ax.set_xticklabels(light_doses[1:])
            ax.set_yticks([])

            ax.xaxis.set_tick_params(labelsize=fontsize)    
            ax.set_xlabel(xlabel, fontsize=fontsize)

            ax.set_title(title_value, fontsize=fontsize+2)

            if dE:
                ax_top = ax.secondary_xaxis('top')
                ax_top.set_xlabel('Estimated $\Delta E_{00}$ values', fontsize=fontsize)
                ax_top.set_xticks(np.linspace(0,1,N+1)[1:-1]) 
                ax_top.set_xticklabels(dE_val)
                ax_top.xaxis.set_tick_params(labelsize=fontsize) 
                ax_top.spines['top'].set_visible(False)                 
                ax_top.xaxis.labelpad = 20
        
        
        elif orientation == 'vertical':

            fig, ax = plt.subplots(1,1, figsize=(6, (N-1)*4)) 

            ax.set_facecolor((background_grey,background_grey,background_grey))
            fig.patch.set_facecolor((background_grey, background_grey, background_grey))

            if isinstance(title, str):
                title_space = 0
            else:
                title_space = 0

            if dE:
                y = 0.9
                h = 0.7 + title_space
            else:
                y = 0.9
                h = 0.6 + title_space

            cp_init = matplotlib.patches.Rectangle((0.0, 0.05), 1, y, edgecolor='None', fc=d_srgb[0], lw=2)
            ax.add_patch(cp_init)

            i = 0
            for d in d_srgb[1:][::-1]:
                cp = matplotlib.patches.Ellipse(xy=(0.5, 1/N + i), width=h, height=0.6/(N-1), edgecolor='None', fc=d, lw=2)
                ax.add_patch(cp)
                i = i + (1/N)

            ax.yaxis.set_ticks_position(position='left')
            ax.set_yticks(np.linspace(0,1,N+1)[1:-1])        
            ax.set_yticklabels(light_doses[1:][::-1])
            ax.set_xticks([])

            ax.yaxis.set_tick_params(labelsize=fontsize)    
            ax.set_ylabel(xlabel, fontsize=fontsize)

            ax.set_title(title_value, fontsize=fontsize+2, y=0.97)

            if dE:
                ax_top = ax.secondary_yaxis('right')
                ax_top.set_ylabel('Estimated $\Delta E_{00}$ values', fontsize=fontsize)
                ax_top.set_yticks(np.linspace(0,1,N+1)[1:-1]) 
                ax_top.set_yticklabels(dE_val[::-1])
                ax_top.yaxis.set_tick_params(labelsize=fontsize) 
                ax_top.spines['right'].set_visible(False) 
                ax_top.tick_params(axis='x', which='major', pad=20)

        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        ax.grid(False)       

        plt.tight_layout()
            
        if save == True:
            if path_fig == 'cwd':
                path_fig = f'{os.getcwd()}/MFT_{str(nb).zfill(2)}_SW.png'  
                nb = nb + 1  
                             
                
            fig.savefig(path_fig,dpi=300, facecolor=(background_grey, background_grey, background_grey)) 
        
        plt.show()


def swatches_rectangle(data, data_type:Optional[str] = 'Lab', labels:Optional[list] = [], bottom_scale:Optional[str] = 'JND', top_labels:Optional[dict] = None, fontsize: Optional[int] = 24, side_annotations:Optional[tuple] = ('',''), colorbar:Optional[bool] = False, save:Optional[bool] = False, path_fig:Optional[str] = 'cwd', title:Optional[str] = None, background_grey: Optional [float] = 0.85): 

    
    if data_type.lower() == 'lab':          
        data_srgb = [(colour.XYZ_to_sRGB(colour.Lab_to_XYZ(x[0]), D65).clip(0, 1), colour.XYZ_to_sRGB(colour.Lab_to_XYZ(x[1]), D65).clip(0, 1)) for x in data]
    else:
        data_srgb = data

    # Number of data
    N = len(data_srgb)   
          
    # Length of each colour swatch
    L_sw = (1 - ((N+1)*0.05)) / N
    
    i = 0
    j = 0.05 + (L_sw/2)

    # Define empty labels
    if len(labels) == 0:
        labels = [''] * len(data)

    # Define the figure
    fig, ax = plt.subplots(1,1, figsize=((N)*5,6))        
    ax.set_facecolor((background_grey,background_grey,background_grey))
    fig.patch.set_facecolor((background_grey, background_grey, background_grey))
    
    # Empty dict to record the x-axis tick positions 
    positions_ticks = []

    # Plot each data
    for srgb, label in zip(data_srgb, labels):

        cp_1 = matplotlib.patches.Rectangle((0.05+i, 0.5), L_sw, 0.5, color=srgb[0])
        cp_2 = matplotlib.patches.Rectangle((0.05+i, 0), L_sw, 0.5, color=srgb[1])
        positions_ticks.append(j)
        
        i = i + 0.05 + L_sw
        j = j + (0.05 + L_sw)

        ax.add_patch(cp_1)
        ax.add_patch(cp_2)
        
    
    # Set the bottom xticks and label
    ax.xaxis.set_ticks_position(position='bottom')     
    ax.set_xticks(positions_ticks)      
    ax.set_xticklabels(labels)
    ax.xaxis.set_tick_params(labelsize=fontsize) 
    ax.set_xlabel('Samples', fontsize=fontsize)

    
    # Remove the yticks
    ax.set_yticks([])
    
    
    # Add a dash line on the left side     
    ax.axhline(0.5, xmin=0, xmax=0.04, ls='--', color='k')

    
    # Insert text on the left side
    top_text = side_annotations[0]
    ax.annotate(text=top_text, xy=(0.01,0.76) , rotation=90, va='center', fontsize=fontsize-2)
    
    bottom_text = side_annotations[1]
    ax.annotate(text=bottom_text, xy=(0.01,0.25) , rotation=90, va='center', fontsize=fontsize-2)

    # Whether to add a title
    ax.set_title(title, fontsize=fontsize+2, y=1.21)
    
    # Remove the grid
    ax.grid(False)

    
    # Configure the top labels
    if top_labels != None:
        ax_top = ax.secondary_xaxis('top')
        ax_top.set_xlabel(labels_eq[list(top_labels.keys())[0]], fontsize=fontsize)
        ax_top.set_xticks(positions_ticks) 
        ax_top.set_xticklabels(list(top_labels.values())[0])
        ax_top.xaxis.set_tick_params(labelsize=fontsize) 
        ax_top.spines['top'].set_visible(False)     
        
    
    # Configure the axes spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    
    # Optional: Add a custom legend for basic colors
    if colorbar:
        basic_colors = ['red', 'green', 'blue', 'cyan', 'magenta', 'yellow', 'black', 'white']
        for i, color in enumerate(basic_colors):
            rect = matplotlib.patches.Rectangle((0.975, 0.1+i/10), 0.024, 0.1, facecolor=color, edgecolor='black')
            ax.add_patch(rect)

    
    plt.tight_layout()
            
    # Whether to save the figure
    if save == True:        
        fig.savefig(path_fig,dpi=300, facecolor=(background_grey, background_grey, background_grey)) 
        
    plt.show()