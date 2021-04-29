import sys
import h5py
import numpy as np
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

        self.colors = ['Blue', 'Red', 'Green', 'Orange', 'Purple', 'Brown', 'Pink', 'Olive', 'Grey', 'Cyan']
        self.lines = ['solid', 'dashed', 'dotted']
        self.markers = ['None', 'Circle', 'Square', 'Triangle']
        self.modes = ['Line', 'Profile', 'Profile (norm)', 'Mean', 'Max', 'Min', 'Weighted', '2D', '2D (norm)']


# connect events to handling functions
        self.actionLoad.triggered.connect(self.load)
        self.PlotCommand.editingFinished.connect(self.getDatasets)
        self.UIReplot.clicked.connect(self.plotDatasetList)
        self.UIPos.valueChanged.connect(self.plotDatasetList)
        self.DatasetList.itemChanged.connect(self.plotDatasetList)

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
        self.DatasetList.blockSignals(True)
        self.DatasetList.clear()
        self.DatasetList.setColumnCount(5)
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
                CBMode = QtWidgets.QComboBox()
                for mode in self.modes:
                    CBMode.addItem(mode)
                CBMode.setCurrentIndex(0)
                self.DatasetList.setCellWidget(icount, 1, CBMode)

                for i in range(2):
                    ele = QtWidgets.QTableWidgetItem('')
                    ele.setCheckState(QtCore.Qt.Unchecked)
                    self.DatasetList.setItem(icount, i+2, ele)
                CBcol = QtWidgets.QComboBox()
                for col in self.colors:
                    CBcol.addItem(col)
                CBcol.setCurrentIndex(icount % len(self.colors))
                self.DatasetList.setCellWidget(icount,4,CBcol)
                icount += 1
        self.DatasetList.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem('Field'))
        self.DatasetList.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem('Mode'))
        self.DatasetList.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem('Right Axis'))
        self.DatasetList.setHorizontalHeaderItem(3, QtWidgets.QTableWidgetItem('Log'))
        self.DatasetList.setHorizontalHeaderItem(4, QtWidgets.QTableWidgetItem('Color'))

        self.DatasetList.resizeColumnsToContents()
        self.DatasetList.verticalHeader().hide()
        self.DatasetList.blockSignals(False)

    def plotDatasetList(self):
        self.axes.clear()
        self.axesr.clear()
        self.pos = self.UIPos.value()
        self.hasRAxis = False
        self.xlabel = None
        self.ylabel = []
        self.ylabelR = []
        self.plotType = None

        ncol = self.DatasetList.rowCount()
        for i in range(ncol):
            ele = self.DatasetList.item(i, 0)
            if ele.checkState() == QtCore.Qt.Checked:
                file = ele.data(QtCore.Qt.UserRole)
                field = str(ele.text())
                rAxis = (self.DatasetList.item(i, 2).checkState() == QtCore.Qt.Checked)
                log = (self.DatasetList.item(i, 3).checkState() == QtCore.Qt.Checked)
                color='tab:'+str(self.DatasetList.cellWidget(i, 4).currentText()).lower()
                mode = str(self.DatasetList.cellWidget(i, 1).currentText()).lower()
                self.doPlot(file,field,mode,rAxis,log,color)
        self.axes.set_xlabel(self.xlabel)
        if not self.hasRAxis:
            self.axesr.get_yaxis().set_visible(False)
        else:
            self.axesr.get_yaxis().set_visible(True)
        self.canvas.draw()

    ##############################
    # plot of individual dataset

    def doPlot(self, file, field, mode, rAxis, log, color):
        data = self.files[file].getData(field, mode=mode, rel=self.pos)
        if data is None:
            return

        if self.xlabel is None:
            self.xlabel=data['xlabel']

        if 'plot' in data['plot']:
            ax=self.axes
            if rAxis:
                ax=self.axesr
                self.hasRAxis=True
            ax.plot(data['x'], data['y'],ds=data['line'],color=color)
            if log:
                ax.set_yscale('log')
        elif 'image' in data['plot']:
            bbox = [np.min(data['y']), np.max(data['y']), np.min(data['x']), np.max(data['x'])]
            im = self.axes.imshow(np.flipud(data['z']), aspect='auto', interpolation='none', cmap='viridis', extent=bbox)


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
        self.axesr=self.axes.twinx()
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
