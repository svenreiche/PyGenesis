import sys
import h5py
from PyQt5 import QtWidgets,QtGui,QtCore
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap, QDesktopServices
from PyQt5.uic import loadUiType

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)


# PyGenesis specific imports
Ui_PyGenesisGUI, QMainWindow = loadUiType('PyGenesis.ui')

import GenOutputFile

class PyGenesis(QMainWindow, Ui_PyGenesisGUI):
    def __init__(self):
        super(PyGenesis, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Genesis Postprocessor in Python")
        self.initmpl()

        self.files = {}
        self.updateDataBrowser()

# connect events to handling functions
        self.actionLoad.triggered.connect(self.load)
        self.PlotCommand.editingFinished.connect(self.getDatasets)
        self.UIReplot.clicked.connect(self.plotDatasetList)
        
# main routine for plotting
    def getDatasets(self):
        cmd=str(self.PlotCommand.text())
        datasets={}
        for key in self.files.keys():
            found = self.files[key].findRecord(cmd)
            if len(found):
                datasets[key] = found
        if datasets:
            self.updateDatasetList(datasets)
            self.plotDatasetList()

    def updateDatasetList(self, dset):
        self.DatasetList.clear()
        self.DatasetList.setColumnCount(1)
        self.DatasetList.setRowCount(0)
        icount = 0
        for key in dset:
            name = key.split('/')[-1]+'/'
            for fld in dset[key]:
                self.DatasetList.setRowCount(icount+1)
                ele = QtWidgets.QTableWidgetItem(name+fld)
                ele.setCheckState(QtCore.Qt.Checked)
                ele.setData(QtCore.Qt.UserRole, key)
                self.DatasetList.setItem(icount, 0, ele)
                icount += 1
        self.DatasetList.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem('Field'))
        self.DatasetList.resizeColumnsToContents()
        self.DatasetList.verticalHeader().hide()

    def plotDatasetList(self):
        self.axes.clear()
        ncol = self.DatasetList.rowCount()
        for i in range(ncol):
            ele = self.DatasetList.item(i, 0)
            if ele.checkState() == QtCore.Qt.Checked:
                file = ele.data(QtCore.Qt.UserRole)
                field = str(ele.text())
                self.doPlot(file,field)
        self.canvas.draw()

    def doPlot(self,file,field):
        data = self.files[file].getData(field)
        if data is None:
            return
        if 'plot' in data['plot']:
            self.axes.plot(data['x'], data['y'],ds=data['line'])


    def load(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Genesis Output File",
                                                            "", "HDF5 Files (*.h5)", options=options)
        if not fileName:
            return
        self.files[fileName] = GenOutputFile.GenOutputFile()
        self.files[fileName].load(fileName)

        self.updateDataBrowser()
#-----------------
# gui action

# update databrowser
    def updateDataBrowser(self):
        self.DataBrowser.clear()
        self.DataBrowser.setHeaderItem(QtWidgets.QTreeWidgetItem(['Files and Datasets', 'Record Size']))
        for file in self.files.keys():
            root = QtWidgets.QTreeWidgetItem(self.DataBrowser, [self.files[file].filename, ''])
            for key in self.files[file].file.keys():
                if isinstance(self.files[file].file[key], h5py.Dataset):
                    QtWidgets.QTreeWidgetItem(root, [key, str(self.files[file].file[key].shape)])
                else:
                    lvl1 = QtWidgets.QTreeWidgetItem(root, [key, ''])
                    for key1 in self.files[file].file[key].keys():
                        if isinstance(self.files[file].file[key][key1], h5py.Dataset):
                            QtWidgets.QTreeWidgetItem(lvl1, [key1, str(self.files[file].file[key][key1].shape)])
                        else:
                            lvl2 = QtWidgets.QTreeWidgetItem(lvl1, [key1, ''])
                            for key2 in self.files[file].file[key][key1].keys():
                                if isinstance(self.files[file].file[key][key1][key2], h5py.Dataset):
                                    QtWidgets.QTreeWidgetItem(lvl2, [key2, str(self.files[file].file[key][key1][key2].shape)])
                                else:
                                    QtWidgets.QTreeWidgetItem(lvl2,  [key2, ''])




# initializing the plot window
    def initmpl(self):
        self.fig=Figure()
        self.axes=self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar=NavigationToolbar(self.canvas,self.mplwindow, coordinates=True)
        self.mplvl.addWidget(self.toolbar)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = PyGenesis()
    main.show()
    sys.exit(app.exec_())
