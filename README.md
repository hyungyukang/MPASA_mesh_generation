# MPAS-A mesh creation instruction using MPAS-Tools

- Contact: Hyun Kang (kangh@ornl.gov)
- MPAS-Tools guide for more details:  https://mpas-dev.github.io/MPAS-Tools/master/index.html

## 1. Installing MPAS-Tools & activating conda Env.
```
conda create -n mpas_tools_env -c conda-forge mpas_tools
conda activate mpas_tools_env
conda install jigsawpy
```
- There is no need to reinstall `jigsawpy` after the initial installation.

## 2. Changing ‘config_mesh.xml’
- Change ‘config_mesh.xml’ file accordingly

## 3. Running the script
- Run the script ‘mesh_gen_MPASA.py’
```
python mesh_gen_MPASA.py
```

- The script will create several files:
  - `base_mesh.nc` (outFileName in `config_mesh.xml`): A generated mesh
  - `graph.info`: Graph partition file of the mesh
  - `fig_base_mesh_latlon.png`
    - This is a quick visualization of the mesh configuration in the latitude-longitude grid.
    - Users can check the mesh configuration using this figure while running the mesh generation program.
  - If Python complains about ‘cartopy’,
    - Untar `cartopy.tar`
    ```
    tar xf cartopy.tar
    ```
    - Make a directory
    ```
    mkdir ~/.local/share/cartopy/shapefiles/natural_earth/physical
    ```
    - Copy files to the directory
    ```
    cp cartopy/* ~/.local/share/cartopy/shapefiles/natural_earth/physical/
    ```
## 4. Verification (optional): Visualize the generated mesh
- Change the mesh file name at line 17 of `plot_cellWidth_raw_mesh.py`
- Run the script ‘mesh_gen_MPASA.py’
```
python plot_cellWidth_raw_mesh.py
```
- Display the figure `fig_mesh_cellWidth.png`
