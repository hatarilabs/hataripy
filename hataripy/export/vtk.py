import os
import numpy as np
from ..discretization import StructuredGrid


def start_tag(f, tag, indent_level, indent_char='  '):
    s = indent_level * indent_char + tag
    indent_level += 1
    f.write(s + '\n')
    return indent_level


def end_tag(f, tag, indent_level, indent_char='  '):
    indent_level -= 1
    s = indent_level * indent_char + tag
    f.write(s + '\n')
    return indent_level


class Vtk3D(object):

    def __init__(self, model, output_folder, verbose=None, nanval=-1e+20):
        if verbose is None:
            verbose = model.verbose
        self.verbose = verbose
        assert os.path.exists(output_folder), 'output folder doesnt exits: ' + output_filename
        self.output_folder = output_folder
        self.model = model
        self.modelgrid = model.modelgrid
        self.shape = (self.modelgrid.nlay, self.modelgrid.nrow,
                      self.modelgrid.ncol)
        self.nlay = self.modelgrid.nlay
        self.nrow = self.modelgrid.nrow
        self.ncol = self.modelgrid.ncol
        self.ncol = self.modelgrid.ncol
        self.nanval = nanval
        self.arrays = {}
        return

    def add_array(self, name, a):
        if type(a)==np.recarray:
            matrix = np.zeros(self.shape)
            for row in a:
                matrix[a.k,a.i,a.j]=1
            a = matrix
        assert a.shape == self.shape
        self.arrays[name] = a
        return

    def modelMesh(self, output_file='modelMesh.vtu', boundary=None, cellvalues=None, smooth=False, avoidpoint=False):
        self.file_preparation(output_file)
        self.output_file=output_file
        if boundary==None:
            actWCells = self.modelgrid.idomain
        else:
            actWCells = self.arrays[boundary]
        vtkSecuences = self.get_3d_vertex_connectivity(actWCells,defZ=False,smooth=smooth)

        f = open(self.filePath, 'w')
        cellType = 11
        self.write_vtu_file(f, vtkSecuences, cellType, actWCells, cellvalues, smooth, avoidpoint)

    def waterTable(self, output_file='waterTable.vtu', smooth=False, avoidpoint=True):
        self.file_preparation(output_file)
        self.output_file=output_file
        actWCells = self.modelgrid.idomain
        vtkSecuences = self.get_2d_vertex_connectivity(self.arrays['head'])

        f = open(self.filePath, 'w')
        cellType = 8
        self.write_vtu_file(f, vtkSecuences, cellType, actWCells, 'waterTable',smooth, avoidpoint)

    def file_preparation(self, output_file):
        assert output_file.lower().endswith(".vtu")
        filePath = os.path.join(self.output_folder,output_file)
        if os.path.exists(filePath):
            if self.verbose:
                print('Removing existing vtk file: ' + output_file)
            os.remove(filePath)
        self.filePath = filePath

    def write_vtu_file(self,f,vtkSecuences,cellType,actWCells,cellvalues,smooth,avoidpoint):
        verts, secus, zverts = vtkSecuences
        ncells = len(secus)
        npoints = verts.shape[0]

        if self.verbose:
            print('Writing vtk file: ' + self.output_file)
            print('Number of point is {}, Number of cells is {}\n'.format(npoints, ncells))

        indent_level = 0
        s = '<?xml version="1.0"?>'
        f.write(s + '\n')
        indent_level = start_tag(f, '<VTKFile type="UnstructuredGrid">',
                                 indent_level)

        # unstructured grid
        indent_level = start_tag(f, '<UnstructuredGrid>', indent_level)

        # piece
        s = '<Piece NumberOfPoints="{}" ' \
            'NumberOfCells="{}">'.format(npoints, ncells)
        indent_level = start_tag(f, s, indent_level)

        # points
        s = '<Points>'
        indent_level = start_tag(f, s, indent_level)

        s = '<DataArray type="Float64" NumberOfComponents="3">'
        indent_level = start_tag(f, s, indent_level)
        assert (isinstance(self.modelgrid, StructuredGrid))
        for row in verts:
            s = indent_level * '  ' + '{} {} {} \n'.format(*row)
            f.write(s)
        s = '</DataArray>'
        indent_level = end_tag(f, s, indent_level)

        s = '</Points>'
        indent_level = end_tag(f, s, indent_level)

        # cells
        s = '<Cells>'
        indent_level = start_tag(f, s, indent_level)

        s = '<DataArray type="Int32" Name="connectivity">'
        indent_level = start_tag(f, s, indent_level)
        for row in secus:
            s = indent_level * '  ' + ' '.join([str(i) for i in row]) + '\n'
            f.write(s)
        s = '</DataArray>'
        indent_level = end_tag(f, s, indent_level)

        s = '<DataArray type="Int32" Name="offsets">'
        indent_level = start_tag(f, s, indent_level)
        icount = 0
        for row in secus:
            icount += len(row)
            s = indent_level * '  ' + '{} \n'.format(icount)
            f.write(s)
        s = '</DataArray>'
        indent_level = end_tag(f, s, indent_level)

        s = '<DataArray type="UInt8" Name="types">'
        indent_level = start_tag(f, s, indent_level)
        for row in secus:
            s = indent_level * '  ' + '{} \n'.format(cellType)
            f.write(s)
        s = '</DataArray>'
        indent_level = end_tag(f, s, indent_level)

        s = '</Cells>'
        indent_level = end_tag(f, s, indent_level)

        # add cell data
        s = '<CellData Scalars="scalars">'
        indent_level = start_tag(f, s, indent_level)

        if cellvalues == 'waterTable':
            self.write_water_table(f, indent_level, arrayName='waterTable', actWCells=actWCells)
        elif cellvalues == None:
            for arrayName, arrayValues in self.arrays.items():
                self.write_data_array(f, indent_level, arrayName, arrayValues, actWCells)
        else:
            for name in cellvalues:
                self.write_data_array(f, indent_level, name, self.arrays[name], actWCells)
        s = '</CellData>'
        indent_level = end_tag(f, s, indent_level)

        if avoidpoint==False:
            # add point data
            s = '<PointData Scalars="scalars">'
            indent_level = start_tag(f, s, indent_level)
            if cellvalues == None:
                for arrayName, arrayValues in self.arrays.items():
                    self.write_point_value(f, indent_level, arrayName, actWCells, smooth)
            else:
                for name in cellvalues:
                    self.write_point_value(f, indent_level, name, actWCells, smooth)
            s = '</PointData>'
            indent_level = end_tag(f, s, indent_level)
        else: pass

        # end piece
        indent_level = end_tag(f, '</Piece>', indent_level)

        # end unstructured grid
        indent_level = end_tag(f, '</UnstructuredGrid>', indent_level)

        # end xml
        indent_level = end_tag(f, '</VTKFile>', indent_level)

        # end file
        f.close()
        return

    def write_data_array(self, f, indent_level, arrayName, arrayValues, actWCells):
        # header tag
        s = '<DataArray type="Float64" Name="{}" format="ascii">'.format(arrayName)
        indent_level = start_tag(f, s, indent_level)

        # data
        nlay = arrayValues.shape[0]

        for lay in range(nlay):
            s = indent_level * '  '
            f.write(s)
            idx = (actWCells[lay] != 0)
            arrayValuesLay = arrayValues[lay][idx].flatten()
            for layValues in arrayValuesLay:
                s = ' {}'.format(layValues)
                f.write(s)
            f.write('\n')

        # ending tag
        s = '</DataArray>'
        indent_level = end_tag(f, s, indent_level)
        return

    def write_water_table(self, f, indent_level, arrayName='waterTable', actWCells=None):
        # header tag
        s = '<DataArray type="Float64" Name="{}" format="ascii">'.format(arrayName)
        indent_level = start_tag(f, s, indent_level)
        s = indent_level * '  '
        f.write(s)
        idx = (actWCells[0] != 0)
        arrayValues = self.getUpperActiveLayer(self.arrays['head'])
        arrayValues = arrayValues[idx].flatten()
        for value in arrayValues:
            s = ' {}'.format(value)
            f.write(s)
            f.write('\n')
        s = '</DataArray>'
        indent_level = end_tag(f, s, indent_level)
        return

    def write_point_value(self, f, indent_level, arrayName, actWCells, smooth):
        # header tag
        s = '<DataArray type="Float64" Name="{}" format="ascii">'.format(arrayName)
        indent_level = start_tag(f, s, indent_level)

        # data
        verts, secus, zverts = self.get_3d_vertex_connectivity(actWCells,defZ=True,
                                    zvalues=self.arrays[arrayName],smooth=smooth)

        for z in zverts:
            s = indent_level * '  '
            f.write(s)
            s = ' {}'.format(z)
            f.write(s)
            f.write('\n')
        # ending tag
        s = '</DataArray>'
        indent_level = end_tag(f, s, indent_level)
        return

    def get_3d_vertex_connectivity(self, actWCells,defZ=False,zvalues=None,smooth=False):
        ncells = int(actWCells.sum())
        npoints = ncells * 8
        verts = np.empty((npoints, 3), dtype=np.float)
        iverts = []
        zverts = []
        ipoint = 0

        if defZ==False:
            zVertices = self.extendedDataArray(self.modelgrid.top_botm)
        else:
            zVertices = self.extendedDataArray(zvalues)

        for k in range(self.nlay):
            for i in range(self.nrow):
                for j in range(self.ncol):
                    if actWCells[k, i, j] == 0:
                        continue

                    ivert = []

                    pts = self.modelgrid._cell_vert_list(i, j)
                    pt0, pt1, pt2, pt3, pt0 = pts

                    if smooth == False:
                        cellBot = self.modelgrid.top_botm[k + 1, i, j]
                        cellTop = self.modelgrid.top_botm[k,i,j]
                        celElev = [cellBot, cellTop]
                        for elev in celElev:
                            verts[ipoint, :] = np.append(pt1,elev)
                            verts[ipoint+1, :] = np.append(pt2,elev)
                            verts[ipoint+2, :] = np.append(pt0,elev)
                            verts[ipoint+3, :] = np.append(pt3,elev)
                            ivert.extend([ipoint, ipoint+1, ipoint+2, ipoint+3])
                            zverts.extend([elev,elev,elev,elev])
                            ipoint += 4
                    else:
                        layers = [k+1,k]
                        for lay in layers:
                            verts[ipoint, :] = np.append(pt1,zVertices[lay,i+1,j])
                            verts[ipoint+1, :] = np.append(pt2,zVertices[lay,i+1,j+1])
                            verts[ipoint+2, :] = np.append(pt0,zVertices[lay,i,j])
                            verts[ipoint+3, :] = np.append(pt3,zVertices[lay,i,j+1])
                            ivert.extend([ipoint, ipoint+1, ipoint+2, ipoint+3])
                            zverts.extend([zVertices[lay,i+1,j],zVertices[lay,i+1,j+1],
                                        zVertices[lay,i,j],zVertices[lay,i,j+1]])
                            ipoint += 4
                    iverts.append(ivert)
        return verts, iverts, zverts

    def get_2d_vertex_connectivity(self, headArray):
        ibound = self.modelgrid.idomain
        npoints = ibound[0].sum() * 4
        verts = np.empty((npoints, 3), dtype=np.float)
        iverts = []
        zverts = []
        ipoint = 0

        wtCells=self.getUpperActiveLayer(headArray)
        vertexArray = self.extendedDataArray(headArray)
        wtVerts=self.getUpperActiveLayer(vertexArray)

        for i in range(self.nrow):
            for j in range(self.ncol):
                if ibound[:, i, j].sum() == 0 or wtCells[i,j] == self.nanval:
                    continue
                ivert = []
                pts = self.modelgrid._cell_vert_list(i, j)
                pt0, pt1, pt2, pt3, pt0 = pts

                verts[ipoint, :] = np.append(pt1,wtVerts[i+1,j])
                verts[ipoint+1, :] = np.append(pt2,wtVerts[i+1,j+1])
                verts[ipoint+2, :] = np.append(pt0,wtVerts[i,j])
                verts[ipoint+3, :] = np.append(pt3,wtVerts[i,j+1])
                ivert.extend([ipoint, ipoint+1, ipoint+2, ipoint+3])
                ipoint += 4
                iverts.append(ivert)
        return verts, iverts, zverts

    def getUpperActiveLayer(self, headArray):
        upperCells = np.zeros([headArray.shape[1],headArray.shape[2]])
        for row in range(headArray.shape[1]):
            for col in range(headArray.shape[2]):
                heads=headArray[:,row,col]
                if heads[heads>self.nanval].size > 0:
                    upperCells[row,col]=round(heads[heads>self.nanval][0],3)
                else:
                    upperCells[row,col]=self.nanval
        return upperCells

    def extendedDataArray(self, dataArray):
        if dataArray.shape[0] == self.nlay+1:
            dataArray = dataArray
        else:
            listArray = [dataArray[0]]
            for lay in range(dataArray.shape[0]):
                listArray.append(dataArray[lay])
            dataArray = np.stack(listArray)

        matrix = np.zeros([self.nlay+1,self.nrow+1,self.ncol+1])
        for lay in range(self.nlay+1):
            for row in range(self.nrow+1):
                for col in range(self.ncol+1):

                    indexList = [[row-1,col-1], [row-1,col],[row,col-1],[row,col]]
                    neighList = []
                    for index in indexList:
                        if index[0] in range(self.nrow) and index[1] in range(self.ncol):
                            neighList.append(dataArray[lay,index[0],index[1]])
                    neighList = np.array(neighList)
                    if neighList[neighList > self.nanval].shape[0] > 0:
                        headMean = neighList[neighList > self.nanval].mean()
                    else:
                        headMean = self.nanval
                    matrix[lay,row,col]=headMean
        return matrix
