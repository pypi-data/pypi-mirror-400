import numpy as np
import subprocess,os,shlex,io,pickle
import matplotlib.pyplot as plt
import shutil

from .easings import *
from .animations import *

def in_notebook():
    try:
        from IPython import get_ipython
        shell = get_ipython().__class__.__name__
        return shell == "ZMQInteractiveShell"
    except Exception:
        return False
    
if in_notebook():
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm

def status_message(start_msg, end_msg):
    if in_notebook():
        from IPython.display import display, update_display, Markdown
        display_id = display(Markdown(start_msg), display_id=True)
        def update():
            update_display(Markdown(end_msg), display_id=display_id.display_id)
        return update
    else:
        print(start_msg, end="\r", flush=True)
        def update():
            print(end_msg + " " * max(0, len(start_msg) - len(end_msg)))
        return update

#----------------------------------------------
# SEQUENCE CLASS
#----------------------------------------------

class Sequence:
    def __init__(self,fig,name,tqdm=True,dpi=200,easing=easeLinear()):
        #buf = io.BytesIO()
        #pickle.dump(fig, buf)
        #buf.seek(0)
        #self.fig = pickle.load(buf) 
        self.fig = fig
        self.ax = self.fig.get_axes()
        if len(self.ax) == 1:
            self.ax = self.ax[0]
        else:
            self.ax = np.array(self.ax)
        if isinstance(self.ax,np.ndarray):
            if isinstance(self.ax[0],np.ndarray):
                self.main_axis = self.ax[0,0]
            else:
                self.main_axis = self.ax[0]
        else:
            self.main_axis = self.ax
        self.name = name
        self.tqdm = tqdm
        self.dpi = dpi
        self.easing = easing
        self.x = 0
        self.sequence_str = ''
        self.set_white()

    def set_white(self):
        if isinstance(self.ax,np.ndarray) == False:
            axes = (self.ax,)
        else:
            axes = self.ax.flatten()
        for axis in axes:
            axis.spines['bottom'].set_color('white')
            axis.spines['top'].set_color('white')
            axis.spines['left'].set_color('white')
            axis.spines['right'].set_color('white')
            axis.xaxis.label.set_color('white')
            axis.yaxis.label.set_color('white')
            axis.tick_params(axis='both',colors='white')

    def plot(self,animations,easing=None,debug=False):
        if isinstance(animations,Animation):
            animations = (animations,)
        for animation in animations:
            if animation.axis is None:
                animation.set_axis(self.main_axis)
            animation.initialize()
            if animation.easing == None:
                if easing is None:
                    animation.easing = self.easing
                else:
                    animation.easing = easing
            animation.apply(animation.x_max-1)
        self.save_plot(debug)

    def animate(self,animations,easing=None,debug=False):
        if isinstance(animations,Animation):
            animations = (animations,)
        x_max = 0
        for animation in animations:
            if animation.axis is None:
                animation.set_axis(self.main_axis)
            animation.initialize()
            if animation.easing == None:
                if easing is None:
                    animation.easing = self.easing
                else:
                    animation.easing = easing

            if animation.x_max > x_max:
                x_max = animation.x_max
        
        loop = range(x_max)
        if self.tqdm:
            loop = tqdm(loop)

        for x in loop:
            for animation in animations:
                animation.apply(x)
            self.save_plot(debug)
            for animation in animations:
                animation.clean(x)
        
    def wait(self,duration):
        #Have to do in two steps, because doesn't work in 1 if wait is the last animation of the sequence
        self.sequence_str += 'file \'' + self.name + '_{}.png\'\n'.format(self.x - 1)
        self.sequence_str += 'duration {}\n'.format((duration-1)/30)
        self.sequence_str += 'file \'' + self.name + '_{}.png\'\n'.format(self.x - 1)
        self.sequence_str += 'duration {}\n'.format(1/30)
        self.x += 1

    def save_plot(self,debug):
        if debug is False:
            if os.path.isdir(self.name) == False:
                os.makedirs(self.name)
            fn = self.name + '/' + self.name +  '_{}.png'.format(self.x)
            self.fig.savefig(fn,dpi=self.dpi,transparent=True)
            
            self.sequence_str += 'file \'' + self.name + '_{}.png\'\n'.format(self.x)
            self.sequence_str += 'duration {}\n'.format(1/30)
        self.x += 1
    
    def save_video(self,speed=1,multialpha=False,prerendered=False,clean=True):
        video_fn = self.name + '.mov'
        update = status_message("Rendering video...", "Saved video " + video_fn)
        if not prerendered:
            self.sequence_str += 'file \'' + self.name + '_{}.png\'\n'.format(self.x-1)#repeat last frame otherwise not seen for some reason
            self.sequence_str += 'duration {}\n'.format(1/30)
            with open(self.name + '/' + self.name + '.txt','w+') as f:
                lines = self.sequence_str.split('\n')
                for line in lines:
                    if speed != 1:
                        if 'duration' in line:
                            line = 'duration {}'.format(float(line.split(' ')[-1])/speed)
                    f.write(line + '\n')
        sequence_fn = self.name + '/' + self.name  + '.txt'

        if multialpha:
            command = 'ffmpeg -f concat -safe 0 -i {} -y -vf premultiply=inplace=1 -c:v prores_ks -profile:v 4 -pix_fmt yuva444p10le -hide_banner -loglevel error {}'.format(sequence_fn,video_fn)
        else:
            command = 'ffmpeg -f concat -safe 0 -i {} -y -c:v prores -pix_fmt yuva444p10le -hide_banner -loglevel error {}'.format(sequence_fn,video_fn)
        subprocess.run(shlex.split(command))
        if clean:
            shutil.rmtree(self.name)
        plt.close()
        update()


#TODO : implementing blitting as in https://matplotlib.org/stable/users/explain/animations/blitting.html
#has to be an option on the sequence Class, as it can only draw objects on top of the saved background.

#TODO : implement deepcopy of fig so that we can rerun the same code of Sequence without having to reinitialize the fig, because it changes in the sequence code
#code implemented in the init of sequence, but the axes are regenerated from the copied figure, so if some anims use a specific axis, it does not exist anymore.
#have to, as initialisation, replace the specific axis with the new one (save old axis in Sequence, find index of specific axis in old axes, get new axis using index)