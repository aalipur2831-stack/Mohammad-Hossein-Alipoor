import tkinter as tk
from tkinter import messagebox
import random
from collections import deque
import time

# ==================== Car Class ====================

class Car:
    def __init__(self, cid, direction):
        self.id = cid
        self.direction = direction  # 'N', 'S', 'E', 'W'
        self.wait_time = 0
        self.passed = False

# ==================== Traffic Light Class ====================

class TrafficLight:
    def __init__(self, direction):
        self.direction = direction
        self.state = 'red'  # 'red', 'green', 'yellow'
        self.timer = 0
    
    def change_state(self, state):
        self.state = state
        if state == 'green':
            self.timer = 10  # 10 seconds green
        elif state == 'yellow':
            self.timer = 3   # 3 seconds yellow
        else:
            self.timer = 0   # red
    
    def tick(self):
        if self.timer > 0:
            self.timer -= 1
            if self.timer == 0 and self.state == 'green':
                self.change_state('yellow')
            elif self.timer == 0 and self.state == 'yellow':
                self.change_state('red')
        return self.state

# ==================== Lane Class ====================

class Lane:
    def __init__(self, direction):
        self.direction = direction
        self.queue = deque()
        self.passed_count = 0
    
    def add_car(self, car):
        self.queue.append(car)
    
    def get_waiting_count(self):
        return len(self.queue)
    
    def release_cars(self, count=3):
        released = []
        for _ in range(min(count, len(self.queue))):
            car = self.queue.popleft()
            car.passed = True
            self.passed_count += 1
            released.append(car)
        return released

# ==================== Intersection Class ====================

class Intersection:
    def __init__(self):
        self.lanes = {
            'N': Lane('N'),
            'S': Lane('S'),
            'E': Lane('E'),
            'W': Lane('W')
        }
        self.lights = {
            'N': TrafficLight('N'),
            'S': TrafficLight('S'),
            'E': TrafficLight('E'),
            'W': TrafficLight('W')
        }
        self.total_cars = 0
        self.total_wait = 0
        self.current_green = None
        self.phase = 0  # 0: NS, 1: EW
    
    def add_car(self, direction):
        car = Car(self.total_cars + 1, direction)
        self.lanes[direction].add_car(car)
        self.total_cars += 1
        return car
    
    def get_stats(self):
        avg_wait = 0
        if self.total_cars > 0:
            avg_wait = self.total_wait / self.total_cars
        return {
            'total': self.total_cars,
            'avg_wait': avg_wait,
            'waiting': sum(lane.get_waiting_count() for lane in self.lanes.values())
        }

# ==================== Smart Controller ====================

class Controller:
    def __init__(self, intersection):
        self.intersection = intersection
        self.cycle_time = 0
        self.phase_time = 10  # seconds for each phase
    
    def update(self):
        inter = self.intersection
        
        # Calculate waiting cars in each direction
        n_wait = inter.lanes['N'].get_waiting_count() + inter.lanes['S'].get_waiting_count()
        e_wait = inter.lanes['E'].get_waiting_count() + inter.lanes['W'].get_waiting_count()
        
        # Adaptive algorithm: phase with more cars gets priority
        self.cycle_time += 1
        
        if self.cycle_time >= self.phase_time:
            if n_wait > e_wait:
                self.set_green('NS')
            elif e_wait > n_wait:
                self.set_green('EW')
            else:
                # If equal, alternate
                if inter.current_green == 'NS':
                    self.set_green('EW')
                else:
                    self.set_green('NS')
            self.cycle_time = 0
        
        # Tick lights
        for light in inter.lights.values():
            light.tick()
        
        # If light is green, release cars
        if inter.current_green == 'NS':
            self.release_cars(['N', 'S'])
        elif inter.current_green == 'EW':
            self.release_cars(['E', 'W'])
    
    def set_green(self, phase):
        inter = self.intersection
        inter.current_green = phase
        
        if phase == 'NS':
            inter.lights['N'].change_state('green')
            inter.lights['S'].change_state('green')
            inter.lights['E'].change_state('red')
            inter.lights['W'].change_state('red')
        else:  # EW
            inter.lights['E'].change_state('green')
            inter.lights['W'].change_state('green')
            inter.lights['N'].change_state('red')
            inter.lights['S'].change_state('red')
    
    def release_cars(self, directions):
        inter = self.intersection
        for direction in directions:
            lane = inter.lanes[direction]
            if lane.get_waiting_count() > 0:
                # 2 cars pass per tick
                released = lane.release_cars(2)
                for car in released:
                    inter.total_wait += car.wait_time

