import pygame


class Grade:
    def __init__(self, color, tex, blend):
        self.color = color
        self.tex = tex
        self.blend = blend
        if self.color == None and self.tex == None:
            self.color = (0, 0, 0)
        if self.tex == None:
            self.surf = pygame.Surface((128, 128))
            self.surf.fill(self.color)
        else:
            self.surf = pygame.image.load(self.tex)

class Grades:
    def __init__(self, gm):
        self.gm = gm

        self.grades = []
    
    def add(self, color=None, tex=None, blend=pygame.BLEND_ADD):
        self.grades.append(Grade(color, tex, blend))
    

    def run(self):
        for g in self.grades:
            self.gm.screen.blit(g.surf, (0, 0), special_flags=g.blend)


class Light:
    def __init__(self, size, color):
        self.size = size
        self.rad = round(self.size/2)-1
        self.color = color
        self.surf = pygame.Surface((self.size, self.size))
        pygame.gfxdraw.aacircle(
            self.surf,
            self.rad, self.rad,
            self.rad,
            self.color
            )
        pygame.gfxdraw.filled_circle(
            self.surf,
            self.rad, self.rad,
            self.rad,
            self.color
            )
        self.rect = self.surf.get_rect()
