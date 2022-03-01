import sys
import h5py
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog, QMainWindow
from PyQt5.QtGui import QPixmap, QDesktopServices
from PyQt5.uic import loadUiType

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

# PyGenesis specific imports
import GenOutputFile
# Import Gui
from PyGenesisGUI import Ui_PyGenesisGUI


class PyGenesis(QMainWindow, Ui_PyGenesisGUI):
    def __init__(self):
        super(PyGenesis, self).__init__()
        self.setupUi(self)

        # Initialize containers
        self.hasRAxis = False
        self.xlabel = None
        self.ylabel = []
        self.ylabelR = []
        self.plotType = None
        self.title = None
        self.fig = None
        self.axes = None
        self.axesr = None
        self.canvas = None
        self.toolbar = None
        self.initmpl()

        self.files = {}
        self.updateDataBrowser()

        self.colors = ['Blue', 'Red', 'Green', 'Orange', 'Purple', 'Brown', 'Pink', 'Olive', 'Grey', 'Cyan']
        self.lines = ['solid', 'dashed', 'dotted']
        self.markers = ['None', 'Circle', 'Square', 'Triangle']
        self.modes = ['Profile', 'Profile (norm)', 'Mean', 'Max', 'Min', 'Weighted', '2D', '2D (norm)', 'Line']
        self.colormap = 'viridis'

        # formating the datalist
        self.DatasetList.clear()
        self.DatasetList.setColumnCount(8)
        self.DatasetList.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem('Field'))
        self.DatasetList.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem('Mode'))
        self.DatasetList.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem('Right Axis'))
        self.DatasetList.setHorizontalHeaderItem(3, QtWidgets.QTableWidgetItem('Log'))
        self.DatasetList.setHorizontalHeaderItem(4, QtWidgets.QTableWidgetItem('Color'))
        self.DatasetList.setHorizontalHeaderItem(5, QtWidgets.QTableWidgetItem('Rel. Pos.'))
        self.DatasetList.setHorizontalHeaderItem(6, QtWidgets.QTableWidgetItem('Legend'))
        self.DatasetList.setHorizontalHeaderItem(7, QtWidgets.QTableWidgetItem('Scale'))
        self.DatasetList.verticalHeader().hide()

        # connect events to handling functions
        self.actionLoad.triggered.connect(self.load)
        self.actionClose.triggered.connect(self.close)
        self.actionReload.triggered.connect(self.reload)
        self.actionDelete.triggered.connect(self.deleteDataset)
        self.actionDuplicate.triggered.connect(self.duplicateDataset)
        self.actionCor1.triggered.connect(self.coherence)
        self.actionCor2.triggered.connect(self.coherence)
        self.actionAutocorrelation.triggered.connect(self.convolution)
        self.actionWigner.triggered.connect(self.Wigner)
        self.PlotCommand.returnPressed.connect(self.getDatasets)
        self.UIReplot.clicked.connect(self.plotDatasetList)
        self.UIPos.valueChanged.connect(self.plotDatasetList)
        self.DatasetList.itemChanged.connect(self.plotDatasetList)
        self.DataBrowser.itemDoubleClicked.connect(self.addDataset)
        self.UIXmax.editingFinished.connect(self.plotDatasetList)
        self.UIXmin.editingFinished.connect(self.plotDatasetList)
        self.UIYmax.editingFinished.connect(self.plotDatasetList)
        self.UIYmin.editingFinished.connect(self.plotDatasetList)
        self.UILegend.toggled.connect(self.plotDatasetList)
        self.actionviridis.triggered.connect(self.changeColormap)
        self.actionInferno.triggered.connect(self.changeColormap)
        self.actionSeismic.triggered.connect(self.changeColormap)
        self.actionOcean.triggered.connect(self.changeColormap)
        self.actionTerrain.triggered.connect(self.changeColormap)
        self.actionJet.triggered.connect(self.changeColormap)

    def changeColormap(self):
        self.colormap = self.sender().objectName()[6:].lower()
        self.plotDatasetList()

