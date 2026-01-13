#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import pyuda
import csv
import sys
client=pyuda.Client()

row_resolution=5e-3 #units of m
column_resolution=5e-3 #units of m

tile='N2'
max_phi=90*np.pi/180
min_phi=-90*np.pi/180


def RZ_shifts_rotation_only(R_unshifted,Z_unshifted,tile,upper_or_lower):
    aff_trans = client.geometry("/affinetransforms", 50000, no_cal=True)
    centrecolumn_tiles_mat=aff_trans.data['asbuilt/rz_2d/centrecolumn_tiles/data'].matrix
    centrecolumn_tiles_mat[0,2]=0
    centrecolumn_tiles_mat[1,2]=0
    div_tiles_upper_t1_mat=aff_trans.data['asbuilt/rz_2d/div_tiles_upper_t1/data'].matrix
    div_tiles_upper_t1_mat[0,2]=0
    div_tiles_upper_t1_mat[1,2]=0
    div_tiles_upper_t2_mat=aff_trans.data['asbuilt/rz_2d/div_tiles_upper_t2/data'].matrix
    div_tiles_upper_t2_mat[0,2]=0
    div_tiles_upper_t2_mat[1,2]=0
    div_tiles_upper_t3_mat=aff_trans.data['asbuilt/rz_2d/div_tiles_upper_t3/data'].matrix
    div_tiles_upper_t3_mat[0,2]=0
    div_tiles_upper_t3_mat[1,2]=0
    div_tiles_upper_t4_mat=aff_trans.data['asbuilt/rz_2d/div_tiles_upper_t4/data'].matrix
    div_tiles_upper_t4_mat[0,2]=0
    div_tiles_upper_t4_mat[1,2]=0
    div_tiles_upper_t5_mat=aff_trans.data['asbuilt/rz_2d/div_tiles_upper_t5/data'].matrix
    div_tiles_upper_t5_mat[0,2]=0
    div_tiles_upper_t5_mat[1,2]=0

    div_tiles_lower_t1_mat=aff_trans.data['asbuilt/rz_2d/div_tiles_lower_t1/data'].matrix
    div_tiles_lower_t1_mat[0,2]=0
    div_tiles_lower_t1_mat[1,2]=0
    div_tiles_lower_t2_mat=aff_trans.data['asbuilt/rz_2d/div_tiles_lower_t2/data'].matrix
    div_tiles_lower_t2_mat[0,2]=0
    div_tiles_lower_t2_mat[1,2]=0
    div_tiles_lower_t3_mat=aff_trans.data['asbuilt/rz_2d/div_tiles_lower_t3/data'].matrix
    div_tiles_lower_t3_mat[0,2]=0
    div_tiles_lower_t3_mat[1,2]=0
    div_tiles_lower_t4_mat=aff_trans.data['asbuilt/rz_2d/div_tiles_lower_t4/data'].matrix
    div_tiles_lower_t4_mat[0,2]=0
    div_tiles_lower_t4_mat[1,2]=0
    div_tiles_lower_t5_mat=aff_trans.data['asbuilt/rz_2d/div_tiles_lower_t5/data'].matrix
    div_tiles_lower_t5_mat[0,2]=0
    div_tiles_lower_t5_mat[1,2]=0

    cassette_upper_mat=aff_trans.data['asbuilt/rz_2d/cassette_upper/data'].matrix
    cassette_upper_mat[0,2]=0
    cassette_upper_mat[1,2]=0
    cassette_lower_mat=aff_trans.data['asbuilt/rz_2d/cassette_lower/data'].matrix
    cassette_lower_mat[0,2]=0
    cassette_lower_mat[1,2]=0

    unshifted_RZ_vec=np.array([R_unshifted,Z_unshifted,1]).reshape(3,1)
    if upper_or_lower=='upper':
        if tile=='T1':
            shift_vec=div_tiles_upper_t1_mat@unshifted_RZ_vec
        if tile=='T2':
            shift_vec=div_tiles_upper_t2_mat@unshifted_RZ_vec
        if tile=='T3':
            shift_vec=div_tiles_upper_t3_mat@unshifted_RZ_vec
        if tile=='T4':
            shift_vec=div_tiles_upper_t4_mat@unshifted_RZ_vec
        if tile=='T5':
            shift_vec=div_tiles_upper_t5_mat@unshifted_RZ_vec
        if tile=='C5' or tile=='C6':
            shift_vec=centrecolumn_tiles_mat@unshifted_RZ_vec
        if tile=='B1' or tile=='B2' or tile=='B3' or tile=='B4' or tile=='N1' or tile=='N2':
            shift_vec=cassette_upper_mat@unshifted_RZ_vec
    else:
        if tile=='T1':
            shift_vec=div_tiles_lower_t1_mat@unshifted_RZ_vec
        if tile=='T2':
            shift_vec=div_tiles_lower_t2_mat@unshifted_RZ_vec
        if tile=='T3':
            shift_vec=div_tiles_lower_t3_mat@unshifted_RZ_vec
        if tile=='T4':
            shift_vec=div_tiles_lower_t4_mat@unshifted_RZ_vec
        if tile=='T5':
            shift_vec=div_tiles_lower_t5_mat@unshifted_RZ_vec
        if tile=='C5' or tile=='C6':
            shift_vec=centrecolumn_tiles_mat@unshifted_RZ_vec
        if tile=='B1' or tile=='B2' or tile=='B3' or tile=='B4' or tile=='N1' or tile=='N2':
            shift_vec=cassette_lower_mat@unshifted_RZ_vec
    R_shifted=shift_vec[0][0]
    Z_shifted=shift_vec[1][0]
    return R_shifted, Z_shifted


