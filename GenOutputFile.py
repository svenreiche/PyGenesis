import h5py
import re
class GenOutputFile:
    def __init__(self):
        self.hasFile = False
        self.filename = ''
        self.filepath = ''
        self.file = None

    def load(self, file):
        self.filepath = file
        self.filename = file.split('/')[-1]
        self.file = h5py.File(self.filepath, 'r')
        # basic dimension
        self.s =self.file['Global']['s'][()]
        self.z =self.file['Lattice']['zplot'][()]
        self.zlat =self.file['Lattice']['z'][()]

    def reload(self):
        if self.file is None:
            return
        self.file.close()
        self.load(self.filepath)

    def H5Iterator(self, name, node):
        if isinstance(node,h5py.Dataset):
            if not (self.re.search(name) is None):
                self.found.append(name)

    def findRecord(self,fld):
        if self.file is None:
                return
        self.re=re.compile(fld,re.IGNORECASE)
        self.found=[]
        self.file.visititems(self.H5Iterator)
        return self.found

    def getData(self,field):

        idx = field.find('/')
        tag = field[idx:]
        if 'Glob' in tag[0:5] or 'Meta' in tag[0:5]:   # global and meta data sets cannot be plotted
            return None
        if 'Lattice' in tag:   # first check for lattice data
            x = self.zlat
            if 'zplot' in tag:
                x = self.z
            y = self.file.get(tag)
            return {'x': x, 'y': y, 'plot': 'plot', 'line': 'steps'}
        elif 'Global' in tag:
            x = self.z
            y = self.file.get(tag)
            return {'x': x, 'y': y, 'plot': 'plot', 'line': 'default'}
        return None