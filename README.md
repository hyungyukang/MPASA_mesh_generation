# MPAS-A mesh creation instruction using MPAS-Tools

- Contact: Hyun Kang (kangh@ornl.gov)
- MPAS-Tools guide for more details:  https://mpas-dev.github.io/MPAS-Tools/master/index.html

## 1. Installing MPAS-Tools & activating conda Env.
```
conda create -n mpas_tools_env -c conda-forge mpas_tools
conda activate mpas_tools_env
conda install jigsawpy
```
- No need to install ‘jigsawpy’ after the first installation

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
    - A visualization of the mesh configuration in lat-lon grid
    - Users can check their mesh configuration with this figure while running the mesh creation program.
  - If python complains about ‘cartopy’,
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
