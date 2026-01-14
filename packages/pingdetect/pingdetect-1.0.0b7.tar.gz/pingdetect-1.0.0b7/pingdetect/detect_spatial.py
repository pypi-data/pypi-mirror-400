
'''
Copyright (c) 2025- Cameron S. Bodine
'''

import os, sys
import ast
import numpy as np
import pandas as pd
import geopandas as gpd

# #=======================================================================
# def calcDetectIdx(smthTrkFile: str,
#                   df: pd.DataFrame, 
#                   stride: int, 
#                   nchunk: int=0):
#     '''
#     Associate predicted crabpot with actual coordinates. Since detections
#     are boxes and there is noise in vessel positioning, depth, and heading,
#     calculate average x/y over box coordinates to get a better estimate of
#     target location.

#     1. Calculate trackline csv idx
#     2. Get necessary attributes - record number, trackline easting/northing,
#        heading/cog, dep_m, pixM
#     3. Return updated dataframe
#     '''

#     # Convert string xyxy into list
#     if 'xyxy' in df.columns:
#         df['xyxy'] = df['xyxy'].apply(ast.literal_eval)
#         df[['box_x1', 'box_y1', 'box_x2', 'box_y2']] = pd.DataFrame(df['xyxy'].tolist(), index=df.index)

#         # Calculate bbox center point
#         df['mid_x'] = np.around((df['box_x2'] + df['box_x1'])/2, 0)
#         df['mid_y'] = np.around((df['box_y2'] + df['box_y1'])/2, 0)

#     else:
#         # df.rename(columns={'x': 'mid_x', 'y': 'mid_y'}, inplace=True)
#         print('No xyxy column in dataframe!')
#         print('Bug, report to developer.')
#         sys.exit('Exiting...')
    
#     # Calculate box index for each corner of the bbox
#     if 'vid_frame_id' in df.columns:
#         # df['box_ping_idx'] = ((df['vid_frame_id'] * stride) + df['mid_x']).astype(int)

#         df['box_ping_idx_start'] = ((df['vid_frame_id'] * stride) + df['box_x1']).astype(int)
#         df['box_ping_idx_end'] = ((df['vid_frame_id'] * stride) + df['box_x2']).astype(int)
        

#     else:
#         df['box_ping_idx'] = ((df['chunk_id'] * nchunk) + df['chunk_offset'] + df['mid_x']).astype(int)

#     # df.set_index(keys='box_ping_idx', drop=False, inplace=True)

#     # Get smooth trakcline file
#     smthTrk = pd.read_csv(smthTrkFile)

#     # # Get the record number, trackline easting/northing, heading/cog, and pixM
#     # df['record_num'] = smthTrk['record_num']
#     # df['trk_utm_es'] = smthTrk['trk_utm_es']
#     # df['trk_utm_ns'] = smthTrk['trk_utm_ns']
#     # df['trk_lons'] = smthTrk['trk_lons']
#     # df['trk_lats'] = smthTrk['trk_lats']
#     # df['instr_heading'] = smthTrk['instr_heading']
#     # df['trk_cog'] = smthTrk['trk_cog']
#     # df['dep_m'] = smthTrk['dep_m']
#     # df['pixM'] = smthTrk['pixM']

#     # Calculate average attributes over box area
#     attrs = ['trk_utm_es', 'trk_utm_ns', 'trk_lons',
#              'trk_lats', 'instr_heading', 'trk_cog', 'dep_m', 'pixM']
    
#     record_nums = []
#     attr_means = {attr: [] for attr in attrs}
    
#     for idx, row in df.iterrows():
#         start_idx = int(row['box_ping_idx_start'])
#         end_idx = int(row['box_ping_idx_end'])
        
#         mode_vals = smthTrk['record_num'].iloc[start_idx:end_idx+1].mode().values
#         record_nums.append(mode_vals[0] if len(mode_vals) > 0 else np.nan)
        
#         for attr in attrs:
#             attr_means[attr].append(smthTrk[attr].iloc[start_idx:end_idx+1].mean())
    
