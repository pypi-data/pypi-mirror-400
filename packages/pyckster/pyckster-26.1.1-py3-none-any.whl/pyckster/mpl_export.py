#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Matplotlib export utilities for seismic data visualization.

This module provides functions to export seismic plots to various image formats
using matplotlib's non-interactive 'Agg' backend.

Copyright (C) 2024, 2025 Sylvain Pasquet
Email: sylvain.pasquet@sorbonne-universite.fr

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for image export
import matplotlib.pyplot as plt
import numpy as np


def export_mpl_plot(output_file, dpi=150):
    """
    Export current matplotlib figure to image file.
    
    Supports PNG, PDF, JPEG, and TIFF formats based on file extension.
    
    Parameters
    ----------
    output_file : str
        Path to save image file. Format is determined by extension:
        - .png: PNG format
        - .pdf: PDF format
        - .jpg/.jpeg: JPEG format
        - .tif/.tiff: TIFF format
    dpi : int, optional
        Resolution in dots per inch, default 150
    
    Returns
    -------
    bool
        True if export successful
    
    Raises
    ------
    ValueError
        If file extension is not supported
    """
    ext = output_file.lower().split('.')[-1]
    
    valid_formats = ['png', 'pdf', 'jpg', 'jpeg', 'tif', 'tiff']
    if ext not in valid_formats:
        raise ValueError(f"Unsupported format '{ext}'. Valid formats: {', '.join(valid_formats)}")
    
    plt.savefig(output_file, dpi=dpi, bbox_inches='tight')
    plt.close()
    
    return True