# main routine for plotting
    def getDatasets(self):
        cmd = str(self.PlotCommand.text())
        if len(cmd) < 1:
            return
        datasets = {}
        for key in self.files.keys():
            found = self.files[key].findRecord(cmd)
            if len(found):
                datasets[key] = found
        if datasets:
            self.DatasetList.blockSignals(True)
            self.DatasetList.setRowCount(0)
            for key in datasets.keys():
                name = key.split('/')[-1] + '/'
                for fld in datasets[key]:
                    self.addDatasetListEntry(key, name+fld)
            self.DatasetList.blockSignals(False)
            self.plotDatasetList()

    def addDatasetListEntry(self, file, field, option=None):
        if option is None:
            option = self.modes

        icount = self.DatasetList.rowCount()
        self.DatasetList.setRowCount(icount+1)
        ele = QtWidgets.QTableWidgetItem(field)
        ele.setCheckState(QtCore.Qt.Checked)
        ele.setData(QtCore.Qt.UserRole, file)
        self.DatasetList.setItem(icount, 0, ele)
        CBMode = QtWidgets.QComboBox()
        for mode in option:
            CBMode.addItem(mode)
        if self.files[file].is2D:
            CBMode.setCurrentIndex(0)
        else:
            CBMode.setCurrentIndex(len(option)-1)

        self.DatasetList.setCellWidget(icount, 1, CBMode)
        CBMode.currentIndexChanged.connect(self.plotDatasetList)
        for i in range(2):
            ele = QtWidgets.QTableWidgetItem('')
            ele.setCheckState(QtCore.Qt.Unchecked)
            self.DatasetList.setItem(icount, i+2, ele)
        CBcol = QtWidgets.QComboBox()
        for col in self.colors:
            CBcol.addItem(col)
        CBcol.setCurrentIndex(icount % len(self.colors))
        self.DatasetList.setCellWidget(icount, 4, CBcol)
        CBcol.currentIndexChanged.connect(self.plotDatasetList)
        ele = QtWidgets.QTableWidgetItem('')
        self.DatasetList.setItem(icount, 5, ele)
        ele = QtWidgets.QTableWidgetItem('')
        self.DatasetList.setItem(icount, 6, ele)
        ele = QtWidgets.QTableWidgetItem('1.0')
        self.DatasetList.setItem(icount, 7, ele)
        self.DatasetList.resizeColumnsToContents()

    def plotDatasetList(self):
        self.DatasetList.blockSignals(True)
        self.axes.clear()
        self.axesr.clear()
        self.hasRAxis = False
        self.xlabel = None
        self.ylabel = []
        self.ylabelR = []
        self.plotType = None
        self.title = None
        font = QtGui.QFont()
        ncol = self.DatasetList.rowCount()
        for i in range(ncol):
            ele = self.DatasetList.item(i, 0)
            if ele.checkState() == QtCore.Qt.Checked:
                file = ele.data(QtCore.Qt.UserRole)
                field = str(ele.text())
                rAxis = (self.DatasetList.item(i, 2).checkState() == QtCore.Qt.Checked)
                log = (self.DatasetList.item(i, 3).checkState() == QtCore.Qt.Checked)
                color = 'tab:'+str(self.DatasetList.cellWidget(i, 4).currentText()).lower()
                mode = str(self.DatasetList.cellWidget(i, 1).currentText()).lower()
                zpos = str(self.DatasetList.item(i, 5).text())
                leg = str(self.DatasetList.item(i, 6).text())
                scl = str(self.DatasetList.item(i, 7).text())
                try:                    
                    scale = float(scl) 
                except:
                    scale = 1.0
                try:
                    spos = float(zpos)
                except:
                    spos = self.UIPos.value()
                res = self.doPlot(file, field, mode, rAxis, log, color, spos, leg, scale)
                if res:
                    font.setItalic(False)
                    ele.setFont(font)
                else:
                    font.setItalic(True)
                    ele.setFont(font)

        self.axes.set_xlabel(self.xlabel)
        ylab = r''
        print(self.ylabel)
        for ele in self.ylabel:
            if len(ele) < 1:
                continue
            if len(ylab) > 0:
                ylab += r', '
            ylab += ele
        self.axes.set_ylabel(ylab)
        self.axes.set_title(self.title)

        if not self.hasRAxis:
            self.axesr.get_yaxis().set_visible(False)
        else:
            self.axesr.get_yaxis().set_visible(True)

        # get the limits in the plots
        try:
            xmin = float(str(self.UIXmin.text()))
        except:
            xmin = self.axes.get_xlim()[0]
        try:
            xmax = float(str(self.UIXmax.text()))
        except:
            xmax = self.axes.get_xlim()[1]
        self.axes.set_xlim([xmin, xmax])
        try:
            ymin = float(str(self.UIYmin.text()))
        except:
            ymin = self.axes.get_ylim()[0]
        try:
            ymax = float(str(self.UIYmax.text()))
        except:
            ymax = self.axes.get_ylim()[1]
        self.axes.set_ylim([ymin, ymax])

        if self.UILegend.isChecked():
            self.axes.legend()

        self.canvas.draw()

        self.DatasetList.blockSignals(False)

    ##############################
    # plot of individual dataset

    def doPlot(self, file, field, mode, rAxis, log, color, pos, leg, scale):
        if 'Correlation' in field:
            data = self.files[file].getCoherence(field[:-1], pos, int(field[11:12]))
        elif 'Convolution' in field:
            data = self.files[file].getConvolution(field[:-1], pos)
        elif 'Wigner' in field:
            data = self.files[file].getWigner(field, pos)
        else:
            data = self.files[file].getData(field, mode = mode, rel = pos, legend = leg)
        if data is None:
            return False
        
        if rAxis:
            self.ylabelR.append(data['ylabel'])
        else:
            self.ylabel.append(data['ylabel'])

        if self.xlabel is None:
            self.xlabel = data['xlabel']
        else:
            if not (self.xlabel == data['xlabel']):
                return False
        
        if self.title is None:
            self.title = data['title']

        if 'plot' in data['plot']:
            ax = self.axes
            if rAxis:
                ax = self.axesr
                self.hasRAxis = True

            ax.plot(data['x'], data['y']*scale, ds=data['line'], color=color, label=data['label'])
            if log:
                ax.set_yscale('log')
        elif 'image' in data['plot']:
            bbox = [np.min(data['y']), np.max(data['y']), np.min(data['x']), np.max(data['x'])]
            im = self.axes.imshow(np.flipud(data['z']), aspect='auto', interpolation='none', cmap=self.colormap, extent=bbox)
        return True
    ####################33
    # menu item action or other events

    def reload(self):
        for key in self.files.keys():
            self.files[key].reload()
        self.updateDataBrowser()

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

    def close(self):
        cur = self.DataBrowser.currentItem()
        if cur is None:
            return  # nothing selected
        while self.DataBrowser.indexOfTopLevelItem(cur) < 0:
            cur = cur.parent()
        file = cur.data(0, QtCore.Qt.UserRole)
        del self.files[file]
        self.updateDataBrowser()

    def addDataset(self, QTWItem):
        if len(str(QTWItem.text(1))) < 2:
            return
        Field = str(QTWItem.text(0))
        cur = QTWItem
        while self.DataBrowser.indexOfTopLevelItem(cur) < 0:
            cur = cur.parent()
            Field = str(cur.text(0)) + '/' + Field
        file = cur.data(0, QtCore.Qt.UserRole)
        self.DatasetList.blockSignals(True)
        self.addDatasetListEntry(file, Field)
        self.DatasetList.blockSignals(False)
        self.plotDatasetList()

    def duplicateDataset(self):
        row = self.DatasetList.currentRow()
        ele = self.DatasetList.item(row, 0)
        file = ele.data(QtCore.Qt.UserRole)
        field = str(ele.text())
        self.DatasetList.blockSignals(True)
        self.addDatasetListEntry(file,field)
        self.DatasetList.blockSignals(False)

    def deleteDataset(self):
        row = self.DatasetList.currentRow()
        if row < 0:
            return
        self.DatasetList.blockSignals(True)
        self.DatasetList.removeRow(row)
        self.DatasetList.blockSignals(False)

    def coherence(self):
        cmd = 'Field([/]|[2-9][/])intensity'
        order = '1'
        sname = self.sender().objectName()
        if 'Cor2' in sname:
            order = '2'
        for key in self.files.keys():
            found = self.files[key].findRecord(cmd)
            if len(found):
                name = key.split('/')[-1] + '/'
                for fld in found:
                    self.DatasetList.blockSignals(True)
                    self.addDatasetListEntry(key, 'Correlation' + order + '(' + name + fld + ')')
                    self.DatasetList.blockSignals(False)

    def convolution(self):
        cmd = 'Field.*/power'
        for key in self.files.keys():
            found = self.files[key].findRecord(cmd)
            if len(found):
                name = key.split('/')[-1] + '/'
                for fld in found:
                    self.DatasetList.blockSignals(True)
                    self.addDatasetListEntry(key, 'Convolution(' + name + fld + ')')
                    self.DatasetList.blockSignals(False)

    def Wigner(self):
        cmd = 'Field([/]|[2-9][/])intensity'
        for key in self.files.keys():
            found = self.files[key].findRecord(cmd)
            if len(found):
                name = key.split('/')[-1] + '/'
                for fld in found:
                    self.DatasetList.blockSignals(True)
                    self.addDatasetListEntry(key, 'Wigner(' + name + fld + ')', ['2D'])
                    self.DatasetList.blockSignals(False)

    # -----------------
# gui action

# update databrowser
    def updateDataBrowser(self):
        self.DataBrowser.clear()
        self.DataBrowser.setHeaderItem(QtWidgets.QTreeWidgetItem(['Files and Datasets', 'Record Size']))
        for file in self.files.keys():
            root = QtWidgets.QTreeWidgetItem(self.DataBrowser, [self.files[file].filename, ''])
            root.setData(0, QtCore.Qt.UserRole, file)
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
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        self.axesr = self.axes.twinx()
        self.canvas = FigureCanvas(self.fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas, self.mplwindow, coordinates=True)
        self.mplvl.addWidget(self.toolbar)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = PyGenesis()
    main.show()
    sys.exit(app.exec_())
