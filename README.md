<img src="https://images.squarespace-cdn.com/content/v1/58c95854c534a56689231265/1571418050553-F87MZCX17GDLDWW4SZCE/ke17ZwdGBToddI8pDm48kKvryBMD-s2r8Pv086kJRRIUqsxRUqqbr1mOJYKfIPR7LoDQ9mXPOjoJoqy81S2I8N_N4V1vUb5AoIIIbLZhVYxCRW4BPu10St3TBAUQYVKcN_mEHA4JpnSJ3dQYhueAobPiP7s_keov7WGkJAt2s1YGm3B8OM-YHGRgiLl8h7Jx/HeadEquipotencialsandModelDrains.png?format=1000w" alt="hataripy3" style="width:50;height:20">

Introduction
-----------------------------------------------

A new unofficial version of the Flopy is available as Hataripy. This “fork” has tools for the representation of many features, boundary conditions and output with options for grid smoothing. Documentation for this library is on progress as we expect to introduce other features and identify some bugs.

Currently the library can:

- Create the model mesh on the active zone with point and cell values

- Create a shell of the water table

- Create the geometry of any boundary condition


Installation
-----------------------------------------------
You can install the library by typing this line on the Anaconda Prompt if your are in Windows or in the Shell of Linux:

pip install -i https://test.pypi.org/simple/hataripy


Link
-----------------------------------------------
Hataripy site: [http://modflowpy.github.io/hataripydoc/](http://modflowpy.github.io/hataripydoc/)

Flopy code documentation is available at [http://modflowpy.github.io/flopypydoc/](http://modflowpy.github.io/flopypydoc/)


Getting Started
-----------------------------------------------
In order to do this code, please download the files from this link: https://www.hatarilabs.com/s/intruductiontoHataripy.rar, uncompress them under your “Documents” folder and create a new notebook of the “Scripts” folder. The script will locate the model files and generate the VTU files on the specified address. A description of the code can be seen on this video: https://youtu.be/y0o2pdjcLV0.

### Import packages define paths and load model


```python
import os, re, sys, hataripy
import numpy as np
```

    hataripy is installed in E:\Software\Anaconda3\lib\site-packages\hataripy



```python
modPath = '../Model/'
modName = 'Model1'
exeName = '../Exe/MODFLOW-NWT_64.exe'  
mfModel = hataripy.modflow.Modflow.load(modName+'.nam', model_ws=modPath,
                                exe_name=exeName)
```


```python
# get a list of the model packages
mfModel.get_package_list()
```




    ['DIS', 'NWT', 'BAS6', 'UPW', 'RCH', 'EVT', 'DRN', 'OC']



### Define objects that will be represented on the VTKs and add them to geometry object


```python
# read heads from the model output
headArray = hataripy.utils.binaryfile.HeadFile(modPath+modName+'.hds').get_data()
# get information about the drain cells
drnCells = mfModel.drn.stress_period_data[0]
```


```python
# add the arrays to the vtkObject
vtkObject = hataripy.export.vtk.Vtk3D(mfModel,'../vtuFiles/',verbose=True)
vtkObject.add_array('head',headArray)
vtkObject.add_array('drn',drnCells)
```

### Create the VTKs for model output, boundary conditions and water table


```python
vtkObject.modelMesh('modelMesh.vtu',smooth=True,cellvalues=['head'])
vtkObject.modelMesh('modelDrn.vtu',smooth=True,cellvalues=['drn'],boundary='drn',avoidpoint=True)
vtkObject.waterTable('waterTable.vtu',smooth=True)
```

    Removing existing vtk file: modelMesh.vtu
    Writing vtk file: modelMesh.vtu
    Number of point is 255920, Number of cells is 31990

    Removing existing vtk file: modelDrn.vtu
    Writing vtk file: modelDrn.vtu
    Number of point is 7432, Number of cells is 929

    Removing existing vtk file: waterTable.vtu
    Writing vtk file: waterTable.vtu
    Number of point is 25592, Number of cells is 6398

Processing of the VTKs in Paraview can be seen on this video:https://youtu.be/jy3qr4ht6bA
