import numpy as np

#----------------------------------------------
# ANIMATION CLASSES
#----------------------------------------------

class Animation:
    def __init__(self,duration,delay=0,easing=None,axis=None,**kwargs):
        self.anim_function = None
        self.delay = delay
        self.duration = duration
        self.set_easing(easing)
        self.compute_timings()
        self.set_axis(axis)
        self.anim_type = 'show'
        self.obj = None
        kwargs = self.clean_kwargs(kwargs)
        self.kwargs = kwargs
        self.anim_function = self.function

    def set_axis(self,axis):
        self.axis = axis
        return self

    def compute_timings(self):
        self.x_min = self.delay
        self.x_max = self.duration + self.delay

    def set_duration(self,duration):
        self.duration = duration
        self.compute_timings()
        return self

    def set_delay(self,delay):
        self.delay = delay
        self.compute_timings()
        return self

    def set_easing(self,easing):
        self.easing = easing
        return self

    def apply(self,x):
        if x < self.x_min or x >= self.x_max:
            return
        if self.duration == 1:
            self.anim_function(1)
            return
        t = self.easing.ease((x-self.delay)/(self.duration-1))
        self.anim_function(t)

    def initialize(self):
        self.clean(0)

    def show(self):
        self.anim_type = 'show'
        return self

    def hide(self,delay=0,duration=None):
        self.anim_type = 'hide'
        self.set_delay(delay)
        if duration is not None:
            self.set_duration(duration)
        return self
    
    def spawn(self):
        self.anim_type = 'spawn'
        return self
    
    def despawn(self,delay=0,duration=None):
        self.anim_type = 'despawn'
        self.set_delay(delay)
        if duration is not None:
            self.set_duration(duration)
        return self
    
    def grow(self):
        self.anim_type = 'grow'
        return self
    
    def shrink(self,delay=0,duration=None):
        self.anim_type = 'shrink'
        self.set_delay(delay)
        if duration is not None:
            self.set_duration(duration)
        return self
    
    def update(self):
        self.anim_type = 'update'
        return self
    
    def deupdate(self):
        self.anim_type = 'deupdate'
        return self
    
    def morph(self,new_x,new_y,new_alpha=None):
        self.new_x = new_x
        self.new_y = new_y
        self.new_alpha = new_alpha
        self.anim_type = 'morph'
        return self
    
    def demorph(self):
        self.anim_type = 'demorph'
        return self
    
    def reverse(self,delay=0,duration=None):
        self.set_delay(delay)
        if duration is not None:
            self.set_duration(duration)
        return self
    
    def clean(self,x):
        if x >= self.x_min-1 and x < self.x_max-1 and self.obj is not None:
            if isinstance(self.obj,list):
                for obj in self.obj:
                    obj.remove()
            else:
                self.obj.remove()
            self.obj = None

    def clean_kwargs(self,kwargs):
        if 'duration' in kwargs:
            del kwargs['duration']
        if 'delay' in kwargs:
            del kwargs['delay']
        if 'easing' in kwargs:
            del kwargs['delay']
        if 'axis' in kwargs:
            del kwargs['axis']
        return kwargs

