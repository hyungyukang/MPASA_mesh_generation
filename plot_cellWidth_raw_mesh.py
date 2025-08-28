################################################################################
# Displaying cell width of a raw MPAS-A mesh
#
# Author: Hyun Kang (ORNL)
# Date: 08/28/2025
################################################################################

import numpy as np
import xarray as xr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import cartopy.crs as ccrs

# --- File name ---
fileName = "base_test_mesh.nc"

# --- load ---
ds = xr.open_dataset(fileName)

lon = ds["lonCell"].values * (180.0/np.pi)
lat = ds["latCell"].values * (180.0/np.pi)
val = np.sqrt(ds["areaCell"].values) / 1000.0

# --- sanitize ---
m = np.isfinite(lon) & np.isfinite(lat) & np.isfinite(val)
lon = lon[m]; lat = lat[m]; val = val[m]

# if nothing to plot, fail early (prevents zero-size errors later)
if lon.size < 3:
    raise ValueError(f"No valid points to plot (finite count={lon.size}).")

# wrap longitudes to [-180, 180]
lon = ((lon + 180.0) % 360.0) - 180.0

# --- levels ---
nlevels = 251
vmin = float(np.nanmin(val))
vmax = float(np.nanmax(val))

if not np.isfinite(vmin) or not np.isfinite(vmax) or vmin == vmax:
    vmin, vmax = 0.0, (vmin if np.isfinite(vmin) else 0.0) + 1e-6
levels = np.linspace(vmin, vmax, nlevels)

# --- plot WITHOUT cartopy ---
tri = mtri.Triangulation(lon, lat)

# --- plot with Cartopy ---
fig = plt.figure(figsize=(12, 7))
ax = plt.axes(projection=ccrs.PlateCarree())

cn = ax.tricontourf(tri, val, levels=levels, cmap='terrain',
                    antialiased=False, extend="both")


ax.coastlines(linewidth=0.8, color="k")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title("Cell width (km)")

tick_idx = np.arange(0, len(levels), 25)
cbar = plt.colorbar(cn, orientation="horizontal", pad=0.08, fraction=0.05)
cbar.set_ticks(levels[tick_idx])
cbar.set_label("Cell width (km)")
cbar.ax.set_xticklabels([f"{v:.2f}" for v in levels[tick_idx]])

ax.set_xlim(lon.min()-2, lon.max()+2)
ax.set_ylim(lat.min()-2, lat.max()+2)
ax.set_aspect("equal", adjustable="box")  # degrees on both axes

plt.tight_layout()
plt.savefig("fig_mesh_cellWidth.png", dpi=120, bbox_inches="tight")
plt.close(fig)
