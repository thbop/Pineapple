import pygame


class Entity:
    def __init__(self, gm):
        self.gm = gm

        self.rect = pygame.Rect(100, 100, 5, 5)
        self.id = '0'
        self.aniB = True
        self.ss = None
        self.ani = {'None':[pygame.Surface(self.rect.size)]}
        self.ani_state = ['None', 0, False]
        self.ani_speed = 10

        self.other = {}
    
    def run(self):
        render_pos = (self.rect.x-self.gm.camera.x, self.rect.y-self.gm.camera.y)
        rsurf = None
        if render_pos[0] < -10 or render_pos[0] > self.gm.res+10 or render_pos[1] < -10 or render_pos[1] > self.gm.res+10:
            pass
        else:
            if self.aniB:
                if self.gm.tick % self.ani_speed == 0:
                    if self.ani_state[1] == len(self.ani[self.ani_state[0]]) - 1:
                        self.ani_state[1] = 0
                    else:
                        self.ani_state[1] += 1
                
                rsurf = pygame.transform.flip(self.ani[self.ani_state[0]][self.ani_state[1]], self.ani_state[2], False)
            else:
                if self.gm.world.edefs[int(self.id)] == None:
                    pass
                elif self.id == '1' and not self.gm.editor: pass
                elif self.id == '5' and not self.gm.editor: pass
                else:
                    rsurf = self.gm.world.edefs[int(self.id)]
        if rsurf != None:
            # pygame.draw.rect(self.gm.screen, (255, 0, 0), [render_pos[0], render_pos[1], self.rect.width, self.rect.height], 1)
            self.gm.screen.blit(rsurf, render_pos)
            
            return rsurf