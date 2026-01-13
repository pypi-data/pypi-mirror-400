# Create openEMS simulation models from GDSII layout files

gds2openEMS provides utility functions for an RFIC FEM simulation workflow based on the openEMS FDTD field solver.

The full repository with examples is available at 
https://github.com/VolkerMuehlhaus/openems_ihp_sg13g2


# Documentation
Extensive documentation on creating models using gds2openEMS available in PDF format here:
https://github.com/VolkerMuehlhaus/openems_ihp_sg13g2/tree/main/doc 

# Installation
To install the gds2openEMS module, activate the venv where you want to install.

Documentation for the gds2openEMS workflow assumes that you have created a Python venv 
named "openems" in ~/venv/openems and installed the modules there, including the Python modules that come with openEMS itself.

If you follow this, you would first activate the venv: 
```
    source ~\venv\openems\bin\activate
```
and then install gds2openEMS module and dependencies via PyPI: 
```
    pip install gds2openEMS    
```

To upgrade to the latest version, do 
```
    pip install gds2openEMS --upgrade   
```



# Dependencies
This module also installs these dependencies:
    gdspy > 1.6.0

In addition, you need to install the Python module that ship with openEMS as described there: 
https://docs.openems.de/python/install.html#python-linux-install 

# Example script using gds2palace
Below is an example script that create *.json and *msh input files for simulation with Palace.
Input is a layout in GDSII file format and an XML file with stackup information

```python
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules')))
from modules import *

from openEMS import openEMS
import numpy as np


# Model comments
# 
# This is a generic model running port excitation for all ports defined below, 
# to get full [S] matrix data.
# Output is stored to Touchstone S-parameter file. 
# No data plots are created by this script.


# ======================== workflow settings ================================

# preview model/mesh only?
# postprocess existing data without re-running simulation?
preview_only = True
postprocess_only = False

# ===================== input files and path settings =======================

gds_filename = "line_simple_viaport.gds"   # geometries
XML_filename = "SG13G2_nosub.xml"          # stackup

# preprocess GDSII for safe handling of cutouts/holes?
preprocess_gds = False

# merge via polygons with distance less than .. microns, set to 0 to disable via merging.
merge_polygon_size = 0


# get path for this simulation file
script_path = utilities.get_script_path(__file__)
# use script filename as model basename
model_basename = utilities.get_basename(__file__)
# set and create directory for simulation output
sim_path = utilities.create_sim_path (script_path,model_basename)
print('Simulation data directory: ', sim_path)
# change current path to model script path
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ======================== simulation settings ================================

unit   = 1e-6  # geometry is in microns
margin = 50    # distance in microns from GDSII geometry boundary to simulation boundary 

fstart =  0e9
fstop  = 110e9
numfreq = 401

refined_cellsize = 1  # mesh cell size in conductor region

# choices for boundary: 
# 'PEC' : perfect electric conductor (default)
# 'PMC' : perfect magnetic conductor, useful for symmetries
# 'MUR' : simple MUR absorbing boundary conditions
# 'PML_8' : PML absorbing boundary conditions
Boundaries = ['PEC', 'PEC', 'PEC', 'PEC', 'PEC', 'PEC']

cells_per_wavelength = 20   # how many mesh cells per wavelength, must be 10 or more
energy_limit = -40          # end criteria for residual energy (dB)

# port configuration, port geometry is read from GDSII file on the specified layer
simulation_ports = simulation_setup.all_simulation_ports()

# in-plane port is specified with target_layername= and direction x or y
# via port is specified with from_layername= and to_layername= and direction z
simulation_ports.add_port(simulation_setup.simulation_port(portnumber=1, 
                                                           voltage=1, 
                                                           port_Z0=50, 
                                                           source_layernum=201, 
                                                           from_layername='Metal1', 
                                                           to_layername='TopMetal2', 
                                                           direction='z'))

simulation_ports.add_port(simulation_setup.simulation_port(portnumber=2, 
                                                           voltage=1, 
                                                           port_Z0=50, 
                                                           source_layernum=202, 
                                                           from_layername='Metal1', 
                                                           to_layername='TopMetal2', 
                                                           direction='z'))

# ======================== simulation ================================

# get technology stackup data
materials_list, dielectrics_list, metals_list = stackup_reader.read_substrate (XML_filename)
# get list of layers from technology
layernumbers = metals_list.getlayernumbers()
# we must also read the layers where we added ports, these are not included in technology layers
layernumbers.extend(simulation_ports.portlayers)

# read geometries from GDSII, only purpose 0
allpolygons = gds_reader.read_gds(gds_filename, 
                                  layernumbers, 
                                  purposelist=[0], 
                                  metals_list=metals_list, 
                                  preprocess=preprocess_gds, 
                                  merge_polygon_size=merge_polygon_size)

# calculate maximum cellsize from wavelength in dielectric
wavelength_air = 3e8/fstop / unit
max_cellsize = (wavelength_air)/(np.sqrt(materials_list.eps_max)*cells_per_wavelength) 

# define excitation and stop criteria and boundaries
FDTD = openEMS(EndCriteria=np.exp(energy_limit/10 * np.log(10)))
FDTD.SetGaussExcite( (fstart+fstop)/2, (fstop-fstart)/2 )
FDTD.SetBoundaryCond( Boundaries )


########### create model, run and post-process ###########

# run all port excitations, one after another

for port in simulation_ports.ports:
    simulation_setup.setupSimulation   ([port.portnumber], 
                                        simulation_ports, 
                                        FDTD, 
                                        materials_list, 
                                        dielectrics_list, 
                                        metals_list, 
                                        allpolygons, 
                                        max_cellsize, 
                                        refined_cellsize, 
                                        margin, 
                                        unit, 
                                        xy_mesh_function=util_meshlines.create_xy_mesh_from_polygons)
    
    simulation_setup.runSimulation  ([port.portnumber], 
                                        FDTD, 
                                        sim_path, 
                                        model_basename, 
                                        preview_only, 
                                        postprocess_only)


# Initialize an empty matrix for S-parameters
num_ports = simulation_ports.portcount
s_params = np.empty((num_ports, num_ports, numfreq), dtype=object)

# Define frequency resolution. Due to FFT from Empire time domain results, 
# this is postprocessing and we can change it again at any time.
f = np.linspace(fstart,fstop,numfreq)

# Populate the S-parameter matrix with simulation results
for i in range(1, num_ports + 1):
    for j in range(1, num_ports + 1):
        s_params[i-1, j-1] = utilities.calculate_Sij(i, j, f, sim_path, simulation_ports)

# Write to Touchstone *.snp file
snp_name = os.path.join(sim_path, model_basename + '.s' + str(num_ports) + 'p')
utilities.write_snp(s_params, f, snp_name)

print('Created S-parameter output file at ', snp_name)

```

