#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pick I/O utilities for reading and writing seismic picks in PyGimLi .sgt format.

This module provides functions to save and load first-arrival traveltime picks
in the PyGimLi .sgt format, which is widely used in seismic refraction processing.

Copyright (C) 2024, 2025 Sylvain Pasquet
Email: sylvain.pasquet@sorbonne-universite.fr

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import numpy as np


def save_picks_to_sgt(output_file, trace_positions, trace_elevations, 
                      source_positions, source_elevations, picks, errors):
    """
    Save picks to PyGimLi .sgt file format.
    
    The .sgt format stores station coordinates and source-geophone-time picks:
    - Header with number of stations and their (x, z) coordinates
    - Pick data with source index, geophone index, time, and error
    
    Parameters
    ----------
    output_file : str
        Path to save the .sgt file
    trace_positions : list of arrays
        List of trace position arrays (one per source)
    trace_elevations : list of arrays
        List of trace elevation arrays (one per source)
    source_positions : list
        List of source positions
    source_elevations : list
        List of source elevations
    picks : list of lists
        Nested list of pick times [source][trace]
    errors : list of lists
        Nested list of pick errors [source][trace]
    
    Returns
    -------
    int
        Number of picks saved
    
    Raises
    ------
    ValueError
        If no picks are available to save
    """
    # Get unique traces from list of trace arrays
    trace_pairs = []
    for sublist_position, sublist_elevation in zip(trace_positions, trace_elevations):
        if sublist_position is not None:
            for trace, elevation in zip(sublist_position, sublist_elevation):
                trace_pairs.append((trace, elevation))

    # Get unique sources
    source_pairs = [(source, elevation) 
                   for source, elevation in zip(source_positions, source_elevations) 
                   if source is not None]

    # Convert to numpy structured arrays
    trace_pairs = np.array(trace_pairs, dtype=[('position', float), ('elevation', float)])
    source_pairs = np.array(source_pairs, dtype=[('position', float), ('elevation', float)])

    # Concatenate and get unique stations
    all_pairs = np.concatenate((trace_pairs, source_pairs))
    stations = np.unique(all_pairs)

    # Get trace indices in station list
    trace_indices = [
        np.where((stations['position'] == trace_pair['position']) & 
                (stations['elevation'] == trace_pair['elevation']))[0][0] 
        for trace_pair in trace_pairs
    ]

    # Get source indices in station list
    source_indices = [
        np.where((stations['position'] == source_pair['position']) & 
                (stations['elevation'] == source_pair['elevation']))[0][0] 
        for source_pair in source_pairs
    ]

    # Count non-NaN picks
    picks_list = [pick for sublist in picks if sublist is not None for pick in sublist]
    n_picks = np.sum(~np.isnan(picks_list))

    if n_picks == 0:
        raise ValueError("No picks to save!")
    
    # Write .sgt file
    with open(output_file, 'w') as f:
        # Write number of stations
        f.write(f"{len(stations)} # shot/geophone points\n")
        f.write("# x\ty\n")
        for station in stations:
            x = station[0]
            y = station[1]
            f.write(f"{x}\t{y}\n")
        
        # Write number of picks
        f.write(f"{n_picks} # measurements\n")
        f.write("# s\tg\tt\terr\n")

        # Write pick data
        for i, pick_list in enumerate(picks):
            if pick_list is not None:
                for j, pick in enumerate(pick_list):
                    if not np.isnan(pick):
                        error = errors[i][j]
                        # Write source index, trace index, pick time, pick error
                        # Indices are 1-based in .sgt format
                        f.write(f"{source_indices[i] + 1}\t{trace_indices[j] + 1}\t{pick:.5f}\t{error:.5f}\n")
    
    return n_picks