def export_seismogram_to_mpl(output_file, data, time_vector, trace_positions, 
                            source_position=None, picks=None, 
                            title=None, normalize=True, gain=1.0, clip=True,
                            clip_percent=99, wiggle=True, fill_mode='Neg.',
                            color_map='seismic', dpi=150):
    """
    Export seismogram data to matplotlib image.
    
    Creates a seismic wiggle trace plot with optional picks and saves to file.
    Matches the processing logic from core.py plotSeismoWiggle method.
    
    Parameters
    ----------
    output_file : str
        Path to save image file
    data : 2D array
        Seismic data (time, trace)
    time_vector : 1D array
        Time values in milliseconds
    trace_positions : 1D array
        Trace positions in meters
    source_position : float, optional
        Source position in meters for display
    picks : 1D array, optional
        First-arrival pick times for each trace
    title : str, optional
        Plot title
    normalize : bool, optional
        Normalize each trace individually (True) or by global max (False), default True
    gain : float, optional
        Gain multiplier for trace amplitudes, default 1.0
    clip : bool, optional
        Whether to clip trace amplitudes, default True
    clip_percent : float, optional
        Percentile for amplitude clipping, default 99
    wiggle : bool, optional
        Show wiggle traces, default True
    fill_mode : str, optional
        Fill mode: 'Pos.' for positive or 'Neg.' for negative, default 'Neg.'
    color_map : str, optional
        Colormap for image, default 'seismic'
    dpi : int, optional
        Resolution in dots per inch, default 150
    
    Returns
    -------
    bool
        True if export successful
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Calculate trace amplitude scale (default to spacing between traces)
    if len(trace_positions) > 1:
        mean_spacing = np.mean(np.diff(trace_positions))
        trace_amp_scale = mean_spacing / 2.0
    else:
        trace_amp_scale = 1.0
    
    # Process normalization
    all_data = np.array(data, dtype=float)
    
    if normalize:
        # Normalize mode: each trace is normalized to its own max value
        data_normalized = all_data.copy()
        for i in range(data_normalized.shape[1]):
            trace = data_normalized[:, i]
            max_amp = np.max(np.abs(trace))
            if max_amp > 0:
                # Normalize to max value of 1 and scale by trace_amp_scale
                data_normalized[:, i] = (trace / max_amp) * trace_amp_scale * gain
            else:
                data_normalized[:, i] = trace * trace_amp_scale * gain
    else:
        # Non-normalize mode: all traces normalized by the same global max amplitude
        global_max_amp = np.max(np.abs(all_data))
        if global_max_amp > 0:
            data_normalized = (all_data / global_max_amp) * trace_amp_scale * gain
        else:
            data_normalized = all_data * trace_amp_scale * gain
    
    # Apply amplitude clipping
    if clip:
        data_normalized = np.clip(data_normalized, -trace_amp_scale, trace_amp_scale)
    
    # Create the image plot using normalized data without clipping for visualization
    data_plot = data_normalized.copy()
    vmax = np.percentile(np.abs(data_plot), clip_percent)
    
    # Plot image
    extent = [trace_positions[0], trace_positions[-1], 
             time_vector[-1], time_vector[0]]
    im = ax.imshow(data_plot, aspect='auto', cmap=color_map, 
                   extent=extent, vmin=-vmax, vmax=vmax, 
                   interpolation='bilinear')
    
    # Plot wiggle traces if requested
    if wiggle:
        for i in range(data_normalized.shape[1]):
            if i < len(trace_positions):
                pos = trace_positions[i]
                trace = data_normalized[:, i]
                
                # Calculate fill level (the baseline position)
                fill_level = pos
                
                # Add offset to trace for plotting
                x = trace + pos
                
                # Plot the wiggle trace
                ax.plot(x, time_vector, color='black', linewidth=0.5, alpha=0.7)
                
                # Determine which part to fill based on fill_mode
                if fill_mode == 'Pos.':
                    # Fill positive amplitudes (where x >= fill_level)
                    ax.fill_betweenx(time_vector, pos, x, 
                                   where=(x >= fill_level), 
                                   color='black', alpha=0.5)
                elif fill_mode == 'Neg.':
                    # Fill negative amplitudes (where x <= fill_level)
                    ax.fill_betweenx(time_vector, pos, x, 
                                   where=(x <= fill_level), 
                                   color='black', alpha=0.5)
    
    # Plot picks if provided
    if picks is not None:
        valid_picks = ~np.isnan(picks)
        if np.any(valid_picks):
            ax.plot(trace_positions[valid_picks], picks[valid_picks], 
                   'r+', markersize=8, markeredgewidth=1.5, label='First arrivals')
            ax.legend()
    
    # Mark source position if provided
    if source_position is not None:
        ax.axvline(source_position, color='red', linestyle='--', 
                  linewidth=2, alpha=0.7, label='Source')
    
    ax.set_xlabel('Position (m)', fontsize=12)
    ax.set_ylabel('Time (ms)', fontsize=12)
    if title:
        ax.set_title(title, fontsize=14)
    ax.grid(True, alpha=0.3)
    
    plt.colorbar(im, ax=ax, label='Normalized amplitude')
    plt.tight_layout()
    
    return export_mpl_plot(output_file, dpi=dpi)


def export_layout_to_mpl(output_file, trace_positions, trace_elevations,
                        source_positions, source_elevations,
                        title=None, show_labels=True, dpi=150):
    """
    Export survey layout (geometry) to matplotlib image.
    
    Creates a plot showing source and receiver positions with elevations.
    
    Parameters
    ----------
    output_file : str
        Path to save image file
    trace_positions : list of arrays
        List of trace position arrays (one per source)
    trace_elevations : list of arrays
        List of trace elevation arrays (one per source)
    source_positions : list
        List of source positions
    source_elevations : list
        List of source elevations
    title : str, optional
        Plot title
    show_labels : bool, optional
        Show station labels, default True
    dpi : int, optional
        Resolution in dots per inch, default 150
    
    Returns
    -------
    bool
        True if export successful
    """
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Plot receivers
    for i, (positions, elevations) in enumerate(zip(trace_positions, trace_elevations)):
        if positions is not None:
            ax.plot(positions, elevations, 'bv', markersize=8, 
                   label='Receivers' if i == 0 else '')
    
    # Plot sources
    valid_sources = [(pos, elev) for pos, elev in zip(source_positions, source_elevations) 
                     if pos is not None]
    if valid_sources:
        src_pos, src_elev = zip(*valid_sources)
        ax.plot(src_pos, src_elev, 'r*', markersize=12, label='Sources')
    
    # Add labels if requested
    if show_labels:
        # Label unique receivers
        all_receivers = set()
        for positions, elevations in zip(trace_positions, trace_elevations):
            if positions is not None:
                for pos, elev in zip(positions, elevations):
                    all_receivers.add((pos, elev))
        for i, (pos, elev) in enumerate(sorted(all_receivers)):
            ax.text(pos, elev + 1, f'R{i+1}', fontsize=8, ha='center', va='bottom')
        
        # Label sources
        for i, (pos, elev) in enumerate(valid_sources):
            ax.text(pos, elev - 1, f'S{i+1}', fontsize=8, ha='center', va='top', color='red')
    
    ax.set_xlabel('Position (m)', fontsize=12)
    ax.set_ylabel('Elevation (m)', fontsize=12)
    if title:
        ax.set_title(title, fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_aspect('equal', adjustable='box')
    plt.tight_layout()
    
    return export_mpl_plot(output_file, dpi=dpi)


def export_traveltime_to_mpl(output_file, trace_positions, picks, errors=None,
                           source_position=None, title=None, 
                           show_error_bars=True, dpi=150):
    """
    Export traveltime curve to matplotlib image.
    
    Creates a plot of first-arrival times vs. offset with optional error bars.
    
    Parameters
    ----------
    output_file : str
        Path to save image file
    trace_positions : 1D array
        Trace positions in meters
    picks : 1D array
        First-arrival pick times in milliseconds
    errors : 1D array, optional
        Pick uncertainties in milliseconds
    source_position : float, optional
        Source position in meters
    title : str, optional
        Plot title
    show_error_bars : bool, optional
        Display error bars if errors provided, default True
    dpi : int, optional
        Resolution in dots per inch, default 150
    
    Returns
    -------
    bool
        True if export successful
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Filter out NaN picks
    valid = ~np.isnan(picks)
    valid_positions = trace_positions[valid]
    valid_picks = picks[valid]
    
    # Calculate offsets if source position provided
    if source_position is not None:
        offsets = np.abs(valid_positions - source_position)
        xlabel = 'Offset (m)'
    else:
        offsets = valid_positions
        xlabel = 'Position (m)'
    
    # Plot picks with error bars if available
    if errors is not None and show_error_bars:
        valid_errors = errors[valid]
        ax.errorbar(offsets, valid_picks, yerr=valid_errors, 
                   fmt='bo', markersize=6, capsize=4, 
                   label='First arrivals with errors')
    else:
        ax.plot(offsets, valid_picks, 'bo', markersize=6, 
               label='First arrivals')
    
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel('Time (ms)', fontsize=12)
    if title:
        ax.set_title(title, fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Invert y-axis so time increases downward
    ax.invert_yaxis()
    
    plt.tight_layout()
    
    return export_mpl_plot(output_file, dpi=dpi)
