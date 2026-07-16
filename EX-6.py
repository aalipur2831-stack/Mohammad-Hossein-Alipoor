
import tkinter as tk
from tkinter import ttk, messagebox
import random

FARE = 5000

class Card:
    def __init__(self, card_id, balance=20000):
        self.card_id = card_id
        self.balance = balance
    def charge(self, amount):
        self.balance += amount
    def pay(self):
        if self.balance >= FARE:
            self.balance -= FARE
            return True
        return False

class Passenger:
    def __init__(self, name, card):
        self.name=name
        self.card=card

class Sensor:
    def detect(self): return True

class Motor:
    def __init__(self): self.opened=False
    def open(self): self.opened=True
    def close(self): self.opened=False

class Gate:
    def __init__(self, canvas):
        self.canvas=canvas
        self.sensor=Sensor()
        self.motor=Motor()
        self.left=self.canvas.create_rectangle(170,60,180,180,fill="gray")
        self.right=self.canvas.create_rectangle(220,60,230,180,fill="gray")
    def redraw(self):
        if self.motor.opened:
            self.canvas.coords(self.left,150,60,160,180)
            self.canvas.coords(self.right,240,60,250,180)
        else:
            self.canvas.coords(self.left,170,60,180,180)
            self.canvas.coords(self.right,220,60,230,180)

class App:
    def __init__(self):
        self.root=tk.Tk()
        self.root.title("Metro Gate Simulator")
        self.canvas=tk.Canvas(self.root,width=420,height=260,bg="white")
        self.canvas.pack()
        self.canvas.create_line(0,180,420,180)
        self.passenger=self.canvas.create_oval(20,130,50,160,fill="blue")
        self.gate=Gate(self.canvas)
        self.cards={
            "Ali":Card("1001",20000),
            "Sara":Card("1002",3000)
        }
        self.name=tk.StringVar(value="Ali")
        ttk.Combobox(self.root,textvariable=self.name,values=list(self.cards.keys()),state="readonly").pack()
        f=ttk.Frame(self.root);f.pack()
        ttk.Button(f,text="Enter",command=self.enter).grid(row=0,column=0,padx=5)
        ttk.Button(f,text="Charge +10000",command=self.charge).grid(row=0,column=1,padx=5)
        self.info=ttk.Label(self.root)
        self.info.pack()
        self.log=tk.Listbox(self.root,height=6,width=55)
        self.log.pack()
        self.update_info()
        self.root.mainloop()
    def current(self):
        return Passenger(self.name.get(),self.cards[self.name.get()])
    def update_info(self):
        c=self.cards[self.name.get()]
        self.info.config(text=f"Card:{c.card_id}  Balance:{c.balance}")
    def charge(self):
        c=self.cards[self.name.get()]
        c.charge(10000)
        self.log.insert(tk.END,f"{self.name.get()} charged card.")
        self.update_info()
    def animate(self,x=20):
        if x<360:
            self.canvas.coords(self.passenger,x,130,x+30,160)
            self.root.after(15,lambda:self.animate(x+5))
        else:
            self.canvas.coords(self.passenger,20,130,50,160)
            self.gate.motor.close(); self.gate.redraw()
    def enter(self):
        p=self.current()
        if self.gate.sensor.detect() and p.card.pay():
            self.gate.motor.open(); self.gate.redraw()
            self.log.insert(tk.END,f"{p.name} entered. Remaining:{p.card.balance}")
            self.update_info()
            self.animate()
        else:
            messagebox.showwarning("Denied","Insufficient balance")
            self.log.insert(tk.END,f"{p.name} denied.")

App()
