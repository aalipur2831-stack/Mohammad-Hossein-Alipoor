import tkinter as tk
from tkinter import messagebox
import random
from collections import deque

# ==================== Classes ====================

class Person:
    def __init__(self, pid, src, dst):
        self.id = pid
        self.src = src
        self.dst = dst
        self.wait = 0

class Elevator:
    def __init__(self, eid, cap=8):
        self.id = eid
        self.cap = cap
        self.floor = 1
        self.dir = 'idle'
        self.passengers = []
        self.requests = deque()
        self.open = False
    
    def load(self):
        return len(self.passengers)
    
    def is_full(self):
        return self.load() >= self.cap

class Building:
    def __init__(self):
        self.floors = 40
        self.waiting = {i: [] for i in range(1, 41)}
        self.elevators = [Elevator(1), Elevator(2)]
        self.served = 0
        self.total_wait = 0

# ==================== Controller ====================

class Controller:
    def __init__(self, building):
        self.b = building
    
    def find_elevator(self, floor, direction):
        best = None
        best_dist = 999
        for e in self.b.elevators:
            if e.is_full():
                continue
            dist = abs(e.floor - floor)
            if e.dir == direction:
                if direction == 'up' and e.floor <= floor:
                    dist -= 5
                elif direction == 'down' and e.floor >= floor:
                    dist -= 5
            if dist < best_dist:
                best_dist = dist
                best = e
        return best
    
    def assign_request(self, person):
        """Assign a new passenger request to the best elevator"""
        direction = 'up' if person.dst > person.src else 'down'
        elevator = self.find_elevator(person.src, direction)
        if elevator:
            # Add the source floor to elevator's requests if not already there
            if person.src not in elevator.requests:
                elevator.requests.append(person.src)
            # Store the passenger in building's waiting list
            # The elevator will pick them up when it reaches their floor
            return True
        return False
    
    def step(self):
        for e in self.b.elevators:
            self.process(e)
    
    def process(self, e):
        if not e.requests and not e.passengers:
            e.dir = 'idle'
            return
        
        if not e.requests:
            for p in e.passengers:
                if p.dst not in e.requests:
                    e.requests.append(p.dst)
            return
        
        target = e.requests[0]
        
        if e.floor < target:
            e.dir = 'up'
            e.floor += 1
        elif e.floor > target:
            e.dir = 'down'
            e.floor -= 1
        else:
            # Reached target floor - open doors
            e.open = True
            
            # Drop off passengers
            new_pass = []
            for p in e.passengers:
                if p.dst == e.floor:
                    self.b.served += 1
                    self.b.total_wait += p.wait
                else:
                    new_pass.append(p)
            e.passengers = new_pass
            
            # Pick up passengers waiting on this floor
            waiting = self.b.waiting[e.floor][:]
            for p in waiting:
                if e.is_full():
                    break
                # Determine direction if idle
                if e.dir == 'idle':
                    e.dir = 'up' if p.dst > p.src else 'down'
                # Only pick up if going in same direction
                if (e.dir == 'up' and p.dst > p.src) or (e.dir == 'down' and p.dst < p.src):
                    e.passengers.append(p)
                    self.b.waiting[e.floor].remove(p)
                    if p.dst not in e.requests:
                        e.requests.append(p.dst)
            
            # Remove the completed request
            e.requests.popleft()
            e.open = False

# ==================== GUI ====================

