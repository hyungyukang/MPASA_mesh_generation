#!/usr/bin/env python

################################################################################
# A script for creating spherical mesh for MPAS-A
#
# This script is designed to create a sphercial mesh for MPAS-A by leveraging
# MPAS-Tools (https://mpas-dev.github.io/MPAS-Tools/master/index.html).
# Users need to change 'config_mesh.xml' accordingly to configure a mesh.
#
# Author: Hyun Kang (ORNL)
# Date: 05/25/2025
################################################################################

import numpy as np
import mpas_tools
from mpas_tools.ocean import build_spherical_mesh
#from mpas_tools.parallel import create_pool
import csv
from io import StringIO
import xml.etree.ElementTree as ET
import math
import matplotlib
matplotlib.use("Agg")
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
import cartopy.feature as cfeature
import cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
from cartopy.util import add_cyclic_point


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees).
    Source: https://gis.stackexchange.com/a/56589/15183
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    km = 6371000.0 * c
    return km

def str2bool(s: str) -> bool:
    return s.strip().lower() in ("true", "1", "yes", "on")

def cellWidthVsLatLon():
    """
    Create cell width array for this mesh on a regular latitude-longitude grid.
    Returns
    -------
    cellWidth : ndarray
        m x n array of cell width in km
    lon : ndarray
        longitude in degrees (length n and between -180 and 180)
    lat : ndarray
        longitude in degrees (length m and between -90 and 90)
    """

    #-------------------------------------------------------------------------#

    # Read config_mesh.xml
    tree = ET.parse("./config_mesh.xml")
    root = tree.getroot()
    dxWindowConst = str2bool(root.find("dxWindowConst").text)

    maxdx = float(root.find("dxMax").text)
    if (dxWindowConst):
       mindx = float(root.find("dxMin").text)

       if ( mindx == maxdx ):
          meshType = "QU"
       else:
          meshType = "VR"
    else:
       meshType = "VR"

    # Windows info
    if ( meshType == "VR" ):

       clat = []
       clon = []
       diam = []
       sigx = []
       dxMin = []

       raw_text = root.find("windowDxConst").text.strip()
       reader = csv.reader(StringIO(raw_text))
       rows = [tuple(map(float, row)) for row in reader]
       nw = len(rows) # Number of windows

       for iw in range(nw):
           clon.append(rows[iw][0])
           clat.append(rows[iw][1])
           diam.append(rows[iw][2])
           sigx.append(rows[iw][3])

       if ( dxWindowConst ):
          for iw in range(nw):
              dxMin.append(mindx)
       else:
          for iw in range(nw):
              dxMin.append(rows[iw][4])
    else:
       nw = 0 # nw = 0 for QU mesh

    foutName = root.find("outFileName").text
    dlat = float(root.find("dlatBase").text)
    dlon = float(root.find("dlonBase").text)

    #-------------------------------------------------------------------------#

    nlat = int(180/dlat) + 1 # Number of latitude grids
    nlon = int(360/dlon) + 1 # Number of longitude grids
    lat  = np.linspace(-90. , 90. , nlat)
    lon  = np.linspace(-180., 180., nlon)

    #-------------------------------------------------------------------------#


    print("=================================================================")
    if (meshType=="VR"):
       print("Mesh type =", meshType)
       print("Number of windows =", nw)
       print("Min DX (km) =", mindx)
       print("Max DX (km) =", maxdx)
       print("Window longitude =", clon[:])
       print("Window latitude  =", clat[:])
       print("Diameter (km) =", diam[:])
       print("Transition width (km) =", sigx[:])
    else:
       print("Mesh type =", meshType)
       print("DX (km) =", mindx)
    print("=================================================================")


    nlat = lat.shape[0]
    nlon = lon.shape[0]

    if ( nw > 0 ):
       cellWidth = np.zeros((nw,lat.size,lon.size))

       for k in range(nw):
           diam[k] = diam[k] * 1000.0
           sigx[k] = sigx[k]  * 1000.0

       amp = maxdx - mindx

       for k in range(nw):
           for j in range(nlat):
               for i in range(nlon):
                   # Error function
                   gdist = haversine(lon[i],lat[j],clon[k],clat[k])

                   # Flat for target area
                   if ( gdist < diam[k]/2.0):
                      cellWidth[k,j,i] = amp

                   # Smoothly change following Gaussian distribution
                   else:
                      tmp = 0.5*((gdist-diam[k]/2.0)/(sigx[k]))**2.0
                      cellWidth[k,j,i] = amp * np.exp(-tmp)

       cellWidth[0,:,:] = np.sum(cellWidth,axis=0)
       cellWidth[0,:,:] = np.where(cellWidth[0,:,:] < amp, cellWidth[0,:,:], amp)
       cellWidth[0,:,:] = maxdx - cellWidth[0,:,:]
    else:
       cellWidth = np.zeros((1,lat.size,lon.size))
       cellWidth[:,:,:] = maxdx

    #-------------------------------------------------------------------------#

    # Visualizing the base mesh in the lat-lon grid system
    fig = plt.figure(figsize=(6,3.0))
    ax=plt.axes(projection=ccrs.PlateCarree())

    if ( meshType == "VR"):
       levs = np.linspace(mindx,maxdx,num=21)
    else:
       levs = np.linspace(maxdx-(maxdx*0.01),maxdx+(maxdx*0.01),num=3)

    cs=ax.contourf(lon,lat,cellWidth[0,:,:],levels=levs,cmap='terrain',
                   transform = ccrs.PlateCarree(),extend='both')

    ax.coastlines(lw=0.5)

    ax.set_xticks(np.arange(-180,181,60), crs=ccrs.PlateCarree())
    lon_formatter = cticker.LongitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)

    ax.set_yticks(np.arange(-90,91,30), crs=ccrs.PlateCarree())
    lat_formatter = cticker.LatitudeFormatter()
    ax.yaxis.set_major_formatter(lat_formatter)

    ax.set_title('Cell width ('+meshType+') of the base mesh (km)')

    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='3%', pad=0.10, axes_class=plt.Axes)
    plt.colorbar(cs,cax=cax)
    plt.savefig("fig_base_mesh_latlon.png",bbox_inches='tight',dpi=200)
    plt.close()

    return cellWidth[0,:,:], lon, lat, foutName

    #-------------------------------------------------------------------------#

def main():
    # Obtain cellWidth array based on a mesh configuration
    cellWidth, lon, lat, outMeshName = cellWidthVsLatLon()

    # Create a spherical mesh with the cellWidth array
    build_spherical_mesh(cellWidth, lon, lat, out_filename=outMeshName,
                         do_inject_bathymetry=False, plot_cellWidth=False)

if __name__ == '__main__':
    main()