def RZ_shifts_single_position(R_unshifted,Z_unshifted,tile,upper_or_lower):
    aff_trans = client.geometry("/affinetransforms", 50000, no_cal=True)
    centrecolumn_tiles_mat=aff_trans.data['asbuilt/rz_2d/centrecolumn_tiles/data'].matrix
    div_tiles_upper_t1_mat=aff_trans.data['asbuilt/rz_2d/div_tiles_upper_t1/data'].matrix
    div_tiles_upper_t2_mat=aff_trans.data['asbuilt/rz_2d/div_tiles_upper_t2/data'].matrix
    div_tiles_upper_t3_mat=aff_trans.data['asbuilt/rz_2d/div_tiles_upper_t3/data'].matrix
    div_tiles_upper_t4_mat=aff_trans.data['asbuilt/rz_2d/div_tiles_upper_t4/data'].matrix
    div_tiles_upper_t5_mat=aff_trans.data['asbuilt/rz_2d/div_tiles_upper_t5/data'].matrix

    div_tiles_lower_t1_mat=aff_trans.data['asbuilt/rz_2d/div_tiles_lower_t1/data'].matrix
    div_tiles_lower_t2_mat=aff_trans.data['asbuilt/rz_2d/div_tiles_lower_t2/data'].matrix
    div_tiles_lower_t3_mat=aff_trans.data['asbuilt/rz_2d/div_tiles_lower_t3/data'].matrix
    div_tiles_lower_t4_mat=aff_trans.data['asbuilt/rz_2d/div_tiles_lower_t4/data'].matrix
    div_tiles_lower_t5_mat=aff_trans.data['asbuilt/rz_2d/div_tiles_lower_t5/data'].matrix

    cassette_upper_mat=aff_trans.data['asbuilt/rz_2d/cassette_upper/data'].matrix
    cassette_lower_mat=aff_trans.data['asbuilt/rz_2d/cassette_lower/data'].matrix

    unshifted_RZ_vec=np.array([R_unshifted,Z_unshifted,1]).reshape(3,1)
    if upper_or_lower=='upper':
        if tile=='T1':
            shift_vec=div_tiles_upper_t1_mat@unshifted_RZ_vec
        if tile=='T2':
            shift_vec=div_tiles_upper_t2_mat@unshifted_RZ_vec
        if tile=='T3':
            shift_vec=div_tiles_upper_t3_mat@unshifted_RZ_vec
        if tile=='T4':
            shift_vec=div_tiles_upper_t4_mat@unshifted_RZ_vec
        if tile=='T5':
            shift_vec=div_tiles_upper_t5_mat@unshifted_RZ_vec
        if tile=='C5' or tile=='C6':
            shift_vec=centrecolumn_tiles_mat@unshifted_RZ_vec
        if tile=='B1' or tile=='B2' or tile=='B3' or tile=='B4' or tile=='N1' or tile=='N2':
            shift_vec=cassette_upper_mat@unshifted_RZ_vec
    else:
        if tile=='T1':
            shift_vec=div_tiles_lower_t1_mat@unshifted_RZ_vec
        if tile=='T2':
            shift_vec=div_tiles_lower_t2_mat@unshifted_RZ_vec
        if tile=='T3':
            shift_vec=div_tiles_lower_t3_mat@unshifted_RZ_vec
        if tile=='T4':
            shift_vec=div_tiles_lower_t4_mat@unshifted_RZ_vec
        if tile=='T5':
            shift_vec=div_tiles_lower_t5_mat@unshifted_RZ_vec
        if tile=='C5' or tile=='C6':
            shift_vec=centrecolumn_tiles_mat@unshifted_RZ_vec
        if tile=='B1' or tile=='B2' or tile=='B3' or tile=='B4' or tile=='N1' or tile=='N2':
            shift_vec=cassette_lower_mat@unshifted_RZ_vec
    R_shifted=shift_vec[0][0]
    Z_shifted=shift_vec[1][0]
    return R_shifted, Z_shifted

def calculate_surface_normal_xyz(point1,point2,point3):
    """
    Cross product to calculate surface normal using the three points. Inputs and outputs are in cartesian coordinates.
    """
    surface_vector1=point1-point2
    surface_vector2=point1-point3
    one_cross_two=np.cross(surface_vector2,surface_vector1)
    magnitude=(one_cross_two[0]**2+one_cross_two[1]**2+one_cross_two[2]**2)**0.5
    surface_normal_xyz=one_cross_two/magnitude
    return surface_normal_xyz

def calculate_cylindrical_unit_vectors(point1):
    """
    Calculate cylindrical unit vectors at position point1.
    point1 is given in cartesian coordinates.
    Output is the cylindrical unit vectors written in terms of cartesian coordinates.
    """
    radial_unit_vector=np.array([point1[0],point1[1],0])/((point1[0]**2+point1[1]**2)**0.5)

    toroidal_unit_vector_magnitude_y=np.abs(radial_unit_vector[0]/(radial_unit_vector[0]**2+radial_unit_vector[1]**2)**0.5)
    toroidal_unit_vector_magnitude_x=np.abs((1-toroidal_unit_vector_magnitude_y**2)**0.5)

    if (point1[0]>0) & (point1[1]>=0):
        toroidal_unit_vector=np.array([-toroidal_unit_vector_magnitude_x,toroidal_unit_vector_magnitude_y,0])
    if (point1[0]<=0) & (point1[1]>0):
        toroidal_unit_vector=np.array([-toroidal_unit_vector_magnitude_x,-toroidal_unit_vector_magnitude_y,0])
    if (point1[0]<0) & (point1[1]<=0):
        toroidal_unit_vector=np.array([toroidal_unit_vector_magnitude_x,-toroidal_unit_vector_magnitude_y,0])
    if (point1[0]>=0) & (point1[1]<0):
        toroidal_unit_vector=np.array([toroidal_unit_vector_magnitude_x,toroidal_unit_vector_magnitude_y,0])
    if np.isnan(point1[0])==True:
        toroidal_unit_vector=np.array([np.nan,np.nan,np.nan])
    z_unit_vector=np.array([0,0,1])
    cylindrical_unit_vectors=np.array([radial_unit_vector, toroidal_unit_vector, z_unit_vector])
    return cylindrical_unit_vectors