def read_sgt_file(sgt_file, verbose=False):
    """
    Read PyGimLi .sgt file and parse stations and picks.
    
    Automatically detects coordinate format:
    - 2 columns: (x, z)
    - 3 columns: (x, y, z) or (x, z, 0) depending on which columns have values
    
    Automatically detects column order for picks using header comments.
    Supports various synonyms: s/src/source, g/geo/geophone/r/recv, t/time/tt, err/error/unc
    
    Parameters
    ----------
    sgt_file : str
        Path to .sgt file
    verbose : bool, optional
        Print debug information, default False
    
    Returns
    -------
    dict
        Dictionary containing:
        - 'stations': list of (x, y, z) tuples
        - 'picks': list of (source_idx, geophone_idx, time, error) tuples
        - 'n_stations': int
        - 'n_picks': int
    """
    with open(sgt_file, 'r') as f:
        # Read number of stations
        n_stations = int(f.readline().split('#')[0].strip())
        if verbose:
            print(f"Number of stations: {n_stations}")

        # Skip comment lines
        flag_comment = True
        while flag_comment:
            line = f.readline().strip()
            if '#' in line[0]:
                if verbose:
                    print(f"Comment: {line}")
                flag_comment = True
            else:
                flag_comment = False

        # Read station coordinates
        coords_list = []
        for i in range(n_stations):
            if i > 0:
                line = f.readline().strip()

            if verbose and (i < 5 or i > n_stations - 5):
                print(f"Reading station line: {line}")
        
            if line:
                parts = line.split()
                coords = [float(p) for p in parts]
                coords_list.append(coords)
        
        # Determine coordinate format
        stations = []
        if len(coords_list) > 0:
            n_cols = len(coords_list[0])
            
            if n_cols == 2:
                # 2 columns: (x, z) format
                for coords in coords_list:
                    stations.append((coords[0], 0.0, coords[1]))
                if verbose:
                    print(f"Detected 2-column format: (x, z)")
            
            elif n_cols == 3:
                # Check which columns have non-zero values
                col0_nonzero = any(abs(coords[0]) > 1e-10 for coords in coords_list)
                col1_nonzero = any(abs(coords[1]) > 1e-10 for coords in coords_list)
                col2_nonzero = any(abs(coords[2]) > 1e-10 for coords in coords_list)
                
                if verbose:
                    print(f"Column non-zero detection: col0={col0_nonzero}, col1={col1_nonzero}, col2={col2_nonzero}")
                
                if col0_nonzero and col1_nonzero and col2_nonzero:
                    # All 3 columns non-zero: (x, y, z)
                    for coords in coords_list:
                        stations.append((coords[0], coords[1], coords[2]))
                    if verbose:
                        print(f"Detected 3-column format: (x, y, z)")
                elif col0_nonzero and col1_nonzero and not col2_nonzero:
                    # Columns 0 and 1 non-zero: (x, z, 0) -> store as (x, 0, z)
                    for coords in coords_list:
                        stations.append((coords[0], 0.0, coords[1]))
                    if verbose:
                        print(f"Detected 3-column format: (x, z, 0)")

        # Read number of picks
        n_picks = int(f.readline().split('#')[0].strip())
        if verbose:
            print(f"Number of picks: {n_picks}")

        # Initialize default column indices (standard order: s g t err)
        s_ind = 0
        g_ind = 1
        t_ind = 2
        err_ind = 3

        # Read optional header comment lines to infer column order
        comment_lines = []
        while True:
            line = f.readline()
            if not line:
                line = ""
                break
            line = line.strip()
            if line and line[0] == '#':
                comment_lines.append(line)
                if verbose:
                    print(f"Comment: {line}")
                continue
            else:
                break

        # Parse comment lines to detect column order
        if comment_lines:
            synonyms = {
                's': 's', 'src': 's', 'source': 's',
                'g': 'g', 'geo': 'g', 'geophone': 'g', 'r': 'g', 'recv': 'g', 'receiver': 'g',
                't': 't', 'time': 't', 'tt': 't', 'pick': 't', 'tpick': 't',
                'err': 'err', 'error': 'err', 'unc': 'err', 'uncertainty': 'err', 'sigma': 'err'
            }
            best_fields = []
            for cl in comment_lines:
                cl_proc = cl[1:] if cl.startswith('#') else cl
                for sep in [',', ';', '|']:
                    cl_proc = cl_proc.replace(sep, ' ')
                tokens = [tok.strip().lower().strip(':') for tok in cl_proc.split()]
                fields = []
                for tok in tokens:
                    if tok in synonyms:
                        canon = synonyms[tok]
                        if len(fields) == 0 or fields[-1] != canon:
                            fields.append(canon)
                unique_fields = []
                for fcanon in fields:
                    if fcanon not in unique_fields:
                        unique_fields.append(fcanon)
                if len(unique_fields) > len(best_fields):
                    best_fields = unique_fields
            
            if best_fields:
                try:
                    if 's' in best_fields:
                        s_ind = best_fields.index('s')
                    if 'g' in best_fields:
                        g_ind = best_fields.index('g')
                    if 't' in best_fields:
                        t_ind = best_fields.index('t')
                    if 'err' in best_fields:
                        err_ind = best_fields.index('err')
                    if verbose:
                        print(f"Detected column order from header: {best_fields}")
                        print(f"Using indices: s={s_ind}, g={g_ind}, t={t_ind}, err={err_ind}")
                except (ValueError, IndexError) as e:
                    if verbose:
                        print(f"Error parsing column order: {e}, using defaults")

        # Read picks
        picks = []
        for i in range(n_picks):
            if i == 0 and line:
                # Use the line we already read
                pass
            else:
                line = f.readline().strip()
            
            if line:
                parts = line.split()
                if len(parts) >= 4:
                    # Parse based on detected column order
                    source_idx = int(parts[s_ind])
                    geophone_idx = int(parts[g_ind])
                    time = float(parts[t_ind])
                    error = float(parts[err_ind])
                    picks.append((source_idx, geophone_idx, time, error))

    return {
        'stations': stations,
        'picks': picks,
        'n_stations': n_stations,
        'n_picks': n_picks
    }


