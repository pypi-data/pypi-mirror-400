import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
from scipy.optimize import fsolve
import csv
def func(x,args):
    #args[0] is the rz plane angle
    #args[1] is the phi_z plane angle
    return [np.cos(args[0])*(x[0]**2+x[2]**2)**0.5 - x[2],
            np.cos(args[1])*(x[0]**2+x[2]**2)**0.5 - x[0]**2 - x[2]**2,
            -1+(x[0]**2+x[1]**2+x[2]**2)**0.5]

#T2
tile='T2'
start_r=0.333+297*np.cos(45*np.pi/180)/1000
end_r=start_r+510*np.cos(45*np.pi/180)/1000

#start_z=-1.452982601
#end_z=-1.928434207
#rz_angle=np.arctan((end_z-start_z)/(end_r-start_r)) csv file has resolution issues!
rz_angle=np.pi/4
r_axis=np.linspace(start_r,end_r,1000)
step=3e-3
N_tiles=24
gap=0e-3
toroidal_length=((2*np.pi*r_axis-N_tiles*gap)/N_tiles)
phi_z_angle=np.arctan(step/toroidal_length)
SN_r=[]
SN_phi=[]
SN_z=[]
magnitude=[]
for ii in range(len(r_axis)):
    root = fsolve(func, args=[rz_angle,phi_z_angle[ii]], x0=[0.7, 0.02,0.7])
    SN_r.append(root[0])
    SN_z.append(root[2])
    if root[1]<0:
        SN_phi.append(-1*root[1])
    else:
        SN_phi.append(root[1])
    magnitude.append((root[0]**2+root[1]**2+root[2]**2)**0.5)