def transform_vector_into_cylindrical(surface_normal_xyz,cylindrical_unit_vectors):
    """
    Transform a vector given in terms of cartesian coordinates to cylindrical coordinates.
    """
    radial_unit_vector=cylindrical_unit_vectors[0]
    toroidal_unit_vector=cylindrical_unit_vectors[1]
    if np.abs(radial_unit_vector[0])>1e-10: #problem with infinity when the radial unit vector has a small x component.
        surface_normal_toroidal=(surface_normal_xyz[1]-(radial_unit_vector[1]*surface_normal_xyz[0]/radial_unit_vector[0]))/(toroidal_unit_vector[1]-(toroidal_unit_vector[0]*radial_unit_vector[1]/radial_unit_vector[0]))
        surface_normal_radial=(surface_normal_xyz[0]-(surface_normal_toroidal*toroidal_unit_vector[0]))/radial_unit_vector[0]
    else:
        surface_normal_toroidal=surface_normal_xyz[0]/toroidal_unit_vector[0]
        surface_normal_radial=(surface_normal_xyz[1]-(toroidal_unit_vector[1]*surface_normal_toroidal)/radial_unit_vector[1])
    surface_normal_rTz=np.array([surface_normal_radial,surface_normal_toroidal,surface_normal_xyz[2]]) #equivalent to surface_normal_xyz but in new basis.
    magnitude_rTz=(surface_normal_rTz[0]**2+surface_normal_rTz[1]**2+surface_normal_rTz[2]**2)**0.5 #check
    return surface_normal_rTz
def ensure_outwards_normal(surface_normal_rTz,cylindrical_unit_vectors,point1,loc,tile):
    """
    ensure that the surface normals point outwards from the surface.
    The code generates inwards and outwards surface normal-vectors at position point1. Distance to ref position is used to determine the outwards vector.
    Ref position is dependent on the type of tile.
    """
    if (tile=='N1') or (tile=='N2') or (tile=='B1') or (tile=='B2') or (tile=='B3') or (tile=='B4') or (tile=='B5'):
        ref_pos=np.array([1.25,0,-1.4]) #outwards should point away from this point.
    else:
        ref_pos=np.array([1.2,0,-1.5]) #outwards should point towards this point. e.g. tile 'T2'
    vector_xyz=create_vector_cartesian(surface_normal_rTz, cylindrical_unit_vectors, point1,1)
    opp_vector_xyz=create_vector_cartesian(surface_normal_rTz, cylindrical_unit_vectors, point1,-1)
    distance=((vector_xyz[0][1]-ref_pos[0])**2+(vector_xyz[1][1])**2+(vector_xyz[2][1]-ref_pos[2])**2)**0.5
    opp_distance=((opp_vector_xyz[0][1]-ref_pos[0])**2+(opp_vector_xyz[1][1])**2+(opp_vector_xyz[2][1]-ref_pos[2])**2)**0.5
    if (tile=='N1') or (tile=='N2') or (tile=='B1') or (tile=='B2') or (tile=='B3') or (tile=='B4') or (tile=='B5'):
        if distance>opp_distance:
            dir_surface_normal_rTz=surface_normal_rTz
        else:
            dir_surface_normal_rTz=surface_normal_rTz*-1
    else:
        if distance<opp_distance:
            dir_surface_normal_rTz=surface_normal_rTz
        else:
            dir_surface_normal_rTz=surface_normal_rTz*-1
    if loc=='upper':
        dir_surface_normal_rTz[2]=dir_surface_normal_rTz[2]*-1
    return dir_surface_normal_rTz

def create_vector_cartesian(surface_normal_rTz, cylindrical_unit_vectors, point1,polarity): #polarity controls direct of surface normal but not position at which it is drawn from.
    """
    Generates data points for plotting surface-normals in cartesian coordinates.
    surface_normal_rTz in cylindrical coords.
    cylindrical_unit_vectors and point1 in cartesian.
    """
    radial_unit_vector=cylindrical_unit_vectors[0]
    toroidal_unit_vector=cylindrical_unit_vectors[1]
    z_unit_vector=cylindrical_unit_vectors[2]
    surface_normal_xyz=surface_normal_rTz[0]*radial_unit_vector+surface_normal_rTz[1]*toroidal_unit_vector+surface_normal_rTz[2]*z_unit_vector
    x_points=np.array([0,polarity*surface_normal_xyz[0]])+point1[0]
    y_points=np.array([0,polarity*surface_normal_xyz[1]])+point1[1]
    z_points=np.array([0,polarity*surface_normal_xyz[2]])+point1[2]
    vector_xyz=[x_points, y_points, z_points]
    return vector_xyz

def tile_rows(filename):
    """
    filename is the name given to the Fishpool csv file. This file must have the following column headings: 'x', 'y' and 'z'.
    This function organises the csv data into 'rows' and 'columns'. The row data is represented as a list, and the elements within a list are np.arrays (column data).
    There are three outputs; one for each basis vector in cartesian coordinates.
    """
    surface=pd.read_csv(filename)
    x_surface=np.array(surface['x'])
    y_surface=np.array(surface['y'])
    z_surface=np.array(surface['z'])

    x_diff=np.diff(x_surface)
    y_diff=np.diff(y_surface)
    z_diff=np.diff(z_surface)

    distances=(x_diff**2+y_diff**2+z_diff**2)**0.5 #distance between adjacent points
    new_row_index,=np.where(distances>0.05) #new row index

    x_data_rows=[]
    x_data_rows.append(x_surface[0:new_row_index[0]+1])
    y_data_rows=[]
    y_data_rows.append(y_surface[0:new_row_index[0]+1])
    z_data_rows=[]
    z_data_rows.append(z_surface[0:new_row_index[0]+1])
    for i in range(len(new_row_index)-1):
        x_row=x_surface[new_row_index[i]+1:new_row_index[i+1]+1]
        x_data_rows.append(x_row)
        y_row=y_surface[new_row_index[i]+1:new_row_index[i+1]+1]
        y_data_rows.append(y_row)
        z_row=z_surface[new_row_index[i]+1:new_row_index[i+1]+1]
        z_data_rows.append(z_row)
    return x_data_rows, y_data_rows, z_data_rows