XML file for this example:

```xml
<Stackup schemaVersion="2.0">
<Materials>
<Material Name="Activ" Type="Conductor" Permittivity="1" DielectricLossTangent="0" Conductivity="357141.0" Color="00ff00"/>
<Material Name="Metal1" Type="Conductor" Permittivity="1" DielectricLossTangent="0" Conductivity="21640000.0" Color="39bfff"/>
<Material Name="Metal2" Type="Conductor" Permittivity="1" DielectricLossTangent="0" Conductivity="23190000.0" Color="ccccd9"/>
<Material Name="Metal3" Type="Conductor" Permittivity="1" DielectricLossTangent="0" Conductivity="23190000.0" Color="d80000"/>
<Material Name="Metal4" Type="Conductor" Permittivity="1" DielectricLossTangent="0" Conductivity="23190000.0" Color="93e837"/>
<Material Name="Metal5" Type="Conductor" Permittivity="1" DielectricLossTangent="0" Conductivity="23190000.0" Color="dcd146"/>
<Material Name="TopMetal1" Type="Conductor" Permittivity="1" DielectricLossTangent="0" Conductivity="27800000.0" Color="ffe6bf"/>
<Material Name="TopMetal2" Type="Conductor" Permittivity="1" DielectricLossTangent="0" Conductivity="30300000.0" Color="ff8000"/>
<Material Name="TopVia2" Type="Conductor" Permittivity="1" DielectricLossTangent="0" Conductivity="3143000.0" Color="ff8000"/>
<Material Name="TopVia1" Type="Conductor" Permittivity="1" DielectricLossTangent="0" Conductivity="2191000.0" Color="ffe6bf"/>
<Material Name="Via4" Type="Conductor" Permittivity="1" DielectricLossTangent="0" Conductivity="1660000.0" Color="deac5e"/>
<Material Name="Via3" Type="Conductor" Permittivity="1" DielectricLossTangent="0" Conductivity="1660000.0" Color="9ba940"/>
<Material Name="Via2" Type="Conductor" Permittivity="1" DielectricLossTangent="0" Conductivity="1660000.0" Color="ff3736"/>
<Material Name="Via1" Type="Conductor" Permittivity="1" DielectricLossTangent="0" Conductivity="1660000.0" Color="ccccff"/>
<Material Name="Cont" Type="Conductor" Permittivity="1" DielectricLossTangent="0" Conductivity="2390000.0" Color="00ffff"/>
<Material Name="Passive" Type="Dielectric" Permittivity="6.6" DielectricLossTangent="0.0" Conductivity="0" Color="a0a0f0"/>
<Material Name="SiO2" Type="Dielectric" Permittivity="4.1" DielectricLossTangent="0.0" Conductivity="0" Color="fffcad"/>
<Material Name="Substrate" Type="Semiconductor" Permittivity="11.9" DielectricLossTangent="0" Conductivity="2.0" Color="01e0ff"/>
<Material Name="EPI" Type="Semiconductor" Permittivity="11.9" DielectricLossTangent="0" Conductivity="5.0" Color="294fff"/>
<Material Name="AIR" Type="Dielectric" Permittivity="1.0" DielectricLossTangent="0.0" Conductivity="0" Color="d0d0d0"/>
<Material Name="LOWLOSS" Type="Conductor" Permittivity="1" DielectricLossTangent="0" Conductivity="1E10" Color="ff0000"/>
<Material Name="MIM_equiv" Type="Dielectric" Permittivity="16.87" DielectricLossTangent="0.0" Conductivity="0" Color="ff0000"/>
<Material Name="SiO2" Type="Dielectric" Permittivity="4.1" DielectricLossTangent="0.0" Conductivity="0" Color="fffcad"/>
</Materials>
<ELayers LengthUnit="um">
<Dielectrics>
<Dielectric Name="AIR" Material="AIR" Thickness="300.0000"/>
<Dielectric Name="Passive" Material="Passive" Thickness="0.4000"/>
<Dielectric Name="SiO2" Material="SiO2" Thickness="15.7303"/>
<!--  Comment: Material name SiO2 is excluded from meshing, so we must use a different name to add some spacing at the bottom of the simulation box  -->
<Dielectric Name="Spacing" Material="SiO2" Thickness="2.0"/>
</Dielectrics>
<Layers>
<Substrate Offset="2.0"/>
<Layer Name="Activ" Type="conductor" Zmin="0.0000" Zmax="0.4000" Material="Activ" Layer="1"/>
<Layer Name="Metal1" Type="conductor" Zmin="1.0400" Zmax="1.4600" Material="Metal1" Layer="8"/>
<Layer Name="Metal2" Type="conductor" Zmin="2.0000" Zmax="2.4900" Material="Metal2" Layer="10"/>
<Layer Name="Metal3" Type="conductor" Zmin="3.0300" Zmax="3.5200" Material="Metal3" Layer="30"/>
<Layer Name="Metal4" Type="conductor" Zmin="4.0600" Zmax="4.5500" Material="Metal4" Layer="50"/>
<Layer Name="Metal5" Type="conductor" Zmin="5.0900" Zmax="5.5800" Material="Metal5" Layer="67"/>
<Layer Name="TopMetal1" Type="conductor" Zmin="6.4303" Zmax="8.4303" Material="TopMetal1" Layer="126"/>
<Layer Name="TopMetal2" Type="conductor" Zmin="11.2303" Zmax="14.2303" Material="TopMetal2" Layer="134"/>
<Layer Name="TopVia2" Type="via" Zmin="8.4303" Zmax="11.2303" Material="TopVia2" Layer="133"/>
<Layer Name="TopVia1" Type="via" Zmin="5.5800" Zmax="6.4303" Material="TopVia1" Layer="125"/>
<Layer Name="Via4" Type="via" Zmin="4.5500" Zmax="5.0900" Material="Via4" Layer="66"/>
<Layer Name="Via3" Type="via" Zmin="3.5200" Zmax="4.0600" Material="Via3" Layer="49"/>
<Layer Name="Via2" Type="via" Zmin="2.4900" Zmax="3.0300" Material="Via2" Layer="29"/>
<Layer Name="Via1" Type="via" Zmin="1.4600" Zmax="2.0000" Material="Via1" Layer="19"/>
<Layer Name="Cont" Type="via" Zmin="0.4000" Zmax="1.0400" Material="Cont" Layer="6"/>
<Layer Name="MIM_DK" Type="conductor" Zmin="5.5800" Zmax="5.6800" Material="MIM_equiv" Layer="36"/>
<Layer Name="MIM" Type="conductor" Zmin="5.6800" Zmax="6.4303" Material="TopVia1" Layer="36"/>
</Layers>
</ELayers>
</Stackup>
```