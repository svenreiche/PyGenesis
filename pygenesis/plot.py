import matplotlib.pyplot as plt
import numpy as np

scale_factor ={'k':1e-3,'M':1e-6,'G':1e-9,'m':1e3,'mu':1e6,'n':1e9,'%':1e2}

def plot(obj,fld,method='raw',position=0.0,scale='',**kwargs):
    if not isinstance(obj, list):
        obj = [obj]
    multi = len(obj) > 1
    data=[ob.getData(fld,method,position) for ob in obj]
    if method =='raw' or method == 'norm':
        for dat in data:
            genplot2D(dat,multi,**kwargs)
        return
    elif method == 'max' or method == 'mean' or method == 'slice' or method == 'trace':
        genplot1D(data,scale =scale, multi=multi)
        return

def plotLattice(obj,fld,**kwargs):
    a = 1


def genplot1D(data,scale = '', multi=False):
    if scale in scale_factor.keys():
        scl = scale_factor[scale]
    else:
        scl = 1
    x=data[0]['x']
    xlab=data[0]['xlabel']
    file=data[0]['file']

    fig = plt.figure()
    ax = fig.add_subplot(111)
    icount = 0
    for dat in data:
        for key in dat['data'].keys():
            ylab, leg, title = getYLabel(key, scale, file, multi)
            ax.plot(x,scl*dat['data'][key],label=leg)
            icount+=1
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_title(title)
    if icount > 1:
        ax.legend()
    plt.show()


def genplot2D(data,multi=False,**kwargs):
    y=data['x']
    x=data['y']
    ext = (np.min(x),np.max(x),np.min(y),np.max(y))
    ylab=data['xlabel']
    xlab=data['ylabel']

    if 'xlabel' in kwargs.keys():
        xlab=kwargs['xlabel']
    if 'ylabel' in kwargs.keys():
        ylab=kwargs['ylabel']
    pkwargs={}
    if  'cmap' in kwargs.keys():
        pkwargs['cmap']=kwargs['cmap']
    if 'vmax' in kwargs.keys():
        pkwargs['vmax']=kwargs['vmax']

    for key in data['data'].keys():
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.imshow(np.flipud(data['data'][key]),aspect='auto',extent=ext,**pkwargs)
        ax.set_xlabel(xlab)
        ax.set_ylabel(ylab)
        if 'title' in kwargs.keys():
            title = kwargs['title']
        else:
            title = 'Dataset: '
            if multi:
                title +='%s/' % data['file']
            title +='%s' % key
            if data['method'] in Lab_method.keys():
                title+=' (%s)' % Lab_method[data['method']]
        ax.set_title(title)
        if 'xlim' in kwargs.keys():
            ax.set_xlim(kwargs['xlim'])
        if 'ylim' in kwargs.keys():
            ax.set_ylim(kwargs['ylim'])
        plt.show()


# method labels

def getYLabel(key,scale,file, multi):
    leg=key
    if multi:
        leg='%s/%s' % (file,key)
    var=''
    unit=''
    if scale=='mu':
        scale='$\mu$'
    if 'power' in key:
        title='Radiation Power'
        var='$P$'
        unit='W'
    elif 'position' in key:
        title = 'Position'
        var ='$<x>$'
        unit='m'
    elif 'position' in key:
        title = 'Size'
        var = '$\sigma$'
        unit = 'm'
    elif 'bunching' in key:
        title='Bunching'
        var='$b$'
        unit=''
    label=r'%s (%s%s)' % (var,scale,unit)
    return label,leg,title

Lab_method={'norm':'2D-Normalized','raw':'2D'}
#