def tile_rows_cut(filename,min_phi,max_phi):
    """
    filename is the name given to the Fishpool csv file. This file must have the following column headings: 'x', 'y' and 'z'.
    This function organises the csv data into 'rows' and 'columns'. The row data is represented as a list, and the elements within a list are np.arrays (column data).
    In addition, the function crops the csv data so that only data between min_phi and max_phi is kept (cylindrical coordinates).
    There are three outputs; one for each basis vector in cartesian coordinates.
    """

    surface=pd.read_csv(filename)
    x_surface_uncut=np.array(surface['x'])
    y_surface_uncut=np.array(surface['y'])
    z_surface_uncut=np.array(surface['z'])

    radius_surface=(x_surface_uncut**2+y_surface_uncut**2)**0.5
    phi_surface=np.arcsin(y_surface_uncut/radius_surface)

    x_surface=np.array([]) #these will define the surface after cropping the data.
    y_surface=np.array([])
    z_surface=np.array([])
    phi_surface_ii=np.array([])
    for i in range(len(x_surface_uncut)):
        if (phi_surface[i]>min_phi-1e-4) & (phi_surface[i]<max_phi+1e-3): #added a small constant in case phi_surface has rounding errors.
            x_surface=np.concatenate([x_surface,np.array([x_surface_uncut[i]])])
            y_surface=np.concatenate([y_surface,np.array([y_surface_uncut[i]])])
            z_surface=np.concatenate([z_surface,np.array([z_surface_uncut[i]])])
            phi_surface_ii=np.concatenate([phi_surface_ii,np.array([phi_surface[i]])])

    x_diff=np.diff(x_surface)
    y_diff=np.diff(y_surface)
    z_diff=np.diff(z_surface)

    distances=(x_diff**2+y_diff**2+z_diff**2)**0.5 #distance between adjacent points
    new_row_index,=np.where(distances>0.05) #new row index
    x_data_rows=[]
    x_data_rows.append(x_surface[0:new_row_index[0]+1])
    y_data_rows=[]
    y_data_rows.append(y_surface[0:new_row_index[0]+1])
    z_data_rows=[]
    z_data_rows.append(z_surface[0:new_row_index[0]+1])
    for i in range(len(new_row_index)-1):
        x_row=x_surface[new_row_index[i]+1:new_row_index[i+1]+1]
        x_data_rows.append(x_row)
        y_row=y_surface[new_row_index[i]+1:new_row_index[i+1]+1]
        y_data_rows.append(y_row)
        z_row=z_surface[new_row_index[i]+1:new_row_index[i+1]+1]
        z_data_rows.append(z_row)
    return x_data_rows, y_data_rows, z_data_rows


def three_points(x_data_rows, y_data_rows, z_data_rows, row_index, column_index,method):
    """
    Locate three, closely separated, points on the surface.
    One of these points is defined by row_index, column_index; called point1.
    The other two points are have a common row, which is a different row to point1
    Outputs are the three points in cartesian coordinates.
    """
    interest_x=x_data_rows[row_index][column_index]
    interest_y=y_data_rows[row_index][column_index]
    interest_z=z_data_rows[row_index][column_index]
    point1=np.array([interest_x,interest_y,interest_z])

    if row_index==0:
        two_row_x=x_data_rows[1]
        two_row_y=y_data_rows[1]
        two_row_z=z_data_rows[1]
        diff_x=interest_x-two_row_x
        diff_y=interest_y-two_row_y
        diff_z=interest_z-two_row_z
        distances=(diff_x**2+diff_y**2+diff_z**2)**0.5
        indices_sort=np.argsort(distances)
    if (row_index==len(x_data_rows)-1) or (row_index==-1):
        two_row_x=x_data_rows[-2]
        two_row_y=y_data_rows[-2]
        two_row_z=z_data_rows[-2]
        diff_x=interest_x-two_row_x
        diff_y=interest_y-two_row_y
        diff_z=interest_z-two_row_z
        distances=(diff_x**2+diff_y**2+diff_z**2)**0.5
        indices_sort=np.argsort(distances)
    if (row_index>0) and (row_index<len(x_data_rows)-1):
        above_x=x_data_rows[row_index+1]
        above_y=y_data_rows[row_index+1]
        above_z=z_data_rows[row_index+1]

        abv_diff_x=interest_x-above_x
        abv_diff_y=interest_y-above_y
        abv_diff_z=interest_z-above_z
        abv_distances=(abv_diff_x**2+abv_diff_y**2+abv_diff_z**2)**0.5
        min_abv=min(abv_distances)

        below_x=x_data_rows[row_index-1]
        below_y=y_data_rows[row_index-1]
        below_z=z_data_rows[row_index-1]

        blw_diff_x=interest_x-below_x
        blw_diff_y=interest_y-below_y
        blw_diff_z=interest_z-below_z
        blw_distances=(blw_diff_x**2+blw_diff_y**2+blw_diff_z**2)**0.5
        min_blw=min(blw_distances)
        if method=='min':
            if min_abv<=min_blw:
                indices_sort=np.argsort(abv_distances)
                two_row_x=x_data_rows[row_index+1]
                two_row_y=y_data_rows[row_index+1]
                two_row_z=z_data_rows[row_index+1]
            else:
                indices_sort=np.argsort(blw_distances)
                two_row_x=x_data_rows[row_index-1]
                two_row_y=y_data_rows[row_index-1]
                two_row_z=z_data_rows[row_index-1]
        if method=='above':
            indices_sort=np.argsort(abv_distances)
            two_row_x=x_data_rows[row_index+1]
            two_row_y=y_data_rows[row_index+1]
            two_row_z=z_data_rows[row_index+1]
        if method=='below':
            indices_sort=np.argsort(blw_distances)
            two_row_x=x_data_rows[row_index-1]
            two_row_y=y_data_rows[row_index-1]
            two_row_z=z_data_rows[row_index-1]
    point2=np.array([two_row_x[indices_sort[0]],two_row_y[indices_sort[0]],two_row_z[indices_sort[0]]])
    point3=np.array([two_row_x[indices_sort[1]],two_row_y[indices_sort[1]],two_row_z[indices_sort[1]]])
    return point1, point2, point3