class App:
    def __init__(self, root):
        self.root = root
        root.title("Smart Elevator")
        root.geometry("900x650")
        root.configure(bg='#1a1a2e')
        
        self.b = Building()
        self.ctrl = Controller(self.b)
        self.running = False
        self.speed = 500  # milliseconds
        
        self.setup_ui()
        self.draw()
    
    def setup_ui(self):
        # Top panel
        top = tk.Frame(self.root, bg='#16213e')
        top.pack(fill=tk.X, pady=5)
        
        tk.Button(top, text="Start", command=self.start, bg='#27ae60', fg='white',
                 font=('Arial', 11, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Stop", command=self.stop, bg='#e67e22', fg='white',
                 font=('Arial', 11, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Reset", command=self.reset, bg='#e74c3c', fg='white',
                 font=('Arial', 11, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="New Passenger", command=self.add_person, bg='#3498db', fg='white',
                 font=('Arial', 11, 'bold'), width=12).pack(side=tk.LEFT, padx=5)
        
        # Stats
        self.stats = tk.Label(top, text="Served: 0 | Avg Wait: 0.0 sec",
                             bg='#16213e', fg='white', font=('Arial', 10))
        self.stats.pack(side=tk.RIGHT, padx=10)
        
        # Canvas
        self.canvas = tk.Canvas(self.root, bg='#0f3460', width=850, height=550)
        self.canvas.pack(pady=5)
    
    def draw(self):
        self.canvas.delete('all')
        w, h = 850, 550
        fx, fw = 100, 500
        fh = 12
        base = 520
        
        # Floors
        for fl in range(1, 41):
            y = base - (fl-1) * fh
            self.canvas.create_line(fx, y, fx+fw, y, fill='#aaa', width=1)
            self.canvas.create_text(fx-15, y-3, text=str(fl), fill='#ddd', font=('Arial', 7))
            
            cnt = len(self.b.waiting[fl])
            if cnt:
                self.canvas.create_text(fx+25, y-3, text=f'👤{cnt}', fill='#ff6b6b', font=('Arial', 8))
        
        # Elevators
        for i, e in enumerate(self.b.elevators):
            x = 200 + i*300
            y = base - (e.floor-1) * fh - 10
            color = '#2ecc71' if e.open else '#3498db'
            self.canvas.create_rectangle(x, y, x+55, y+15, fill=color, outline='white', width=2)
            
            if e.dir == 'up':
                self.canvas.create_text(x+27, y-15, text='↑', fill='#2ecc71', font=('Arial', 14))
            elif e.dir == 'down':
                self.canvas.create_text(x+27, y-15, text='↓', fill='#e74c3c', font=('Arial', 14))
            
            load = e.load()
            if load:
                self.canvas.create_text(x+27, y+22, text=f'👥{load}', fill='#ffd93d', font=('Arial', 8))
            
            # Show next target
            if e.requests:
                target = e.requests[0]
                self.canvas.create_text(x+27, y+42, text=f'Target: {target}', fill='#aaa', font=('Arial', 6))
            
            self.canvas.create_text(x+27, y+52, text=f'Elevator {e.id}', fill='#aaa', font=('Arial', 7))
        
        # Legend
        self.canvas.create_text(20, 20, text='Legend:', fill='white', font=('Arial', 9, 'bold'), anchor='w')
        self.canvas.create_rectangle(20, 30, 35, 45, fill='#3498db')
        self.canvas.create_text(42, 38, text='Moving', fill='white', font=('Arial', 8), anchor='w')
        self.canvas.create_rectangle(130, 30, 145, 45, fill='#2ecc71')
        self.canvas.create_text(152, 38, text='Door Open', fill='white', font=('Arial', 8), anchor='w')
    
    def add_person(self):
        src = random.randint(1, 40)
        dst = random.randint(1, 40)
        while dst == src:
            dst = random.randint(1, 40)
        
        p = Person(len(self.b.waiting[src])+1, src, dst)
        self.b.waiting[src].append(p)
        
        # Assign the request to an elevator
        if self.ctrl.assign_request(p):
            messagebox.showinfo('Info', f'Passenger from floor {src} to {dst} assigned')
        else:
            messagebox.showwarning('Warning', f'No elevator available for floor {src} to {dst}')
        
        self.draw()
    
    def step(self):
        if not self.running:
            return
        
        # Increase waiting time
        for fl in self.b.waiting.values():
            for p in fl:
                p.wait += 0.5
        for e in self.b.elevators:
            for p in e.passengers:
                p.wait += 0.5
        
        self.ctrl.step()
        self.draw()
        
        avg = 0
        if self.b.served:
            avg = self.b.total_wait / self.b.served
        self.stats.config(text=f'Served: {self.b.served} | Avg Wait: {avg:.1f} sec')
        
        self.root.after(self.speed, self.step)
    
    def start(self):
        if not self.running:
            self.running = True
            self.step()
    
    def stop(self):
        self.running = False
    
    def reset(self):
        self.running = False
        self.b = Building()
        self.ctrl = Controller(self.b)
        self.draw()
        self.stats.config(text='Served: 0 | Avg Wait: 0.0 sec')

# ==================== Run ====================

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()