class zoom(Animation):
    def __init__(self,zoom, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zoom = 1/zoom

    def reverse(self):
        super().reverse()
        self.zoom = 1/self.zoom
        return self

    def initialize(self):
        self.width_init  = self.axis.get_xlim()[1]-self.axis.get_xlim()[0]
        self.height_init = self.axis.get_ylim()[1]-self.axis.get_ylim()[0]
        self.width_end = self.width_init * self.zoom
        self.height_end = self.height_init * self.zoom

    def function(self,t):
        center = ((self.axis.get_xlim()[1]+self.axis.get_xlim()[0])/2,(self.axis.get_ylim()[1]+self.axis.get_ylim()[0])/2)
        width = self.width_init + (self.width_end - self.width_init)*t
        height = self.height_init + (self.height_end - self.height_init)*t
        x_range = (center[0] - width/2, center[0] + width/2)
        y_range = (center[1] - height/2, center[1] + height/2)
        self.axis.set_xlim(x_range[0],x_range[1])
        self.axis.set_ylim(y_range[0],y_range[1])

class lims(Animation):
    def __init__(self,xlim=None,ylim=None, *args, **kwargs):
        if xlim is None and ylim is None:
            raise ValueError('Both xlim and ylim cannot be empty.')
        super().__init__(*args, **kwargs)
        self.xlim = xlim
        self.ylim = ylim

    def initialize(self):
        self.xlim_init = self.axis.get_xlim()
        self.ylim_init = self.axis.get_ylim()
        if self.xlim is not None:
            self.xlim_end = self.xlim
        else:
            self.xlim_end = self.xlim_init
        if self.ylim is not None:
            self.ylim_end = self.ylim
        else:
            self.ylim_end = self.ylim_init

    def function(self,t):
        xlim_left   = self.xlim_init[0] + (self.xlim_end[0] - self.xlim_init[0])*t
        xlim_right  = self.xlim_init[1] + (self.xlim_end[1] - self.xlim_init[1])*t
        ylim_bottom = self.ylim_init[0] + (self.ylim_end[0] - self.ylim_init[0])*t
        ylim_top    = self.ylim_init[1] + (self.ylim_end[1] - self.ylim_init[1])*t
        self.axis.set_xlim(xlim_left,xlim_right)
        self.axis.set_ylim(ylim_bottom,ylim_top)

class move(Animation):
    def __init__(self,pos, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pos = pos
        self.anim_function = self.function

    def reverse(self):
        super().reverse()
        self.pos = self.pos_init
        return self

    def initialize(self):
        width  = self.axis.get_xlim()[1]-self.axis.get_xlim()[0]
        height = self.axis.get_ylim()[1]-self.axis.get_ylim()[0]
        self.pos_init = (self.axis.get_xlim()[0]+width/2,self.axis.get_ylim()[0]+height/2)
        self.pos_end = self.pos

    def function(self,t):
        width  = self.axis.get_xlim()[1]-self.axis.get_xlim()[0]
        height = self.axis.get_ylim()[1]-self.axis.get_ylim()[0]
        pos_x = self.pos_init[0] + (self.pos_end[0] - self.pos_init[0])*t
        pos_y = self.pos_init[1] + (self.pos_end[1] - self.pos_init[1])*t
        self.axis.set_xlim(pos_x-width/2,pos_x+width/2)
        self.axis.set_ylim(pos_y-height/2,pos_y+height/2)

class scatter(Animation):
    def __init__(self,x,y, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = x
        self.y = y
    
    def function(self,t):
        kwargs = self.kwargs.copy()
        if 'alpha' not in kwargs:
            kwargs['alpha'] = 1
        if self.anim_type == 'show':
            kwargs['alpha'] *= t
            x = self.x
            y = self.y
        elif self.anim_type == 'hide':
            kwargs['alpha'] *= 1-t
            x = self.x
            y = self.y
        elif self.anim_type == 'spawn':
            i_max = min(round(t*len(self.x)) + 1,len(self.x))
            x = self.x[:i_max]
            y = self.y[:i_max]
            if 'c' in kwargs:
                kwargs['c'] = kwargs['c'][:i_max]
        elif self.anim_type == 'despawn':
            i_max = max(round((1-t)*len(self.x)),0)
            x = self.x[:i_max]
            y = self.y[:i_max]
            if 'c' in kwargs:
                kwargs['c'] = kwargs['c'][:i_max]
        elif self.anim_type == 'morph':
            x = []
            y = []
            a = []
            if 'alpha' not in kwargs:
                kwargs['alpha'] = 1
            for i in range(len(self.x)):
                x.append(self.x[i] + (self.new_x[i] - self.x[i])*t)
                y.append(self.y[i] + (self.new_y[i] - self.y[i])*t)
                if self.new_alpha is not None:
                    a.append(kwargs['alpha'] + (self.new_alpha[i] - kwargs['alpha'])*t)
                else:
                    a.append(kwargs['alpha'])
            kwargs['alpha'] = a
        elif self.anim_type == 'demorph':
            x = []
            y = []
            a = []
            if 'alpha' not in kwargs:
                kwargs['alpha'] = 1
            for i in range(len(self.x)):
                x.append(self.x[i] + (self.new_x[i] - self.x[i])*(1-t))
                y.append(self.y[i] + (self.new_y[i] - self.y[i])*(1-t))
                if self.new_alpha is not None:
                    a.append(kwargs['alpha'] + (self.new_alpha[i] - kwargs['alpha'])*t)
                else:
                    a.append(kwargs['alpha'])
            kwargs['alpha'] = a
        
        self.obj = self.axis.scatter(x,y,**kwargs)

class plot(Animation):
    def __init__(self,x,y, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.new_x = None
        self.new_y = None
        self.x = x
        self.y = y

    def clean(self,x):
        super().clean(x)
        if x == self.x_max-1 and self.new_x is not None:
            self.x = self.new_x
            self.y = self.new_y
            self.new_x = None
            self.new_y = None
    
    def function(self,t):
        kwargs = self.kwargs.copy()
        if 'alpha' not in kwargs:
            kwargs['alpha'] = 1
        if self.anim_type == 'show':
            kwargs['alpha'] *= t
            x = self.x
            y = self.y
        elif self.anim_type == 'hide':
            kwargs['alpha'] *= 1-t
            x = self.x
            y = self.y
        elif self.anim_type == 'spawn':
            i_max = min(round(t*len(self.x)) + 1,len(self.x))
            x = self.x[:i_max]
            y = self.y[:i_max]
            if 'c' in kwargs:
                kwargs['c'] = kwargs['c'][:i_max]
        elif self.anim_type == 'despawn':
            i_max = max(round((1-t)*len(self.x)),0)
            x = self.x[:i_max]
            y = self.y[:i_max]
            if 'c' in kwargs:
                kwargs['c'] = kwargs['c'][:i_max]
        elif self.anim_type == 'morph':
            x = []
            y = []
            for i in range(len(self.x)):
                x.append(self.x[i] + (self.new_x[i] - self.x[i])*t)
                y.append(self.y[i] + (self.new_y[i] - self.y[i])*t)
        elif self.anim_type == 'demorph':
            x = []
            y = []
            for i in range(len(self.x)):
                x.append(self.x[i] + (self.new_x[i] - self.x[i])*(1-t))
                y.append(self.y[i] + (self.new_y[i] - self.y[i])*(1-t))
        
        self.obj = self.axis.plot(x,y,**kwargs)

class fill_between(Animation):
    def __init__(self,x,y1,y2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = np.array(x)
        self.y1 = np.array(y1).reshape(-1)
        self.y2 = np.array(y2).reshape(-1)
        if self.y1.size != self.x.size:
            self.y1 = np.ones_like(self.x)*self.y1[0]
        if self.y2.size != self.x.size:
            self.y2 = np.ones_like(self.x)*self.y2[0]
    
    def function(self,t):
        kwargs = self.kwargs.copy()
        if 'alpha' not in kwargs:
            kwargs['alpha'] = 1
        if self.anim_type == 'show':
            kwargs['alpha'] *= t
            x = self.x
            y1 = self.y1
            y2 = self.y2
        elif self.anim_type == 'hide':
            kwargs['alpha'] *= 1-t
            x = self.x
            y1 = self.y1
            y2 = self.y2
        elif self.anim_type == 'spawn':
            i_max = min(round(t*len(self.x)) + 1,len(self.x))
            x = self.x[:i_max]
            y1 = self.y1[:i_max]
            y2 = self.y2[:i_max]
            if 'c' in kwargs:
                kwargs['c'] = kwargs['c'][:i_max]
        elif self.anim_type == 'despawn':
            i_max = max(round((1-t)*len(self.x)),0)
            x = self.x[:i_max]
            y1 = self.y1[:i_max]
            y2 = self.y2[:i_max]
            if 'c' in kwargs:
                kwargs['c'] = kwargs['c'][:i_max]
        elif self.anim_type == 'grow':
            widths = self.y2 - self.y1
            centers = (self.y2 + self.y1)/2
            x = self.x
            y1 = centers - t*widths/2
            y2 = centers + t*widths/2
        elif self.anim_type == 'shrink':
            widths = self.y2 - self.y1
            centers = (self.y2 + self.y1)/2
            x = self.x
            y1 = centers - (1-t)*widths/2
            y2 = centers + (1-t)*widths/2
        
        self.obj = self.axis.fill_between(x=x,y1=y1,y2=y2,**kwargs)

class fill_betweenx(Animation):
    def __init__(self,y,x1,x2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.y = np.array(y)
        self.x1 = np.array(x1).reshape(-1)
        self.x2 = np.array(x2).reshape(-1)
        if self.x1.size != self.y.size:
            self.x1 = np.ones_like(self.y[0])*self.x1[0]
        if self.x2.size != self.y.size:
            self.x2 = np.ones_like(self.y[0])*self.x2[0]
    
    def function(self,t):
        kwargs = self.kwargs.copy()
        if 'alpha' not in kwargs:
            kwargs['alpha'] = 1
        if self.anim_type == 'show':
            kwargs['alpha'] *= t
            y = self.y
            x1 = self.x1
            x2 = self.x2
        elif self.anim_type == 'hide':
            kwargs['alpha'] *= 1-t
            y = self.y
            x1 = self.x1
            x2 = self.x2
        elif self.anim_type == 'spawn':
            i_max = min(round(t*len(self.y)) + 1,len(self.y))
            y = self.y[:i_max]
            x1 = self.x1[:i_max]
            x2 = self.x2[:i_max]
            if 'c' in kwargs:
                kwargs['c'] = kwargs['c'][:i_max]
        elif self.anim_type == 'despawn':
            i_max = max(round((1-t)*len(self.y)),0)
            y = self.y[:i_max]
            x1 = self.x1[:i_max]
            x2 = self.x2[:i_max]
            if 'c' in kwargs:
                kwargs['c'] = kwargs['c'][:i_max]
        elif self.anim_type == 'grow':
            widths = self.x2 - self.x1
            centers = (self.x2 + self.x1)/2
            y = self.y
            x1 = centers - t*widths/2
            x2 = centers + t*widths/2
        elif self.anim_type == 'shrink':
            widths = self.x2 - self.x1
            centers = (self.x2 + self.x1)/2
            y = self.y
            x1 = centers - (1-t)*widths/2
            x2 = centers + (1-t)*widths/2
        
        self.obj = self.axis.fill_betweenx(y=y,x1=x1,x2=x2,**kwargs)

class axvline(Animation):
    def __init__(self,x, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = x
    
    def function(self,t):
        kwargs = self.kwargs.copy()
        if 'alpha' not in kwargs:
            kwargs['alpha'] = 1
        x = self.x
        y_max = 1
        if self.anim_type == 'show':
            kwargs['alpha'] *= t
        elif self.anim_type == 'hide':
            kwargs['alpha'] *= 1-t
        elif self.anim_type == 'spawn':
            y_max = t
        elif self.anim_type == 'despawn':
            y_max = (1-t)

        self.obj = self.axis.axvline(x,ymin=0,ymax=y_max,**kwargs)

class errorbar(Animation):
    def __init__(self,x,y,xerr=None,yerr=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = x
        self.y = y
        if xerr is None:
            xerr = np.zeros_like(x)
        if yerr is None:
            yerr = np.zeros_like(y)
        self.xerr = xerr
        self.yerr = yerr
    
    def function(self,t):
        kwargs = self.kwargs.copy()
        if 'alpha' not in kwargs:
            kwargs['alpha'] = 1
        if self.anim_type == 'show':
            kwargs['alpha'] *= t
            x = self.x
            y = self.y
            xerr = self.xerr
            yerr = self.yerr
        elif self.anim_type == 'hide':
            kwargs['alpha'] *= 1-t
            x = self.x
            y = self.y
            xerr = self.xerr
            yerr = self.yerr
        elif self.anim_type == 'spawn':
            i_max = min(round(t*len(self.x)) + 1,len(self.x))
            x = self.x[:i_max]
            y = self.y[:i_max]
            xerr = self.xerr[:i_max]
            yerr = self.yerr[:i_max]
            if 'c' in kwargs:
                kwargs['c'] = kwargs['c'][:i_max]
        elif self.anim_type == 'despawn':
            i_max = max(round((1-t)*len(self.x)),0)
            x = self.x[:i_max]
            y = self.y[:i_max]
            xerr = self.xerr[:i_max]
            yerr = self.yerr[:i_max]
            if 'c' in kwargs:
                kwargs['c'] = kwargs['c'][:i_max]
        
        self.obj = self.axis.errorbar(x,y,xerr=xerr,yerr=yerr,**kwargs)

class hist(Animation):
    def __init__(self,x,bins=None,range=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = x
        self.bins = bins
        self.range = range
    
    def function(self,t):
        kwargs = self.kwargs.copy()
        if self.anim_type == 'show':
            kwargs['alpha'] *= t
        if self.anim_type == 'hide':
            kwargs['alpha'] *= 1-t
        if self.anim_type == 'spawn':
            i_max = min(round(t*len(self.x)) + 1,len(self.x))
        elif self.anim_type == 'despawn':
            i_max = max(round((1-t)*len(self.x)),0)
        x = self.x[:i_max]
        h,edges,self.obj = self.axis.hist(x,bins=self.bins,range=self.range,**kwargs)

class hist2d(Animation):
    def __init__(self,x,y,bins=None,range=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = x
        self.y = y
        self.bins = bins
        self.range = range
    
    def function(self,t):
        kwargs = self.kwargs.copy()
        if 'alpha' not in kwargs:
            kwargs['alpha'] = 1
            i_max = len(self.x)
        if self.anim_type == 'show':
            kwargs['alpha'] *= t
        if self.anim_type == 'hide':
            kwargs['alpha'] *= 1-t
        elif self.anim_type == 'spawn':
            i_max = min(round(t*len(self.x)) + 1,len(self.x))
        elif self.anim_type == 'despawn':
            i_max = max(round((1-t)*len(self.x)),0)
        x = self.x[:i_max]
        y = self.y[:i_max]
        old_xlim = self.axis.get_xlim()
        old_ylim = self.axis.get_ylim()
        h,xedges,yedges,self.obj = self.axis.hist2d(x,y,bins=self.bins,range=self.range,**kwargs)
        self.axis.set_xlim(old_xlim)
        self.axis.set_ylim(old_ylim)

class contourf(Animation):
    def __init__(self,z,levels=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.z = z
        self.levels = levels
    
    def function(self,t):
        kwargs = self.kwargs.copy()
        if 'alpha' not in kwargs:
            kwargs['alpha'] = 1
        if self.anim_type == 'show':
            kwargs['alpha'] *= t
        elif self.anim_type == 'hide':
            kwargs['alpha'] *= (1-t)
        old_xlim = self.axis.get_xlim()
        old_ylim = self.axis.get_ylim()
        self.obj = self.axis.contourf(self.z,levels=self.levels,**kwargs)
        self.axis.set_xlim(old_xlim)
        self.axis.set_ylim(old_ylim)

class text(Animation):
    def __init__(self,x,y,string, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = x
        self.y = y
        self.string = string
        if isinstance(self.string,str):
            self.string = np.array(self.string).reshape(-1)
    
    def function(self,t):
        kwargs = self.kwargs.copy()
        if 'alpha' not in kwargs:
            kwargs['alpha'] = 1
        if self.anim_type == 'show':
            kwargs['alpha'] *= t
            s = self.string[0]
        elif self.anim_type == 'hide':
            kwargs['alpha'] *= 1-t
            s = self.string[0]
        elif self.anim_type == 'update':
            i = min(round(t*len(self.string)) + 1,len(self.string))
            s = self.string[i]
        elif self.anim_type == 'deupdate':
            i = max(round((1-t)*len(self.string)),0)
            s = self.string[i]

        self.obj = self.axis.text(x=self.x,y=self.y,s=s,**kwargs)