with open('T2_SN.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["position_r", "vector_r", "vector_phi", "vector_z"])
    for ii in range(len(r_axis)):
        writer.writerow([ r_axis[ii], SN_r[ii], SN_phi[ii], SN_z[ii] ])

r_poly_coeffs= np.polyfit(r_axis, SN_r, 5)
r_poly=np.poly1d(r_poly_coeffs)
r_fit=r_poly(r_axis)

phi_poly_coeffs= np.polyfit(r_axis, SN_phi, 5)
phi_poly=np.poly1d(phi_poly_coeffs)
phi_fit=phi_poly(r_axis)

z_poly_coeffs= np.polyfit(r_axis, SN_z, 5)
z_poly=np.poly1d(z_poly_coeffs)
z_fit=z_poly(r_axis)

plt.figure()
plt.title(tile)
plt.scatter(r_axis,SN_r,label='Radial')
plt.plot(r_axis,r_fit,'k')
plt.scatter(r_axis,SN_phi,label='phi')
plt.plot(r_axis,phi_fit,'k')
plt.scatter(r_axis,SN_z,label='Z')
plt.plot(r_axis,z_fit,'k')
plt.ylabel('SN component')
plt.xlabel('Radial position (m)')
plt.legend()
plt.show()
##################################################
#T3
tile='T3'
start_r=0.90
end_r=1.090

#start_z=-1.452982601
#end_z=-1.928434207
#rz_angle=np.arctan((end_z-start_z)/(end_r-start_r)) csv file has resolution issues!
rz_angle=np.pi/4-(0.4431*np.pi/180)#-(0.444*np.pi/180)
r_axis=np.linspace(start_r,end_r,1000)
step=3e-3
N_tiles=24
gap=0e-3
toroidal_length=((2*np.pi*r_axis-N_tiles*gap)/N_tiles)
phi_z_angle=np.arctan(step/toroidal_length)
SN_r=[]
SN_phi=[]
SN_z=[]
magnitude=[]
for ii in range(len(r_axis)):
    root = fsolve(func, args=[rz_angle,phi_z_angle[ii]], x0=[0.7, 0.02,0.7])
    SN_r.append(root[0])
    SN_z.append(root[2])
    if root[1]<0:
        SN_phi.append(-1*root[1])
    else:
        SN_phi.append(root[1])
    magnitude.append((root[0]**2+root[1]**2+root[2]**2)**0.5)

with open('T3_SN.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["position_r", "vector_r", "vector_phi", "vector_z"])
    for ii in range(len(r_axis)):
        writer.writerow([ r_axis[ii], SN_r[ii], SN_phi[ii], SN_z[ii] ])
r_poly_coeffs= np.polyfit(r_axis, SN_r, 5)
r_poly=np.poly1d(r_poly_coeffs)
r_fit=r_poly(r_axis)

phi_poly_coeffs= np.polyfit(r_axis, SN_phi, 5)
phi_poly=np.poly1d(phi_poly_coeffs)
phi_fit=phi_poly(r_axis)

z_poly_coeffs= np.polyfit(r_axis, SN_z, 5)
z_poly=np.poly1d(z_poly_coeffs)
z_fit=z_poly(r_axis)

plt.figure()
plt.title(tile)
plt.scatter(r_axis,SN_r,label='Radial')
plt.plot(r_axis,r_fit,'k')
plt.scatter(r_axis,SN_phi,label='phi')
plt.plot(r_axis,phi_fit,'k')
plt.scatter(r_axis,SN_z,label='Z')
plt.plot(r_axis,z_fit,'k')
plt.ylabel('SN component')
plt.xlabel('Radial position (m)')
plt.legend()
plt.show()
##################################################
#T4 tile
tile='T4'
start_r=1.09
end_r=1.35
rz_angle=0
r_axis=np.linspace(start_r,end_r,1000)
step=3e-3
N_tiles=24
phi_z_angle=np.arctan(step*N_tiles/(2*np.pi*r_axis))
SN_r=[]
SN_phi=[]
SN_z=[]
magnitude=[]
for ii in range(len(r_axis)):
    root = fsolve(func, args=[rz_angle,phi_z_angle[ii]], x0=[0, 0.02,0.99])
    SN_r.append(root[0])
    SN_z.append(root[2])
    if root[1]<0:
        SN_phi.append(-1*root[1])
    else:
        SN_phi.append(root[1])
    magnitude.append((root[0]**2+root[1]**2+root[2]**2)**0.5)

with open('T4_SN.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["position_r", "vector_r", "vector_phi", "vector_z"])
    for ii in range(len(r_axis)):
        writer.writerow([ r_axis[ii], SN_r[ii], SN_phi[ii], SN_z[ii] ])

r_poly_coeffs= np.polyfit(r_axis, SN_r, 5)
r_poly=np.poly1d(r_poly_coeffs)
r_fit=r_poly(r_axis)

phi_poly_coeffs= np.polyfit(r_axis, SN_phi, 5)
phi_poly=np.poly1d(phi_poly_coeffs)
phi_fit=phi_poly(r_axis)

z_poly_coeffs= np.polyfit(r_axis, SN_z, 5)
z_poly=np.poly1d(z_poly_coeffs)
z_fit=z_poly(r_axis)

plt.figure()
plt.title(tile)
plt.scatter(r_axis,SN_r,label='Radial')
plt.plot(r_axis,r_fit,'k')
plt.scatter(r_axis,SN_phi,label='phi')
plt.plot(r_axis,phi_fit,'k')
plt.scatter(r_axis,SN_z,label='Z')
plt.plot(r_axis,z_fit,'k')
plt.ylabel('SN component')
plt.xlabel('Radial position (m)')
plt.legend()
plt.show()
##################################################
#T5
tile='T5'
start_r=1.35
end_r=start_r+np.cos(45*np.pi/180)*480/1000

#start_z=-1.452982601
#end_z=-1.928434207
#rz_angle=np.arctan((end_z-start_z)/(end_r-start_r)) csv file has resolution issues!
rz_angle=np.pi/4
r_axis=np.linspace(start_r,end_r,1000)
#step=1.6e-3
step=1.5e-3
N_tiles=48
gap=0e-3
toroidal_length=((2*np.pi*r_axis-N_tiles*gap)/N_tiles)
phi_z_angle=np.arctan(step/toroidal_length)
SN_r=[]
SN_phi=[]
SN_z=[]
magnitude=[]
for ii in range(len(r_axis)):
    root = fsolve(func, args=[rz_angle,phi_z_angle[ii]], x0=[0.7, 0.02,0.7])
    SN_r.append(-root[0])
    SN_z.append(root[2])
    if root[1]<0:
        SN_phi.append(-1*root[1])
    else:
        SN_phi.append(root[1])
    magnitude.append((root[0]**2+root[1]**2+root[2]**2)**0.5)

with open('T5_SN.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["position_r", "vector_r", "vector_phi", "vector_z"])
    for ii in range(len(r_axis)):
        writer.writerow([ r_axis[ii], SN_r[ii], SN_phi[ii], SN_z[ii] ])
r_poly_coeffs= np.polyfit(r_axis, SN_r, 5)
r_poly=np.poly1d(r_poly_coeffs)
r_fit=r_poly(r_axis)

phi_poly_coeffs= np.polyfit(r_axis, SN_phi, 5)
phi_poly=np.poly1d(phi_poly_coeffs)
phi_fit=phi_poly(r_axis)

z_poly_coeffs= np.polyfit(r_axis, SN_z, 5)
z_poly=np.poly1d(z_poly_coeffs)
z_fit=z_poly(r_axis)

plt.figure()
plt.title(tile)
plt.scatter(r_axis,SN_r,label='Radial')
plt.plot(r_axis,r_fit,'k')
plt.scatter(r_axis,SN_phi,label='phi')
plt.plot(r_axis,phi_fit,'k')
plt.scatter(r_axis,SN_z,label='Z')
plt.plot(r_axis,z_fit,'k')
plt.ylabel('SN component')
plt.xlabel('Radial position (m)')
plt.legend()
plt.show()

##################################################