def generate_surface_norms(tile,min_phi,max_phi, row_resolution, column_resolution,method):
    """
    main function - calls the other functions. Generates surface-normals across the entire surface defined in the csv file. This is only for LOWER.
    row_resolution, column_resolution in metres.
    tile is e.g. 'T2'
    min_phi,max_phi for cropping the Fishpool csv data.
    """
    filename=tile+'.csv'
    x_data_rows, y_data_rows, z_data_rows=tile_rows_cut(filename,min_phi,max_phi)
    row_step=((x_data_rows[1][0]-x_data_rows[0][0])**2+(y_data_rows[1][0]-y_data_rows[0][0])**2+(z_data_rows[1][0]-z_data_rows[0][0])**2)**0.5 #unit m
    column_step=((x_data_rows[0][1]-x_data_rows[0][0])**2+(y_data_rows[0][1]-y_data_rows[0][0])**2+(z_data_rows[0][1]-z_data_rows[0][0])**2)**0.5 #unit m
    if row_step>row_resolution:
        print('Error! Row_resolution is smaller than the resolution of the data.')
        row_resolution=row_step
    if column_step>column_resolution:
        print('Error! Column_resolution is smaller than the resolution of the data.')
        column_resolution=column_step
    row_resolution_i=np.floor(row_resolution/row_step)
    column_resolution_i=np.floor(column_resolution/column_step)

    row_indices=np.arange(0,len(x_data_rows),row_resolution_i)
    row_indices=row_indices.astype(int)
    count=0
    for row in row_indices:
        column_indices=np.arange(0,len(x_data_rows[row]),column_resolution_i)
        column_indices=column_indices.astype(int)
        for col in column_indices:
            point1,point2,point3=three_points(x_data_rows, y_data_rows, z_data_rows, row, col,method) #points on a tile surface z<0
            surface_normal_xyz=calculate_surface_normal_xyz(point1,point2,point3)
            cylindrical_unit_vectors=calculate_cylindrical_unit_vectors(point1)
            surface_normal_rTz=transform_vector_into_cylindrical(surface_normal_xyz,cylindrical_unit_vectors) #surface-normal might not point outwards from surface
            dir_surface_normal_rTz=ensure_outwards_normal(surface_normal_rTz,cylindrical_unit_vectors,point1,'lower',tile) #surface-normal points outwards.
            dir_surface_normal_rTz=dir_surface_normal_rTz.reshape(1,3)
            point1=point1.reshape(1,3)
            if count==0:
                store_vectors_rTz=dir_surface_normal_rTz
                store_positions_xyz=point1
            else:
                store_vectors_rTz=np.concatenate([store_vectors_rTz,dir_surface_normal_rTz])
                store_positions_xyz=np.concatenate([store_positions_xyz,point1])
            count=count+1
    return store_positions_xyz,store_vectors_rTz,x_data_rows,y_data_rows,z_data_rows


def construct_stencil(x_data_rows, y_data_rows, z_data_rows, row, col):
    if row<=2 or row>=len(x_data_rows)-2 or col<=2 or col>= len(x_data_rows[0])-2:
        return np.array([np.nan,np.nan,np.nan]),np.nan,np.array([np.nan,np.nan,np.nan]),np.array([np.nan,np.nan,np.nan])
    x=x_data_rows[row][col]
    y=y_data_rows[row][col]
    z=z_data_rows[row][col]

    x_row_above=x_data_rows[row+1]
    y_row_above=y_data_rows[row+1]
    z_row_above=z_data_rows[row+1]

    diff_above=((x-x_row_above)**2+(y-y_row_above)**2+(z-z_row_above)**2)**0.5
    index_sorted_above=np.argsort(diff_above) #smallest number to largest
    min_above_index1=index_sorted_above[0]
    min_above_index2=index_sorted_above[1]

    x_row_below=x_data_rows[row-1]
    y_row_below=y_data_rows[row-1]
    z_row_below=z_data_rows[row-1]

    diff_below=((x-x_row_below)**2+(y-y_row_below)**2+(z-z_row_below)**2)**0.5
    index_sorted_below=np.argsort(diff_below) #smallest number to largest
    min_below_index1=index_sorted_below[0]
    min_below_index2=index_sorted_below[1]

    x_row_current=x_data_rows[row]
    y_row_current=y_data_rows[row]
    z_row_current=z_data_rows[row]

    diff_current=((x-x_row_current)**2+(y-y_row_current)**2+(z-z_row_current)**2)**0.5
    index_sorted_current=np.argsort(diff_current) #smallest number to largest
    min_current_index1=index_sorted_current[1]
    min_current_index2=index_sorted_current[2]

#    if x<0.82:
#    plt.figure()
#    axes = plt.axes(projection='3d')
#    axes.plot(x_row_current,y_row_current,z_row_current,'y')
#    axes.scatter(x,y,z,'b')
#    axes.scatter(x_row_below[min_below_index1],y_row_below[min_below_index1],z_row_below[min_below_index1],color='k')
#        axes.scatter(x_row_below[min_below_index2],y_row_below[min_below_index2],z_row_below[min_below_index2])
#    axes.scatter(x_row_above[min_above_index1],y_row_above[min_above_index1],z_row_above[min_above_index1],color='k')
#        axes.scatter(x_row_above[min_above_index2],y_row_above[min_above_index2],z_row_above[min_above_index2])
#    axes.scatter(x_row_current[min_current_index1],y_row_current[min_current_index1],z_row_current[min_current_index1],color='r')
#    axes.scatter(x_row_current[min_current_index2],y_row_current[min_current_index2],z_row_current[min_current_index2],color='r')
#    plt.show()

    vector1=np.array([x_row_current[min_current_index1]-x_row_current[min_current_index2],y_row_current[min_current_index1]-y_row_current[min_current_index2],z_row_current[min_current_index1]-z_row_current[min_current_index2]])
    vector2=np.array([x_row_above[min_above_index1]-x_row_below[min_below_index1],y_row_above[min_above_index1]-y_row_below[min_below_index1],z_row_above[min_above_index1]-z_row_below[min_below_index1]])

    one_cross_two=np.cross(vector2,vector1)
    magnitude=(one_cross_two[0]**2+one_cross_two[1]**2+one_cross_two[2]**2)**0.5
    surface_normal_xyz=one_cross_two/magnitude

    abs1=(vector1[0]**2+vector1[1]**2+vector1[2]**2)**0.5
    abs2=(vector2[0]**2+vector2[1]**2+vector2[2]**2)**0.5
    angle_check=np.arccos( np.dot(vector1,vector2)/( abs1*abs2 ) )*180/np.pi

