import pygame, math, random

WIDTH,HEIGHT=800,500
pygame.init()
screen=pygame.display.set_mode((WIDTH,HEIGHT))
clock=pygame.time.Clock()

class Cart:
    def __init__(self):
        self.x=WIDTH//2
        self.v=0

class Pendulum:
    def __init__(self):
        self.length=140
        self.angle=0.15
        self.omega=0
    def update(self,force):
        g=9.81
        dt=0.02
        self.omega += (-g/self.length*math.sin(self.angle)+force*0.002)*dt
        self.angle += self.omega*dt

class Controller:
    def control(self,angle):
        noisy=angle+random.uniform(-0.01,0.01)
        return -300*noisy

cart=Cart()
pend=Pendulum()
ctrl=Controller()

running=True
auto=True
while running:
    for e in pygame.event.get():
        if e.type==pygame.QUIT: running=False
        if e.type==pygame.KEYDOWN and e.key==pygame.K_SPACE:
            auto=not auto
    keys=pygame.key.get_pressed()
    force=0
    if auto:
        force=ctrl.control(pend.angle)
    else:
        if keys[pygame.K_LEFT]: force=-80
        if keys[pygame.K_RIGHT]: force=80
    cart.x+=force*0.02
    pend.update(force)

    screen.fill((240,240,240))
    pygame.draw.line(screen,(0,0,0),(0,350),(800,350),2)
    pygame.draw.rect(screen,(50,120,220),(cart.x-40,320,80,30))
    px=cart.x+pend.length*math.sin(pend.angle)
    py=320-pend.length*math.cos(pend.angle)
    pygame.draw.line(screen,(200,0,0),(cart.x,320),(px,py),4)
    pygame.draw.circle(screen,(0,0,0),(int(px),int(py)),10)
    pygame.display.flip()
    clock.tick(50)
pygame.quit()
