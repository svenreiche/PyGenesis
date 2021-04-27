import sys
from PyQt5 import QtWidgets,QtGui,QtCore
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap, QDesktopServices
from PyQt5.uic import loadUiType

Ui_PyGenesisGUI, QMainWindow = loadUiType('PyGenesis.ui')


class PyGenesis(QMainWindow, Ui_PyGenesisGUI):
    def __init__(self):
        super(PyGenesis, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Genesis Postprocessor in Python")



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = PyGenesis()
    main.show()
    sys.exit(app.exec_())
