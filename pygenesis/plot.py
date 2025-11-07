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
    genplot1D(data,scale =scale, multi=multi, method =method,**kwargs)

def plotLattice(obj,fld,scale='',**kwargs):
    if not isinstance(obj, list):
        obj = [obj]
    multi = len(obj) > 1
    data=[ob.getLattice(fld) for ob in obj]
    genplot1D(data, scale=scale, multi=multi,drawstyle = 'steps-mid', **kwargs)


def genplot1D(data,scale = '', multi=False,method='raw',**kwargs):
    if scale in scale_factor.keys():
        scl = scale_factor[scale]
    else:
        scl = 1
    x=data[0]['x']
    xlab=data[0]['xlabel']
    ylab = data[0]['ylabel']
    file=data[0]['file']

    dnames=[]
    for dat in data:
        file = dat['file']
        for key in dat['data'].keys():
            dnames.append('%s:%s' % (file,key))
    labels,ylabels = getLabels(dnames,scale=scale,multi=multi,method=method)

    pkwargs = {}
    if 'drawstyle' in kwargs.keys():
        pkwargs['drawstyle'] = kwargs['drawstyle']

    if 'log' in kwargs.keys():
        dolog = kwargs['log']
    else:
        dolog = False

    fig = plt.figure()
    ax = fig.add_subplot(111)
    icount = 0
    for dat in data:
        for key in dat['data'].keys():
            labtag = '%s:%s' % (dat['file'],key)
            if dolog:
                ax.semilogy(x,scl*dat['data'][key],label=labels[labtag],**pkwargs)
            else:
                ax.plot(x,scl*dat['data'][key],label=labels[labtag],**pkwargs)
            icount+=1
    if method == 'rms':
        fullylab = r'$\sigma_'+ylab[1:]
    else:
        fullylab = ''
        for yy in ylabels:
            fullylab = fullylab + yy+', '
        if len(fullylab)>1:
            fullylab = fullylab[:-2]
    ax.set_xlabel(xlab)
    ax.set_ylabel(fullylab)
    if 'xlim' in kwargs.keys():
        ax.set_xlim(kwargs['xlim'])
    if 'ylim' in kwargs.keys():
        ax.set_ylim(kwargs['ylim'])

    if 'title' in kwargs.keys():
        title = kwargs['title']
    elif data[0]['method'] in Lab_method.keys():
        title = Lab_method[data[0]['method']]
    else:
        title=data[0]['method']
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
        if 'vscl' in kwargs.keys():
            pkwargs['vmax'] = kwargs['vscl'] * np.max(data['data'][key])
            pkwargs['vmin'] = kwargs['vscl'] * np.min(data['data'][key])
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


plabels={'power':['P','W'],'xsize':['\sigma_x','m'],'ysize':['\sigma_y','m'],'xpointing':[r'<\theta_x>','rad'],'ypointing':[r'<\theta_y>','rad'],
         'xposition':['<x>','m'],'yposition':['<y>','m'],'xdivergence':[r'<\sigma_\theta_x>','rad'],'ydivergence':[r'<\sigma_\theta_y>','rad'],
         'intensity-nearfield':['dP/dA',r'W/m$^2$'],'phase-nearfield':['\phi_{NF}','rad'],
         'intensity-farfield':['dP/d\Omega',r'W/rad$^2$'],'phase-farfield':['\phi_{FF}','rad'],
         'pxposition':['<x^\prime>','rad'],'pyposition':['<y^\prime>','rad'],'pulseenergy':['E','J'],
         'xmin':['Min(x)','m'],'ymin':['Min(y)','m'],'pxmin':['Min(x^\prime)','rad'],'pymin':['Min(y^\prime)','rad'],
         'xmax':['Max(x)','m'],'ymax':['Max(y)','m'],'pxax':['Max(x^\prime)','rad'],'pymax':['Max(y^\prime)','rad'],
         'energy':['\gamma','mc$^2$'],'energyspread':['\sigma_\gamma','mc$^2$'],'emax':['Max(\gamma)','mc$^2$'],'emin':['Min(\gamma)','mc$^2$'],
         'current':['I','A'],'emitx':['\epsilon_x','m'],'emity':['\epsilon_y','m'],'betax':[r'\beta_x','m'],'betay':[r'\beta_y','m'],
         'alphax':[r'\alpha_x','rad'],'alphay':[r'\alpha_y','rad'],'bunching':[r'|<exp(i\theta)>|',''],'bunchingphase':[r'\phi_b','rad'],
         'efield':['W_z','eV/m'],'wakefield':['W_z','eV/m'],'LSCfield':['W_z','eV/m'],'SSCfield':['W_z','eV/m'],
         'spectrum-nearfield':['P_{NF}(E_{ph})','arb. units'],'spectrum-farfield':['P_{FF}(E_{ph})','arb. units'],
         'aw':['a_w',''],'ax':['\Delta x_w','m'],'ay':['\Delta y_w','m'],
         'qf':['dB/dx','T/m'],'qx':['\Delta x_q','m'],'qy':['\Delta y_q','m'],
         'cx':['\Delta x^\prime','rad'],'cy':['\Delta y^\prime','rad'],
         'ku':['k_w','m$^{-1}$'], 'kx':['k_x',''],'ky':['k_y',''],
         'phaseshift':[r'\Delta\theta','rad'],'slippage':['\Delta s','$\lambda_{ref}$'],
         'dz':['\Delta z','m'],'z':['z','m'],'gradx':['d\log(a_w)/dx','m$^{-1}$'],'grady':['d\log(a_w)/dy','m$^{-1}$'],
         'chic_angle':[r'\alpha_c','rad'],'chic_lb':['L_b','m'],'chic_ld':['L_d','m'],'chic_lt':['L_c','m']}





def getLabels(dnames,scale='',multi=False,method='raw'):
    res={}
    labels=[]
    if scale =='mu':
        scale ='$\mu$'
    for dname in dnames:
        split1 = dname.split(':')
        file = split1[0]
        field = split1[1]
        split2 = field.split('/')
        group = split2[0]
        tag = split2[-1]
        if method=='integrated':
            tag = tag.replace('power','pulseenergy')
        if tag in plabels.keys():
            lab=plabels[tag]
            if len(lab[1])>0:
                ylabel = r'$%s$ (%s%s)' % (lab[0],scale,lab[1])
            else:
                ylabel = r'$%s$ %s' % (lab[0], scale)
            if multi:
                label = r'$%s$ (%s/%s)' % (lab[0],file,group)
            else:
                label = r'$%s$ (%s)' % (lab[0],group)
        else:
            ylabel=field
            if multi:
                label=file+'/'+field
            else:
                label=field
        res[dname] = label
        if not ylabel in labels:
            labels.append(ylabel)
    return res,labels



Lab_method={'norm':'2D-Normalized','raw':'2D','wigner':'Wigner Distribution','mean':'Mean Value','max':'Maximum Value',
            'profile':'Profile','slice':'Trace of Single Slice','rms':'RMS Width','weighted':'Weighted Mean',
            'integrated':'Integrated Value','lattice':'Lattice'}
#