#     df['record_num'] = record_nums
#     for attr in attrs:
#         df[attr] = attr_means[attr]

#     # df.reset_index(inplace=True, drop=True)
    
#     return df

#=======================================================================
def calcDetectIdx(smthTrkFile: str,
                  df: pd.DataFrame, 
                  stride: int, 
                  nchunk: int=0,
                  transect_id: int | None=None):
    '''
    Associate predicted crabpot with actual coordinates.

    Box-span averaging: average trackline attributes across bbox width (x1→x2).
    Filters trackline to matching transect when transect_id is provided.
    '''

    # Convert string xyxy into list
    if 'xyxy' in df.columns:
        df['xyxy'] = df['xyxy'].apply(ast.literal_eval)
        df[['box_x1', 'box_y1', 'box_x2', 'box_y2']] = pd.DataFrame(df['xyxy'].tolist(), index=df.index)

        # Calculate bbox center point
        df['mid_x'] = np.around((df['box_x2'] + df['box_x1'])/2, 0)
        df['mid_y'] = np.around((df['box_y2'] + df['box_y1'])/2, 0)

    else:
        df.rename(columns={'x': 'mid_x', 'y': 'mid_y'}, inplace=True)
    
    # Load smoothed trackline
    smthTrk = pd.read_csv(smthTrkFile)
    
    # Filter by transect if provided; fallback to full trackline when no match
    if transect_id is not None and 'transect' in smthTrk.columns:
        transect_mask = smthTrk['transect'] == transect_id
        smthTrk_filtered = smthTrk[transect_mask].reset_index(drop=True)
        if len(smthTrk_filtered) == 0:
            # Fallback: use full trackline to avoid empty indexing
            print(f"[WARN] calcDetectIdx: No trackline rows found for transect {transect_id}; falling back to full trackline of {len(smthTrk)} pings.")
            smthTrk_filtered = smthTrk.reset_index(drop=True)
            # Optional flag to trace mismatches downstream
            df['transect_mismatch'] = True
    else:
        smthTrk_filtered = smthTrk
    
    # Calculate stride in pings-per-frame
    try:
        frame_stride_pings = int(np.round(nchunk * float(stride))) if not (isinstance(stride, (int, np.integer)) and stride > 1) else int(stride)
    except Exception:
        frame_stride_pings = int(nchunk)

    # Calculate start/end ping indices spanning bbox width
    if 'vid_frame_id' in df.columns:
        df['box_ping_idx_start'] = ((df['vid_frame_id'] * frame_stride_pings) + df['box_x1']).astype(int)
        df['box_ping_idx_end'] = ((df['vid_frame_id'] * frame_stride_pings) + df['box_x2']).astype(int)
        df['box_ping_idx'] = ((df['vid_frame_id'] * frame_stride_pings) + df['mid_x']).astype(int)
    else:
        df['box_ping_idx_start'] = ((df['chunk_id'] * nchunk) + df['chunk_offset'] + df['box_x1']).astype(int)
        df['box_ping_idx_end'] = ((df['chunk_id'] * nchunk) + df['chunk_offset'] + df['box_x2']).astype(int)
        df['box_ping_idx'] = ((df['chunk_id'] * nchunk) + df['chunk_offset'] + df['mid_x']).astype(int)

    # Clamp to valid range within filtered transect
    max_idx = len(smthTrk_filtered) - 1
    df['box_ping_idx_start'] = df['box_ping_idx_start'].clip(lower=0, upper=max_idx)
    df['box_ping_idx_end'] = df['box_ping_idx_end'].clip(lower=0, upper=max_idx)
    df['box_ping_idx'] = df['box_ping_idx'].clip(lower=0, upper=max_idx)

    # Average attributes over bbox span
    attrs = ['trk_utm_es', 'trk_utm_ns', 'trk_lons', 'trk_lats', 'instr_heading', 'trk_cog', 'dep_m', 'pixM']
    record_nums = []
    attr_means = {attr: [] for attr in attrs}

    for _, row in df.iterrows():
        start_idx = int(row['box_ping_idx_start'])
        end_idx = int(row['box_ping_idx_end'])
        if end_idx < start_idx:
            start_idx, end_idx = end_idx, start_idx
        # use mode for record_num
        mode_vals = smthTrk_filtered['record_num'].iloc[start_idx:end_idx+1].mode().values
        record_nums.append(mode_vals[0] if len(mode_vals) > 0 else np.nan)
        for attr in attrs:
            attr_means[attr].append(smthTrk_filtered[attr].iloc[start_idx:end_idx+1].mean())

    df['record_num'] = record_nums
    for attr in attrs:
        df[attr] = attr_means[attr]

    # Heading/COG differences over last 50 pings using center index
    heading_diffs = []
    cog_diffs = []
    for _, row in df.iterrows():
        center_idx = int(np.clip(np.round((row['box_ping_idx_start'] + row['box_ping_idx_end'])/2), 0, max_idx))
        prev_idx = max(0, center_idx - 50)
        cog_diff = smthTrk_filtered['trk_cog'].iloc[center_idx] - smthTrk_filtered['trk_cog'].iloc[prev_idx]
        heading_diff = smthTrk_filtered['instr_heading'].iloc[center_idx] - smthTrk_filtered['instr_heading'].iloc[prev_idx]
        cog_diffs.append(cog_diff)
        heading_diffs.append(heading_diff)
    df['cog_diff_50'] = cog_diffs
    df['heading_diff_50'] = heading_diffs

    return df

