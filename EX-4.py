import tkinter as tk
from tkinter import ttk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TransferFunction:
    def __init__(self,K,zeta,wn):
        self.K=K; self.zeta=zeta; self.wn=wn

class StepResponse:
    def __init__(self,tf): self.tf=tf
    def simulate(self):
        t=np.linspace(0,10,500)
        K,z,w=self.tf.K,self.tf.zeta,self.tf.wn
        if z>=1:
            y=K*(1-np.exp(-w*t))
        else:
            wd=w*np.sqrt(1-z*z)
            phi=np.arccos(z)
            y=K*(1-(1/np.sqrt(1-z*z))*np.exp(-z*w*t)*np.sin(wd*t+phi))
        return t,y

class Analyzer:
    def __init__(self,t,y,target):
        self.t=t; self.y=y; self.target=target
    def overshoot(self):
        return max(0,(self.y.max()-self.target)/self.target*100)
    def rise(self):
        i=np.argmax(self.y>=0.9*self.target)
        return self.t[i]
    def settling(self):
        idx=np.where(np.abs(self.y-self.target)>0.02*self.target)[0]
        return self.t[idx[-1]] if len(idx) else 0

class App:
    def __init__(self,r):
        self.r=r
        for i,l,v in [(0,"K","1"),(1,"ζ","0.5"),(2,"ωn","2")]:
            ttk.Label(r,text=l).grid(row=i,column=0)
            e=ttk.Entry(r);e.insert(0,v);e.grid(row=i,column=1)
            setattr(self,f"e{i}",e)
        ttk.Button(r,text="Plot",command=self.run).grid(row=3,columnspan=2)
        self.info=ttk.Label(r,text="")
        self.info.grid(row=4,columnspan=2)
        self.fig=Figure(figsize=(5,3));self.ax=self.fig.add_subplot(111)
        FigureCanvasTkAgg(self.fig,master=r).get_tk_widget().grid(row=5,columnspan=2)
    def run(self):
        tf=TransferFunction(float(self.e0.get()),float(self.e1.get()),float(self.e2.get()))
        t,y=StepResponse(tf).simulate()
        an=Analyzer(t,y,tf.K)
        self.ax.clear();self.ax.plot(t,y);self.ax.grid();self.fig.canvas.draw()
        self.info.config(text=f"Overshoot={an.overshoot():.1f}%  Rise={an.rise():.2f}s  Settling={an.settling():.2f}s")
root=tk.Tk();root.title("Control System Analyzer");App(root);root.mainloop()