#check that the intersection of the two vectors is near the spatial point of interest.
    vec1_position_start=np.array([x_row_current[min_current_index1],y_row_current[min_current_index1],z_row_current[min_current_index1]])
    vec2_position_start=np.array([x_row_above[min_above_index1],y_row_above[min_above_index1],z_row_above[min_above_index1]])

    vec2_coord=(vec2_position_start[1]-vec1_position_start[1]+(vector1[1]*vec1_position_start[0]/vector1[0])-(vector1[1]*vec2_position_start[0]/vector1[0]))/(vector2[0]*vector1[1]/vector1[0]-vector2[1] )
    intersection_point_vec2=vector2*vec2_coord+vec2_position_start
    vec1_coord=(vec2_position_start[0]-vec1_position_start[0]+vector2[0]*vec2_coord)/vector1[0]
    intersection_point_vec1=vector1*vec1_coord+vec1_position_start


    return surface_normal_xyz,angle_check,intersection_point_vec1,intersection_point_vec2

def generate_surface_norms_stencils(tile,min_phi,max_phi, row_resolution, column_resolution):
    """
    main function - calls the other functions. Generates surface-normals across the entire surface defined in the csv file. This is only for LOWER.
    row_resolution, column_resolution in metres.
    tile is e.g. 'T2'
    min_phi,max_phi for cropping the Fishpool csv data.
    """
    store_angle_check=[]
    store_intersection_point_vec1=[]
    filename=tile+'.csv'
    x_data_rows, y_data_rows, z_data_rows=tile_rows_cut(filename,min_phi,max_phi)
    row_step=((x_data_rows[1][0]-x_data_rows[0][0])**2+(y_data_rows[1][0]-y_data_rows[0][0])**2+(z_data_rows[1][0]-z_data_rows[0][0])**2)**0.5 #unit m
    column_step=((x_data_rows[0][1]-x_data_rows[0][0])**2+(y_data_rows[0][1]-y_data_rows[0][0])**2+(z_data_rows[0][1]-z_data_rows[0][0])**2)**0.5 #unit m
    if row_step>row_resolution:
        print('Error! Row_resolution is smaller than the resolution of the data.')
        row_resolution=row_step
    if column_step>column_resolution:
        print('Error! Column_resolution is smaller than the resolution of the data.')
        column_resolution=column_step
    row_resolution_i=np.floor(row_resolution/row_step)
    column_resolution_i=np.floor(column_resolution/column_step)

    row_indices=np.arange(1,len(x_data_rows)-1,row_resolution_i)
    row_indices=row_indices.astype(int)
    count=0
    for row in row_indices:
        column_indices=np.arange(1,len(x_data_rows[row])-1,column_resolution_i)
        column_indices=column_indices.astype(int)
        for col in column_indices:
            point1=np.array([x_data_rows[row][col],y_data_rows[row][col],z_data_rows[row][col]])
#            point1_r=(point1[0]**2+point1[1]**2)**0.5
#            if point1_r<0.86:
#                print(row)
#                print(col)
#                print('')
            surface_normal_xyz,angle_check,intersection_point_vec1,intersection_point_vec2=construct_stencil(x_data_rows, y_data_rows, z_data_rows, row, col)
            store_angle_check.append(angle_check)
            store_intersection_point_vec1.append(intersection_point_vec1)

            cylindrical_unit_vectors=calculate_cylindrical_unit_vectors(point1)
            surface_normal_rTz=transform_vector_into_cylindrical(surface_normal_xyz,cylindrical_unit_vectors) #surface-normal might not point outwards from surface
            dir_surface_normal_rTz=ensure_outwards_normal(surface_normal_rTz,cylindrical_unit_vectors,point1,'lower',tile) #surface-normal points outwards.
            dir_surface_normal_rTz=dir_surface_normal_rTz.reshape(1,3)
            point1=point1.reshape(1,3)
            if count==0:
                store_vectors_rTz=dir_surface_normal_rTz
                store_positions_xyz=point1
            else:
                store_vectors_rTz=np.concatenate([store_vectors_rTz,dir_surface_normal_rTz])
                store_positions_xyz=np.concatenate([store_positions_xyz,point1])
            count=count+1
    return store_positions_xyz,store_vectors_rTz,x_data_rows,y_data_rows,z_data_rows,store_angle_check,store_intersection_point_vec1



def plot_surface_norms(store_positions_xyz,store_vectors_rTz,x_data_rows,y_data_rows,z_data_rows):
    """
    3D plot of surface normal vectors
    """
    fig=plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for i in range(len(x_data_rows)):
        plt.plot(x_data_rows[i],y_data_rows[i],z_data_rows[i],'o',linestyle='',color='k')
    for j in range(len(store_positions_xyz)):
        cylindrical_unit_vectors=calculate_cylindrical_unit_vectors(store_positions_xyz[j])
        outward_vector_xyz=create_vector_cartesian(store_vectors_rTz[j], cylindrical_unit_vectors, store_positions_xyz[j],1) #need to input correct position.. in this situation always input 1 rather than -1.
        plt.plot(outward_vector_xyz[0],outward_vector_xyz[1],outward_vector_xyz[2])
    plt.show()
    return

