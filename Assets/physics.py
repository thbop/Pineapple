import pygame
from random import uniform, randint


class Particle:
    def __init__(self, rect, vel, color):
        self.rect = rect
        self.vel = vel
        self.color = color

class Physics:
    def __init__(self, gm):
        self.gm = gm

        self.gravity = .2
        self.winds = []

        self.fparticles = []
        self.bparticles = []
    
    def add_p(self, rect, vel, color, front=True):
        if front:
            self.fparticles.append( Particle(rect, vel, color) )
        else:
            self.bparticles.append( Particle(rect, vel, color) )
    
    def emitter(self, pos, size_range, max_vel, color, max_color_mult, speed):
        if self.gm.tick % speed == 0:
            size = randint(size_range[0], size_range[1])
            rect = pygame.Rect(pos[0], pos[1], size, size)

            vel = [ uniform(-max_vel, max_vel), uniform(-max_vel, max_vel) ]

            color_mult = randint(1, max_color_mult)
            ncolor = []
            for v in color:
                ncolor.append(v*color_mult)
            
            self.add_p(rect, vel, ncolor)
    
    def add_emitter(self, pos, size_range, max_vel, color, max_color_mult, speed):
        self.gm.world.emitters.append([pos, size_range, max_vel, color, max_color_mult, speed])
    
    def run(self, particles, additive=False):
        for e in self.gm.world.emitters:
            self.emitter(e[0], e[1], e[2], e[3], e[4], e[5])
        for p in particles:
            p.vel[1] += self.gravity
            for w in self.winds:
                p.vel[0] += w[0]
                p.vel[1] += w[1]
            
            p.rect.x += p.vel[0]
            p.rect.y += p.vel[1]

            if p.rect.x < -10 or p.rect.x > len(self.gm.world.world[0])*5+10 or p.rect.y < -10 or p.rect.y > len(self.gm.world.world)*5+10:
                particles.remove(p)

            if additive:
                surf = pygame.Surface(p.rect.size)
                surf.fill(p.color)
                self.gm.screen.blit(surf, [p.rect.x-self.gm.camera.x, p.rect.y-self.gm.camera.y], special_flags=pygame.BLEND_ADD)

            else:
                pygame.draw.rect(self.gm.screen, p.color, [p.rect.x-self.gm.camera.x, p.rect.y-self.gm.camera.y, p.rect.width, p.rect.height], 0)
        return particles