#=======================================================================
def calcDetectLoc(beamName: str,

                  df: pd.DataFrame,
                  flip: bool=False,
                  wgs: bool=False,
                  cog: bool=True):

    '''
    Calculate target location with trackline location.
    '''

    lons = 'trk_lons'
    lats = 'trk_lats'
    ping_bearing = 'ping_bearing'

    ########################
    # Calculate ping bearing
    # Determine ping bearing.  Ping bearings are perpendicular to COG.
    if beamName == 'ss_port':
        rotate = -90  # Rotate COG by 90 degrees to the left
    else:
        rotate = 90 # Rotate COG by 90 degrees to the right
    if flip: # Flip rotation factor if True
        rotate *= -1

    # Calculate ping bearing and normalize to range 0-360
    # cog = False
    if cog:
        df[ping_bearing] = (df['trk_cog']+rotate) % 360
    else:
        df[ping_bearing] = (df['instr_heading']+rotate) % 360

    ##############################
    # Calculate Target Coordinates

    # Determine slant range distance based on pixel y and pixel size (m/pixel)
    d_slant = df['mid_y'] * df['pixM']
    df['target_slantrange'] = d_slant

    # Slant-range correction: horizontal range = sqrt(max(d^2 - depth^2, 0))
    # Clamp negatives to 0 to avoid NaNs when slant < depth
    h_sq = (d_slant**2) - (df['dep_m']**2)
    d_horiz = np.sqrt(np.clip(h_sq, a_min=0, a_max=None))
    df['target_range'] = d_horiz

    # Calculate the coordinates from:
    ## origin (track x/y), distance, and COG
    R = 6371.393*1000 #Radius of the Earth in meters
    brng = np.deg2rad(df[ping_bearing])

    # Get lat/lon for origin of each ping
    lat1 = np.deg2rad(df[lats])#.to_numpy()
    lon1 = np.deg2rad(df[lons])#.to_numpy()

    # Calculate latitude of range extent
    lat2 = np.arcsin( np.sin(lat1) * np.cos(d_horiz/R) +
        np.cos(lat1) * np.sin(d_horiz/R) * np.cos(brng))

    # Calculate longitude of range extent
    lon2 = lon1 + np.arctan2( np.sin(brng) * np.sin(d_horiz/R) * np.cos(lat1),
                            np.cos(d_horiz/R) - np.sin(lat1) * np.sin(lat2))

    # Convert range extent coordinates into degrees
    df['target_lat'] = np.degrees(lat2)
    df['target_lon'] = np.degrees(lon2)

    return df