def transform_store_positions_into_cylind(store_positions_xyz):
    """
    transform store_position_xyz into cylindrical coordinates.
    """
    for i in range(len(store_positions_xyz)):
        radius_xy=(store_positions_xyz[i][0]**2+store_positions_xyz[i][1]**2)**0.5
        phi_xy=2*np.pi-np.abs((np.arcsin(store_positions_xyz[i][1]/radius_xy)))
        z_component=store_positions_xyz[i][2]
        element=np.array([radius_xy,phi_xy,z_component]).reshape(1,3)
        if i==0:
            store_positions_rTz=element
        else:
            store_positions_rTz=np.concatenate([store_positions_rTz,element])
    return store_positions_rTz


def lookup_surface_normal_near_probe(large_or_small_phi_edge,probe_position_rTz,store_positions_xyz,store_vectors_rTz,store_positions_rTz=None):
    """
    Locate the tile surface-normal that is closest to a probe.
    Probes are located at tile boundaries (e.g. T2-T2 but not T2-T3).
    large_or_small_phi_edge='large' would take surface-normal of tile from the largest phi values.
    large_or_small_phi_edge='small' would take surface-normal of tile from the smallest phi values.
    At extremes of phi, expect difference in 'height' of tile due to toroidal shadowing.
    The output is dependent on z polarity in position of probe.
    """
    if store_positions_rTz is None:
        store_positions_rTz=transform_store_positions_into_cylind(store_positions_xyz)
    if large_or_small_phi_edge=='large':
        max_phi=max(store_positions_rTz[:,1])
        indices_interest,=np.where(store_positions_rTz[:,1]>max_phi-1e-4)
    if large_or_small_phi_edge=='small':
        min_phi=min(store_positions_rTz[:,1])
        indices_interest,=np.where(store_positions_rTz[:,1]<min_phi+1e-4)
    interest_positions=store_positions_rTz[indices_interest,:]
    interest_vectors=store_vectors_rTz[indices_interest,:]
    if probe_position_rTz[2]>=0: #probes located UPPER
        z_pol=-1
    else:
        z_pol=1 #probes located LOWER
    probe_z=probe_position_rTz[2]*z_pol #should always be negative
    rz_diff=((probe_position_rTz[0]-interest_positions[:,0])**2+(probe_z-interest_positions[:,2])**2)**0.5
    final_index,=np.where(rz_diff==min(rz_diff))[0]
    probe_tile_SN_rTz=np.array([interest_vectors[final_index,0],interest_vectors[final_index,1],interest_vectors[final_index,2]*z_pol]).reshape(1,3)
    probe_csvtile_position_rTz=np.array([interest_positions[final_index,0],interest_positions[final_index,1],interest_positions[final_index,2]*z_pol]).reshape(1,3)
    return probe_tile_SN_rTz,probe_csvtile_position_rTz







def cartesian_to_cylindrical_position_coordinates_list(store_positions_xyz):
    """
    convert position coordinates in cartesian coordinates to cylindrical coordinates.
    """
    store_positions_rTz=[]
    for i in range(len(store_positions_xyz)):
        x_data_i=store_positions_xyz[i][0]
        y_data_i=store_positions_xyz[i][1]
        radius_data_i=(x_data_i**2+y_data_i**2)**0.5
        phi_data_i=np.arcsin(y_data_i/radius_data_i)+2*np.pi
        if phi_data_i>=2.*np.pi:
            phi_data_i=phi_data_i-2.*np.pi
        store_positions_rTz.append(np.array([radius_data_i,phi_data_i,store_positions_xyz[i][2]]))
    return store_positions_rTz


def cartesian_to_cylindrical_position_coordinates_rows(x_data_rows, y_data_rows, z_data_rows):
    """
    convert position coordinates in cartesian coordinates to cylindrical coordinates.
    """
    store_positions_rTz=[]
    for ii in range(len(x_data_rows)):
        temp_store=[]
        for jj in range(len(x_data_rows[ii])):
            x_data_i=x_data_rows[ii][jj]
            y_data_i=y_data_rows[ii][jj]
            radius_data_i=(x_data_i**2+y_data_i**2)**0.5
            phi_data_i=np.arcsin(y_data_i/radius_data_i)+2*np.pi
            if phi_data_i>2.*np.pi-1e-6:
                phi_data_i=0
            temp_store.append(np.array([radius_data_i,phi_data_i,z_data_rows[ii][jj]]))
        store_positions_rTz.append(temp_store)
    return store_positions_rTz

def generate_surface_norm_single_location(tile, probe_r,probe_z,phi_high_low_z,method):
    tile_name=tile
    if tile=='T2':
        max_phi=0
        min_phi=-15*np.pi/180
    if tile=='T3':
        max_phi=0
        min_phi=-15*np.pi/180
    if tile=='T4':
        max_phi=0
        min_phi=-15*np.pi/180
    if tile=='T5':
        min_phi=-7.5*np.pi/180
        max_phi=0
        tile_name='T5A'
        #min_phi=-30*np.pi/180
        #max_phi=-22.5*np.pi/180
        #tile_name='T5D' #use D for high z
    if tile=='N1':
        max_phi=0
        min_phi=-15*np.pi/180
    if tile=='N2':
        max_phi=0
        min_phi=-15*np.pi/180

    filename=tile_name+'.csv'

    x_data_rows, y_data_rows, z_data_rows=tile_rows_cut(filename,min_phi,max_phi)
    store_positions_rTz=cartesian_to_cylindrical_position_coordinates_rows(x_data_rows, y_data_rows, z_data_rows)
    if phi_high_low_z=='high':
        if z_data_rows[0][0]>z_data_rows[0][-1]:
            probe_phi_col=0
        else:
            probe_phi_col=-1
    if phi_high_low_z=='low':
        if z_data_rows[0][0]>z_data_rows[0][-1]:
            probe_phi_col=-1
        else:
            probe_phi_col=0
