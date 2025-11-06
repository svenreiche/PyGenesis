
import pygenesis as pyg

data = pyg.open(file='Test.out.h5',verbose=True)

#pyg.plot(data,'power',method='raw')
#pyg.plot(data,'power',method='norm',xlim=(40,60),ylim=(10,20))
#pyg.plot(data,'power',method='max')
#pyg.plot(data,'power',method='mean')
#pyg.plot(data,'power',method='slice',position=0.95,scale='G')
#pyg.plot(data,'bunching$',method='slice',position=0.95,scale='%')
#pyg.plot(data,'size',method='weighted',scale='mu')

#val = data.getRecord('spectrum')
#pyg.plot(data,'spectrum-farfield','slice',position=0.95)
#pyg.plotLattice(data,'aw')
data.info('Beam')
pyg.plot(data,'SCfield',method = 'profile',position=0.8)

