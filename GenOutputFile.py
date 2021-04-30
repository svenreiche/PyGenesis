import h5py
import re
import numpy as np

class GenOutputFile:
    def __init__(self):
        self.hasFile = False
        self.filename = ''
        self.filepath = ''
        self.file = None
        self.is2D = False
        self.s = None
        self.z = None
        self.zlat = None
        self.spec = {}

    def load(self, file):
        self.filepath = file
        self.filename = file.split('/')[-1]
        self.file = h5py.File(self.filepath, 'r')
        # basic dimension
        self.s = self.file['Global']['s'][()]*1e15/3e8
        self.z = self.file['Lattice']['zplot'][()]
        self.zlat = self.file['Lattice']['z'][()]
        self.freq = self.file['Global']['frequency'][()]

        if len(self.s) > 1:
            self.is2D=True
        else:
            self.is2D=False

    def reload(self):
        if self.file is None:
            return
        self.file.close()
        self.load(self.filepath)

    def generateSpectrum(self):
        found = self.findRecord('spectrum')
        self.spec.clear()
        if found is None:
            return
        for rec in found:
            print('Calculating Spectrum for', rec)
            tag1 = rec.replace('spectrum','intensity')
            tag2 = rec.replace('spectrum','phase')
            sig = np.sqrt(np.array(self.file.get(tag1)))*np.exp(1j*np.array(self.file.get(tag2)))
            self.spec['/'+rec] = np.abs(np.fft.fftshift(np.fft.fft(sig, axis=1), axes=1))**2


    def H5Iterator(self, name, node):
        if isinstance(node,h5py.Dataset):
            if not (self.re.search(name) is None):
                self.found.append(name)
            elif 'intensity' in name and not 'Global' in name:
                name2=name.replace('intensity','spectrum')
                if not (self.re.search(name2) is None):
                    self.found.append(name2)

    def findRecord(self, fld):
        if self.file is None:
                return
        self.re = re.compile(fld,re.IGNORECASE)
        self.found = []
        self.file.visititems(self.H5Iterator)
        return self.found

    def getData(self, field, mode='profile-norm', rel=0):

        idx = field.find('/')
        tag = field[idx:]

        if 'spectrum' in tag and len(self.spec) == 0:
            self.generateSpectrum()

        if 'Glob' in tag[0:5] or 'Meta' in tag[0:5]:   # global and meta data sets cannot be plotted
            return None
        if 'Lattice' in tag:   # first check for lattice data
            x = self.zlat
            if 'zplot' in tag:
                x = self.z
            y = self.file.get(tag)
            return {'x': x, 'y': y, 'xlabel':'z (m)', 'plot': 'plot', 'line': 'steps'}
        if 'spectrum' in tag:
            ele = self.spec[tag]
        else:
            ele = self.file.get(tag)
        dims = ele.shape


        if dims[0] == 1:   # only s-dependence
            if len(dims) == 1 or dims[1] == 1:
                return None
            x = self.s
            y = np.transpose(ele)
            return {'x': x, 'y': y, 'xlabel': 't (fs)', 'plot': 'plot', 'line': 'default'}
        if len(dims) == 1 or dims[0] == 1:
            x = self.z
            y = ele
            return {'x': x, 'y': y, 'xlabel': 'z (m)', 'plot': 'plot', 'line': 'default'}


        if '2d' in mode:
            x = self.z
            y = self.s
            xlabel = 't (fs)'
            z = np.array(ele)
            if 'spectrum' in tag:
                y = self.freq
                xlabel = 'E_ph (eV)'
            if 'norm' in mode.lower():
                zmean =np.mean(z, axis=1)
                for i in range(len(zmean)):
                    if zmean[i] == 0:
                        zmean[i]=1.
                    z[i,:]*=1./zmean[i]
            return {'x': x, 'y': y, 'z': z, 'xlabel': xlabel, 'plot': 'image'}

        if 'line' in mode:
            x = self.z
            ids = np.argmin(np.abs(self.s - 0.01 * np.max(self.s) * rel))
            y = np.transpose(np.array(ele[:,ids]))
            xlabel = 'z (m)'
            return {'x': x, 'y': y, 'xlabel': xlabel, 'plot': 'plot', 'line': 'default'}

        if 'profile' in mode:
            x = self.s
            idz = np.argmin(np.abs(self.z-0.01*np.max(self.z)*rel))
            y = np.transpose(np.array(ele[idz,:]))
            xlabel = 't (fs)'
            if 'spectrum' in tag:
                x = self.freq
                xlabel = 'E_ph (eV)'
            if 'norm' in mode:
                nor = np.max(y)
                if nor == 0:
                    nor = 1
                y = y/nor
            return {'x': x, 'y': y, 'xlabel': xlabel, 'plot': 'plot', 'line': 'default'}

        if 'max' in mode or 'min' in mode or 'mean' in mode:
            x = self.z
            if 'max' in mode:
                y = np.amax(ele,axis = 1)
            elif 'min' in mode:
                y = np.amin(ele,axis = 1)
            else:
                y = np.mean(ele,axis = 1)
            xlabel = 'z (m)'
            return {'x': x, 'y': y, 'xlabel': xlabel, 'plot': 'plot', 'line': 'default'}

    def getWigner(self,field,spos):
        x = self.s
        idz = np.argmin(np.abs(self.z - 0.01 * np.max(self.z) * rel))
        return None

    def getCoherence(self, field, rel, degree):
        idx = field.find('/')
        tag = field[idx:]
        xlabel = 't (fs)'
        idz = np.argmin(np.abs(self.z - 0.01 * np.max(self.z) * rel))
        ele = self.file.get(tag)
        elesup = self.file.get(tag.replace('intensity','phase'))
        if degree == 1:
            sig = np.sqrt(ele[idz,:])*np.exp(1j*elesup[idz,:])
            sigc = np.conj(sig)
        elif degree == 2:
            sig = ele[idz,:]
            sigc= ele[idz,:]
        else:
            return None

        n = 1000
        y = np.zeros(n)
        x = self.s[0:n]
        nfull = len(sig)
        for i in range(n):
            y[i] = np.real(np.mean(sig[0:nfull-i]*sigc[i:nfull]))
        norm = y[0]
        if degree == 2:
            norm = np.mean(sig)**2
        if norm == 0:
            norm = 1
        y /= norm
        return {'x': x, 'y': y, 'xlabel': xlabel, 'plot': 'plot', 'line': 'default'}

    def getConvolution(self, field, rel):
        idx = field.find('/')
        tag = field[idx:]
        x = self.s
        xlabel = 't (fs)'
        idz = np.argmin(np.abs(self.z - 0.01 * np.max(self.z) * rel))
        ele = self.file.get(tag)
        sig = ele[idz, :]
        y = np.convolve(sig,sig,mode='same')[len(x)-1:]
        return {'x': x, 'y': y, 'xlabel': xlabel, 'plot': 'plot', 'line': 'default'}