#probes are usually located at tile edges.
    diff=[]
    for ii in range(len(store_positions_rTz)):
        diff.append(((store_positions_rTz[ii][probe_phi_col][0]-probe_r)**2+(store_positions_rTz[ii][probe_phi_col][2]-probe_z)**2)**0.5)
    row_index_closest=np.where(np.abs(diff)==np.nanmin(np.abs(diff)))
    if np.nanmin(np.abs(diff))>1e-3:
        print(np.nanmin(np.abs(diff)))
    row_index_closest=row_index_closest[0]
    if type(row_index_closest)==np.ndarray:
        row_index_closest=row_index_closest[0]
    point1,point2,point3=three_points(x_data_rows, y_data_rows, z_data_rows, row_index_closest, probe_phi_col,method) #points on a tile surface z<0
    surface_normal_xyz=calculate_surface_normal_xyz(point1,point2,point3)
    cylindrical_unit_vectors=calculate_cylindrical_unit_vectors(point1)
    surface_normal_rTz=transform_vector_into_cylindrical(surface_normal_xyz,cylindrical_unit_vectors) #surface-normal might not point outwards from surface
    dir_surface_normal_rTz=ensure_outwards_normal(surface_normal_rTz,cylindrical_unit_vectors,point1,'lower',tile) #surface-normal points outwards.
    dir_surface_normal_rTz=dir_surface_normal_rTz
    return dir_surface_normal_rTz,point1


store_positions_xyz,store_vectors_rTz,x_data_rows,y_data_rows,z_data_rows,store_angle_check,store_intersection_point_vec1=generate_surface_norms_stencils(tile,min_phi,max_phi, row_resolution, column_resolution)
store_positions_rTz=cartesian_to_cylindrical_position_coordinates_list(store_positions_xyz)
print(tile)
for i in range(len(store_vectors_rTz)):
    tile_check=tile
    if tile=='T5A' or tile=='T5B' or tile=='T5C' or tile=='T5D':
        tile_check='T5'
    store_vectors_shift_r, store_vectors_shift_z=RZ_shifts_rotation_only(store_vectors_rTz[i][0],store_vectors_rTz[i][2],tile_check,'lower')
    store_vectors_rTz_shift_ii=np.array([[store_vectors_shift_r, store_vectors_rTz[i][1],store_vectors_shift_z]])

    store_positions_shift_r, store_positions_shift_z=RZ_shifts_single_position(store_positions_rTz[i][0],store_positions_rTz[i][2],tile_check,'lower')
    store_positions_rTz_shift_ii=np.array([[store_positions_shift_r, store_positions_rTz[i][1],store_positions_shift_z]])
    if i==0:
        store_vectors_rTz_noshift=store_vectors_rTz[i].reshape(1,3)
        store_positions_rTz_noshift=store_positions_rTz[i].reshape(1,3)
        store_vectors_rTz_shift=store_vectors_rTz_shift_ii
        store_positions_rTz_shift=store_positions_rTz_shift_ii
    else:
        store_positions_rTz_noshift=np.concatenate([store_positions_rTz_noshift,store_positions_rTz[i].reshape(1,3)],axis=0)
        store_vectors_rTz_noshift=np.concatenate([store_vectors_rTz_noshift,store_vectors_rTz[i].reshape(1,3)],axis=0)
        store_positions_rTz_shift=np.concatenate([store_positions_rTz_shift,store_positions_rTz_shift_ii],axis=0)
        store_vectors_rTz_shift=np.concatenate([store_vectors_rTz_shift,store_vectors_rTz_shift_ii],axis=0)
    print(str(100*i/len(store_vectors_rTz))+'%')
#    if i==1000:
#        print(i)
#    if i==4500:
#        print(i)
#    if i==8000:
#        print(i)

print('now saving data in csv')

with open((tile)+'_no_shift_surface_normals.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["position_x", "position_y","position_r", "position_phi", "position_z","vector_r", "vector_phi", "vector_z","position_x_check","position_y_check","position_z_check","dot_product_angle"])
    for i in range(len(store_vectors_rTz_noshift)):
        writer.writerow([store_positions_xyz[i,0],store_positions_xyz[i,1],store_positions_rTz_noshift[i,0], store_positions_rTz_noshift[i,1], store_positions_rTz_noshift[i,2], store_vectors_rTz_noshift[i,0], store_vectors_rTz_noshift[i,1], store_vectors_rTz_noshift[i,2],store_intersection_point_vec1[i][0],store_intersection_point_vec1[i][1],store_intersection_point_vec1[i][2], store_angle_check[i] ])
print('noshift written')


with open((tile)+'_shift_surface_normals.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["position_x", "position_y", "position_r_shift", "position_phi", "position_z_shift","vector_r_shift", "vector_phi_shift", "vector_z_shift"])
    for i in range(len(store_vectors_rTz_shift)):
        writer.writerow([store_positions_xyz[i,0],store_positions_xyz[i,1],store_positions_rTz_shift[i,0], store_positions_rTz_shift[i,1],store_positions_rTz_shift[i,2], store_vectors_rTz_shift[i,0], store_vectors_rTz_shift[i,1], store_vectors_rTz_shift[i,2] ])
print('shift written')

#with open((tile)+'_no_shift_surface_normals_stencil.csv', 'w', newline='') as file:
#    writer = csv.writer(file)
#    writer.writerow(["position_x", "position_y","position_r", "position_phi", "position_z","vector_r", "vector_phi", "vector_z"])
#    for i in range(len(store_vectors_rTz_noshift)):
#        writer.writerow([store_positions_xyz[i,0],store_positions_xyz[i,1],store_positions_rTz_noshift[i][0], store_positions_rTz_noshift[i][1], store_positions_rTz_noshift[i][2], store_vectors_rTz_noshift[i][0], store_vectors_rTz_noshift[i][1], store_vectors_rTz_noshift[i][2] ])
#print('noshift written')