def match_picks_to_geometry(sgt_stations, sgt_picks, 
                           trace_positions, trace_elevations,
                           source_positions, source_elevations,
                           matching_mode='exact_x', tolerance=0.01,
                           max_distance=50.0, verbose=False):
    """
    Match picks from SGT file to actual trace/source geometry.
    
    Supports multiple matching strategies:
    - 'exact_x': Match by exact X coordinate (within tolerance)
    - 'nearest_x': Match to nearest X coordinate (within max_distance)
    - 'nearest_xz': Match to nearest (X, Z) coordinate (within max_distance)
    
    Parameters
    ----------
    sgt_stations : list of tuples
        Station coordinates [(x, y, z), ...] from SGT file
    sgt_picks : list of tuples
        Pick data [(source_idx, geophone_idx, time, error), ...] from SGT file
        Note: Indices are 1-based
    trace_positions : list of arrays
        Actual trace positions in dataset
    trace_elevations : list of arrays
        Actual trace elevations in dataset
    source_positions : list
        Actual source positions in dataset
    source_elevations : list
        Actual source elevations in dataset
    matching_mode : str, optional
        Matching strategy: 'exact_x', 'nearest_x', or 'nearest_xz'
    tolerance : float, optional
        Tolerance for exact matching in meters, default 0.01
    max_distance : float, optional
        Maximum distance for nearest neighbor matching in meters, default 50.0
    verbose : bool, optional
        Print debug information, default False
    
    Returns
    -------
    dict
        Dictionary containing:
        - 'picks': 2D list [source][trace] of matched pick times (NaN where no pick)
        - 'errors': 2D list [source][trace] of matched errors
        - 'n_matched': Number of successfully matched picks
        - 'n_total': Total picks in SGT file
    """
    n_sources = len(source_positions)
    n_traces_per_source = [len(tp) if tp is not None else 0 for tp in trace_positions]
    
    # Initialize pick and error arrays with NaN
    matched_picks = [[np.nan] * n_traces for n_traces in n_traces_per_source]
    matched_errors = [[np.nan] * n_traces for n_traces in n_traces_per_source]
    
    n_matched = 0
    n_total = len(sgt_picks)
    
    for source_idx_1based, geophone_idx_1based, pick_time, pick_error in sgt_picks:
        # Convert to 0-based indexing
        source_idx = source_idx_1based - 1
        geophone_idx = geophone_idx_1based - 1
        
        # Get station coordinates from SGT file (0-based indexing)
        if source_idx < len(sgt_stations):
            sgt_source_x, sgt_source_y, sgt_source_z = sgt_stations[source_idx]
        else:
            continue
            
        if geophone_idx < len(sgt_stations):
            sgt_geo_x, sgt_geo_y, sgt_geo_z = sgt_stations[geophone_idx]
        else:
            continue
        
        # Find matching source in actual geometry
        matched_source = None
        for i_src, (src_pos, src_elev) in enumerate(zip(source_positions, source_elevations)):
            if src_pos is None:
                continue
            
            if matching_mode == 'exact_x':
                if abs(src_pos - sgt_source_x) < tolerance:
                    matched_source = i_src
                    break
            elif matching_mode == 'nearest_x':
                if matched_source is None or abs(src_pos - sgt_source_x) < abs(source_positions[matched_source] - sgt_source_x):
                    if abs(src_pos - sgt_source_x) <= max_distance:
                        matched_source = i_src
            elif matching_mode == 'nearest_xz':
                dist = np.sqrt((src_pos - sgt_source_x)**2 + (src_elev - sgt_source_z)**2)
                if matched_source is None or dist < min_dist:
                    if dist <= max_distance:
                        matched_source = i_src
                        min_dist = dist
        
        if matched_source is None:
            continue
        
        # Find matching trace in actual geometry
        matched_trace = None
        if trace_positions[matched_source] is not None:
            for i_tr, (tr_pos, tr_elev) in enumerate(zip(trace_positions[matched_source], 
                                                          trace_elevations[matched_source])):
                if matching_mode == 'exact_x':
                    if abs(tr_pos - sgt_geo_x) < tolerance:
                        matched_trace = i_tr
                        break
                elif matching_mode == 'nearest_x':
                    if matched_trace is None or abs(tr_pos - sgt_geo_x) < abs(trace_positions[matched_source][matched_trace] - sgt_geo_x):
                        if abs(tr_pos - sgt_geo_x) <= max_distance:
                            matched_trace = i_tr
                elif matching_mode == 'nearest_xz':
                    dist = np.sqrt((tr_pos - sgt_geo_x)**2 + (tr_elev - sgt_geo_z)**2)
                    if matched_trace is None or dist < min_dist_trace:
                        if dist <= max_distance:
                            matched_trace = i_tr
                            min_dist_trace = dist
        
        # Assign pick if both source and trace matched
        if matched_trace is not None:
            matched_picks[matched_source][matched_trace] = pick_time
            matched_errors[matched_source][matched_trace] = pick_error
            n_matched += 1
    
    if verbose:
        print(f"Matched {n_matched}/{n_total} picks using {matching_mode} mode")
    
    return {
        'picks': matched_picks,
        'errors': matched_errors,
        'n_matched': n_matched,
        'n_total': n_total
    }
