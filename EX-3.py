# Placeholder: Due to response size limits, this file contains a starter GUI.
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import random

class Tank:
    def __init__(self):
        self.level=50
        self.max_level=200
    def update(self,inflow,outflow):
        self.level=max(0,min(self.max_level,self.level+inflow-outflow))

class App:
    def __init__(self,root):
        self.root=root
        self.root.title("Water Tank Level Control")
        self.tank=Tank()
        self.running=False
        self.mode=tk.StringVar(value="PID")
        self.canvas=tk.Canvas(root,width=120,height=260,bg="white")
        self.canvas.grid(row=0,column=0,rowspan=5,padx=10,pady=10)
        ttk.Radiobutton(root,text="PID",variable=self.mode,value="PID").grid(row=0,column=1,sticky="w")
        ttk.Radiobutton(root,text="On-Off",variable=self.mode,value="ONOFF").grid(row=1,column=1,sticky="w")
        self.lbl=ttk.Label(root,text="Level: 50 cm")
        self.lbl.grid(row=2,column=1)
        ttk.Button(root,text="Start",command=self.start).grid(row=3,column=1,sticky="ew")
        ttk.Button(root,text="Stop",command=self.stop).grid(row=4,column=1,sticky="ew")
        self.fig=Figure(figsize=(5,3),dpi=100)
        self.ax=self.fig.add_subplot(111)
        self.hist=[]
        self.line,=self.ax.plot([],[])
        self.ax.set_ylim(0,200)
        self.ax.set_title("Water Level")
        FigureCanvasTkAgg(self.fig,master=root).get_tk_widget().grid(row=5,column=0,columnspan=2)
        self.draw()
    def draw(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(30,20,90,220)
        h=(self.tank.level/200)*200
        self.canvas.create_rectangle(31,220-h,89,219,fill="deepskyblue")
        self.lbl.config(text=f"Level: {self.tank.level:.1f} cm")
    def loop(self):
        if not self.running:return
        if self.mode.get()=="ONOFF":
            inflow=8 if self.tank.level<120 else 0
        else:
            e=120-self.tank.level
            inflow=max(0,min(8,0.08*e+4))
        self.tank.update(inflow,4)
        self.hist.append(self.tank.level)
        self.line.set_data(range(len(self.hist)),self.hist)
        self.ax.set_xlim(0,max(50,len(self.hist)))
        self.fig.canvas.draw_idle()
        self.draw()
        self.root.after(200,self.loop)
    def start(self):
        if not self.running:
            self.running=True
            self.loop()
    def stop(self):
        self.running=False

root=tk.Tk()
App(root)
root.mainloop()
