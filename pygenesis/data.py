import h5py
import numpy as np
import re

class data:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.hid=None
        self.found=[]
        self.exclude=['Lattice','Meta','Global']

    def loadFile(self,file=None,hid=None):
        if hid is None:
            self.hid=None
            return
        self.hid=hid
        self.file=file
        if self.verbose:
            print('Parsing input file:',file)
            self.parseMeta()
        self.s = self.hid['Global']['s'][()]*1e15/3e8
        self.z = self.hid['Lattice']['zplot'][()]
        self.freq = self.hid['Global']['frequency'][()]
        self.gamma0 = self.hid['Global']['gamma0'][()][0]
        self.lambda0 = self.hid['Global']['lambdaref'][()][0]
        self.sample = self.hid['Global']['sample'][()][0]
        self.slen = self.hid['Global']['slen'][()][0]
        self.time =self.hid['Global']['time'][()][0] > 0
        self.scan=self.hid['Global']['scan'][()][0] > 0
        self.one4one=self.hid['Global']['one4one'][()][0] > 0

        if self.verbose:
            print('Global Data:')
            print('  ','Time-dependent :',self.time)
            print('  ','Scan :',self.scan)
            print('  ','one4one:',self.one4one)
            print('  ','lambda0:',self.lambda0)
            print('  ','sample:',self.sample)
            print('  ','slen:',self.slen)
            print('  ','gamma0:',self.gamma0)


    def parseMeta(self):
        print('Meta Data:')
        ver = self.hid['Meta']['Version']
        print('   Genesis - Version %d.%d.%d' % (int(ver['Major'][()][0]),int(ver['Minor'][()][0]),int(ver['Revision'][()][0])))
        print('   (%s)' % ver['Build_Info'][()][0].decode())
        for key in self.hid['Meta'].keys():
            if isinstance(self.hid['Meta'][key],h5py.Dataset):
                ele = self.hid['Meta'][key][()][0]
                if hasattr(ele,'decode'):
                    if len(ele) < 50:
                        print('  ',key,':',ele.decode().strip())
                else:
                    print('  ',key,':',ele)

    def getRecord(self,fld):
        found = self.findRecord(fld)
        return {fld:self.hid[fld][()] for fld in found}

    def findRecord(self, fld):
        if self.hid is None:
                return []
        self.re = re.compile(fld,re.IGNORECASE)
        self.found.clear()
        self.hid.visititems(self.H5Iterator)
        return self.found

    def excludeRecord(self,exclude=[]):
        self.exclude = exclude

    def H5Iterator(self, name, node):
        if isinstance(node,h5py.Dataset):
            if not (self.re.search(name) is None):
                doexc=False
                for exc in self.exclude:
                    if exc in name:
                        doexc=True
                if not(doexc):
                    self.found.append(name)


    ######
    # getting various data

    def getData(self,fld,method='raw',position=0.0):
        """
        Primary methods to retrieve dataset with some possible processing
        :param fld: regular expression to find a dataset
        :param method: tag for various methods
        :param position: relative value of row or column in 2D array
        :return: dictionary with dataset name, processed data, methods and filename
        """
        if self.hid is None:
            return None
        # get all found dataset
        data = self.getRecord(fld)

        x= self.z
        xlab = r'$z$ (m)'
        y = self.s
        ylab = r'$t$ (fs)'

        for key in data.keys():
            if method == 'mean':
                data[key]=np.mean(data[key],axis=1)
            elif method == 'max':
                data[key]=np.max(data[key],axis=1)
            elif method == 'slice':
                nz=int(np.round(data[key].shape[0]*position))
                if nz >=data[key].shape[0]:
                    nz = data[key].shape[0]-1
                if nz <0:
                    nz = 0
                data[key]=np.transpose(data[key][nz,:])
                x=self.s
                y=self.z
            elif method == 'trace':
                nz = int(np.round(data[key].shape[1] * position))
                if nz >=data[key].shape[1]:
                    nz = data[key].shape[1]-1
                if nz <0:
                    nz = 0
                data[key] = np.transpose(data[key][:,nz])
            elif method == 'norm':
                for iz in range(data[key].shape[0]):
                    norm = np.mean(data[key][iz,:])
                    if norm == 0:
                        norm = 1
                    data[key][iz,:] = data[key][iz,:]/norm
            elif not method =='raw' :
                print('Method %s not implemented' % method)
                return None

            res = {'data':data,'x':x,'y':y,'xlabel':xlab,'ylabel':ylab,'method':method,'file':self.file}

            return res

