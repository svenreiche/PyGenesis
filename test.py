import numpy as np
import pygenesis as pyg

data = pyg.open(file='Test1.out.h5',verbose=True)
data2 = pyg.open(file='Test.out.h5',verbose=True)



#pyg.plot(data,'spectrum-nearfield',method='profile',position=0.95,xlim=(900,1100))
#

pyg.plot([data,data2],'power','mean')
#pyg.plot(data,'spectrum-farfield','rms')
#pyg.plot(data,'spectrum-farfield','profile',0.6)
#pyg.plot(data,'wigner-nearfield',position=0.95,cmap='seismic',vscl=0.1,ylim=(900,1100))
#pyg.plot(data,'power','integrated',scale='mu')

#pyg.plot(data,'spectrum-farfield','slice',position=0.95)
#pyg.plotLattice(data,'aw')
#data.info('Lattice')
#pyg.plotLattice(data,'chic')

#pyg.plot(data,'SCfield',method = 'profile',position=0.8)


#Nt=1000
#s=np.linspace(-10,10,num=Nt)
#sig = np.exp(-(s-2)**2/4)*np.exp(1j*s)
#data.Wigner(sig)