# ==================== GUI ====================

class App:
    def __init__(self, root):
        self.root = root
        root.title("Smart Traffic Light Simulator")
        root.geometry("750x650")
        root.configure(bg='#2c3e50')
        
        self.intersection = Intersection()
        self.controller = Controller(self.intersection)
        self.running = False
        self.speed = 300  # milliseconds
        
        self.setup_ui()
        self.draw()
    
    def setup_ui(self):
        # Top panel
        top = tk.Frame(self.root, bg='#34495e')
        top.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(top, text="▶ Start", command=self.start,
                 bg='#27ae60', fg='white', font=('Arial', 10, 'bold'), width=8).pack(side=tk.LEFT, padx=3)
        tk.Button(top, text="⏸ Stop", command=self.stop,
                 bg='#e67e22', fg='white', font=('Arial', 10, 'bold'), width=8).pack(side=tk.LEFT, padx=3)
        tk.Button(top, text="🔄 Reset", command=self.reset,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'), width=8).pack(side=tk.LEFT, padx=3)
        
        # Add car buttons
        for dir_name, dir_emoji in [('N', '⬆'), ('S', '⬇'), ('E', '➡'), ('W', '⬅')]:
            tk.Button(top, text=f"{dir_emoji} {dir_name}", 
                     command=lambda d=dir_name: self.add_car(d),
                     bg='#3498db', fg='white', font=('Arial', 9, 'bold'), width=5).pack(side=tk.LEFT, padx=2)
        
        # Stats
        self.stats = tk.Label(top, text="Cars: 0 | Waiting: 0 | Avg Wait: 0.0 sec",
                             bg='#34495e', fg='#ffd93d', font=('Arial', 9))
        self.stats.pack(side=tk.RIGHT, padx=5)
        
        # Canvas
        self.canvas = tk.Canvas(self.root, bg='#2c3e50', width=730, height=530)
        self.canvas.pack(pady=5)
    
    def draw(self):
        self.canvas.delete('all')
        cx, cy = 365, 265  # intersection center
        size = 150
        
        # Draw roads
        # North-South road
        self.canvas.create_rectangle(cx-30, cy-size, cx+30, cy+size, fill='#555', outline='')
        # East-West road
        self.canvas.create_rectangle(cx-size, cy-30, cx+size, cy+30, fill='#555', outline='')
        # Intersection
        self.canvas.create_rectangle(cx-30, cy-30, cx+30, cy+30, fill='#444', outline='white')
        
        # Draw center lines
        for i in range(-size+20, size-20, 30):
            if i != 0:
                # North line
                self.canvas.create_line(cx, cy-i, cx, cy-i+15, fill='white', dash=(5,5))
                # South line
                self.canvas.create_line(cx, cy+i, cx, cy+i-15, fill='white', dash=(5,5))
                # East line
                self.canvas.create_line(cx+i, cy, cx+i-15, cy, fill='white', dash=(5,5))
                # West line
                self.canvas.create_line(cx-i, cy, cx-i+15, cy, fill='white', dash=(5,5))
        
        # Draw traffic lights
        light_positions = {
            'N': (cx-20, cy-size+20),
            'S': (cx+20, cy+size-20),
            'E': (cx+size-20, cy-20),
            'W': (cx-size+20, cy+20)
        }
        
        colors = {'red': '#e74c3c', 'green': '#2ecc71', 'yellow': '#f1c40f'}
        
        for dir_name, (x, y) in light_positions.items():
            light = self.intersection.lights[dir_name]
            color = colors.get(light.state, '#e74c3c')
            
            # Light circle
            self.canvas.create_oval(x-12, y-12, x+12, y+12, fill=color, outline='white', width=2)
            # Direction text
            self.canvas.create_text(x, y+25, text=dir_name, fill='white', font=('Arial', 8, 'bold'))
            
            # Waiting cars count in this lane
            count = self.intersection.lanes[dir_name].get_waiting_count()
            if count > 0:
                if dir_name == 'N':
                    self.canvas.create_text(x-30, y, text=f'🚗{count}', fill='#ff6b6b', font=('Arial', 9, 'bold'))
                elif dir_name == 'S':
                    self.canvas.create_text(x+30, y, text=f'🚗{count}', fill='#ff6b6b', font=('Arial', 9, 'bold'))
                elif dir_name == 'E':
                    self.canvas.create_text(x, y+30, text=f'🚗{count}', fill='#ff6b6b', font=('Arial', 9, 'bold'))
                else:  # W
                    self.canvas.create_text(x, y-30, text=f'🚗{count}', fill='#ff6b6b', font=('Arial', 9, 'bold'))
        
        # Green light status (show allowed directions)
        green_dirs = []
        for dir_name, light in self.intersection.lights.items():
            if light.state == 'green':
                green_dirs.append(dir_name)
        
        if green_dirs:
            self.canvas.create_text(cx, cy+70, text=f'🟢 {",".join(green_dirs)} allowed', 
                                   fill='#2ecc71', font=('Arial', 11, 'bold'))
        else:
            self.canvas.create_text(cx, cy+70, text='🔴 All stop', 
                                   fill='#e74c3c', font=('Arial', 11, 'bold'))
        
        # Legend
        self.canvas.create_text(20, 20, text='📖 Legend:', fill='white', font=('Arial', 9, 'bold'), anchor='w')
        self.canvas.create_oval(20, 30, 35, 45, fill='#2ecc71')
        self.canvas.create_text(42, 38, text='Green: Go', fill='white', font=('Arial', 8), anchor='w')
        self.canvas.create_oval(120, 30, 135, 45, fill='#f1c40f')
        self.canvas.create_text(142, 38, text='Yellow: Prepare', fill='white', font=('Arial', 8), anchor='w')
        self.canvas.create_oval(220, 30, 235, 45, fill='#e74c3c')
        self.canvas.create_text(242, 38, text='Red: Stop', fill='white', font=('Arial', 8), anchor='w')
    
    def add_car(self, direction):
        car = self.intersection.add_car(direction)
        messagebox.showinfo('New Car', f'Car entered from direction {direction}')
        self.update_stats()
    
    def update_stats(self):
        stats = self.intersection.get_stats()
        self.stats.config(
            text=f'Cars: {stats["total"]} | Waiting: {stats["waiting"]} | Avg Wait: {stats["avg_wait"]:.1f} sec'
        )
    
    def step(self):
        if not self.running:
            return
        
        # Increase waiting time for cars
        for lane in self.intersection.lanes.values():
            for car in lane.queue:
                car.wait_time += 0.3
        
        # Run controller
        self.controller.update()
        
        # Update display
        self.draw()
        self.update_stats()
        
        # Next step
        self.root.after(self.speed, self.step)
    
    def start(self):
        if not self.running:
            self.running = True
            self.step()
    
    def stop(self):
        self.running = False
    
    def reset(self):
        self.running = False
        self.intersection = Intersection()
        self.controller = Controller(self.intersection)
        self.draw()
        self.update_stats()

# ==================== Run ====================

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()