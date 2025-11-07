import h5py
from pygenesis import data

def checkForFile(file=None):
    try:
        hid = h5py.File(file, 'r')
    except OSError as err:
        print('Error:', err)
        return None
    return hid

def open(file=None,verbose=True):
    hid = checkForFile(file)
    if hid is None:
        return None
    obj=data.data(verbose=verbose)
    obj.loadFile(file,hid)
    return obj

def openParticle(file=None):
    return None

def openField(file=None):
    return None