#=======================================================================
def summarizeDetect(df: pd.DataFrame):
    
    '''
    Summarize by target_id
    '''

    summarized = []

    for name, group in df.groupby('tracker_id'):

        # Store summary in dictionary
        sum_dict = {}

        # Add projName
        sum_dict['projName'] = group['projName'].iloc[0]

        # Get tracker_id
        sum_dict['tracker_id'] = name

        # Most frequent class_id
        sum_dict['class_id'] = group['class_id'].mode()
        sum_dict['class_name'] = group['data'].mode()

        # Get count of predictions
        sum_dict['pred_cnt'] = len(group)

        # Get confidence stats
        sum_dict['conf_avg'] = group['confidence'].mean()
        sum_dict['conf_min'] = group['confidence'].min()
        sum_dict['conf_max'] = group['confidence'].max()
        sum_dict['conf_std'] = group['confidence'].std()

        # Get median record num
        sum_dict['record_num'] = group['record_num'].median()

        # Get avg box center point
        sum_dict['mid_x'] = int(group['mid_x'].mean())
        sum_dict['mid_y'] = int(group['mid_y'].mean())

        # Confidence-weighted location
        if 'confidence' in group.columns:
            w = group['confidence'].fillna(0).to_numpy()
            w_sum = w.sum()
            if w_sum > 0:
                sum_dict['target_lat'] = np.around((group['target_lat'].to_numpy() * w).sum() / w_sum, 8)
                sum_dict['target_lon'] = np.around((group['target_lon'].to_numpy() * w).sum() / w_sum, 8)
            else:
                sum_dict['target_lat'] = np.around(group['target_lat'].mean(), 8)
                sum_dict['target_lon'] = np.around(group['target_lon'].mean(), 8)
        else:
            sum_dict['target_lat'] = np.around(group['target_lat'].mean(), 8)
            sum_dict['target_lon'] = np.around(group['target_lon'].mean(), 8)

        # Get avg slant/range
        sum_dict['target_slantrange'] = np.around(group['target_slantrange'].mean(), 3)
        sum_dict['target_range'] = np.around(group['target_range'].mean(), 3)

        # Get avg depth
        sum_dict['dep_m'] = np.around(group['dep_m'].mean(), 3)


        # Append
        summarized.append(sum_dict)

    finalDF = pd.DataFrame(summarized)

    return finalDF


#=======================================================================
def calcWpt(df: pd.DataFrame,
            outDir: str,
            projDir: str,
            threshold: float=0.2):
    
    '''
    '''

    # Filter by threshold
    if 'conf_avg' in df.columns:
        conf_col = 'conf_avg'
    else:
        conf_col = 'confidence'

    predDF = df.loc[df[conf_col] >= threshold]

    # Drop rows without coordinates; writing an empty GeoDataFrame leads to
    # "unknown geometry type" errors in the GPX driver.
    predDF = predDF.dropna(subset=['target_lon', 'target_lat'])
    if predDF.empty:
        return

    
    # # Calculate name
    # for i, row in predDF.iterrows():
    #     zero = self._addZero(i)
    #     # wptName = namePrefix+'{}{}'.format(zero, i)
    #     conf = int(row['confidence']*100)
    #     wptName = '{} {} {}%'.format(i, row['class_name'], conf)
    #     predDF.loc[i, 'wpt_name'] = wptName

    # Save to shp
    gdf = gpd.GeoDataFrame(predDF, geometry=gpd.points_from_xy(predDF['target_lon'], predDF['target_lat']), crs='EPSG:4326')

    if gdf.empty:
        return

    # Save shapefile
    file_name = os.path.basename(projDir)+'.shp'
    file_name = os.path.join(outDir, file_name)
    gdf.to_file(file_name)

    # file_name = os.path.join(self.outDir, 'CrabPotLoc.gpx')
    file_name = file_name.replace('.shp', '.gpx')
    gdf = gdf.rename(columns={'tracker_id': 'name'})
    gdf = gdf[['name', 'geometry']]
    gdf.to_file(file_name, 'GPX')

    return