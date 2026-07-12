import pygame
import pygame.gfxdraw
import tkinter
import tkinter.filedialog, tkinter.simpledialog
import os
import json

from Assets.spritesheet import spritesheet
from Assets.world import *

class Gui:
    def __init__(self, le):
        self.le = le
        self.ss = spritesheet('Assets/Graphics/gui.png')


        key = (255, 255, 255)
        self.icons = {
            'rectangle-brush':self.ss.image_at([0, 0, 5, 5], key),
            'brush':self.ss.image_at([5, 0, 5, 5], key),
            'save':self.ss.image_at([10, 0, 5, 5], key),
            'open':self.ss.image_at([15, 0, 5, 5], key),
            'new':self.ss.image_at([20, 0, 5, 5], key),
            'entity':self.ss.image_at([25, 0, 5, 5], key)
        }

        self.air = pygame.Surface((5, 5))
        pygame.draw.rect(self.air, (255, 255, 255), [0, 0, 5, 5], 1)

        self.colors = {
            'bg':(20, 20, 20),
            'bg2':(35, 35, 35),
            'hover':(120, 120, 120),
            'selected':(103, 149, 150),
            'selected-hover':(72, 246, 249)
        }

        self.panels = [
            pygame.Rect(0, 0, 7, self.le.res),
            pygame.Rect(self.le.res-7, 0, 7, self.le.res),
            pygame.Rect(0, 0, self.le.res, 7)
        ]
        self.active_tool = 'brush'
        self.active_brush = 0
        self.click = False
    
    def button(self, icon, pos, tool=False, brush=False):
        self.le.screen.blit(icon, pos)
        rect = icon.get_rect()
        rect.x = pos[0]-1
        rect.y = pos[1]-1
        rect.width += 2
        rect.height += 2
        if tool == self.active_tool:
            pygame.draw.rect(self.le.screen, self.colors['selected'], rect, 1)
        if str(brush) == str(self.active_brush):
            pygame.draw.rect(self.le.screen, self.colors['selected'], rect, 1)

        if rect.collidepoint(self.mouse[0], self.mouse[1]):
            if pygame.mouse.get_pressed()[0]:
                pygame.draw.rect(self.le.screen, self.colors['selected-hover'], rect, 1)
                if tool != False:
                    self.active_tool = tool
                    self.active_brush = 0
                if str(brush) != 'False':
                    self.active_brush = brush
                return True
            else:
                pygame.draw.rect(self.le.screen, self.colors['hover'], rect, 1)
                return False
    
    def prompt_file(self):
        """
        Copied from https://stackoverflow.com/questions/63801960/how-to-prompt-user-to-open-a-file-with-python3
        Create a Tk file dialog and cleanup when finished
        """
        top = tkinter.Tk()
        top.withdraw()  # hide window
        file_name = tkinter.filedialog.askopenfilename(parent=top, initialdir=os.getcwd() + '\\Assets\\Worlds')
        top.destroy()
        return file_name
    
    def prompt_string(self, title, prompt):
        top = tkinter.Tk()
        top.withdraw()  # hide window
        string = tkinter.simpledialog.askstring(parent=top, title=title, prompt=prompt)
        top.destroy()
        return string
        

    
    def run(self):
        self.mouse = pygame.mouse.get_pos()
        self.mouse = (
            round(self.mouse[0]/self.le.win_scale),
            round(self.mouse[1]/self.le.win_scale)
            )
        self.collide_with_gui = False
        for p in self.panels:
            if p.collidepoint(self.mouse[0], self.mouse[1]):
                self.collide_with_gui = True
        

        pygame.draw.rect(self.le.screen, self.colors['bg2'], self.panels[0],0)
        pygame.draw.rect(self.le.screen, self.colors['bg2'], self.panels[1],0)
        pygame.draw.rect(self.le.screen, self.colors['bg'], self.panels[2],0)

        if self.button(self.icons['save'], (1, 1)) and not self.click:
            self.le.world.save()
            self.click = True
        
        elif self.button(self.icons['open'], (7, 1)) and not self.click:
            room = self.prompt_file()
            if room != '':
                room = os.path.basename(os.path.normpath(room)).rstrip('.txt')
                self.le.world.current_room = room
                self.le.editor_data['current-room'] = room
                self.le.world.load(self.le.world.world_name)

            self.click = True
        
        elif self.button(self.icons['new'], (13, 1)) and not self.click:
            data = self.prompt_string('New Level', 'id:w:h')
            if data != None:
                room = data[:data.find(':')]
                data = data[data.find(':'):].lstrip(':')
                size = (int(data[:data.find(':')]), int(data[data.find(':'):].lstrip(':')))

                t = ''
                for y in range(size[1]):
                    t += '0'*size[0] + '\n'
                
                file = open(f'Assets/Worlds/{self.le.world.world_name}/{room}.txt', 'w')
                file.write(t)
                file.close()
                self.le.world.current_room = room
                self.le.editor_data['current-room'] = room
                self.le.world.load(self.le.world.world_name)


            self.click = True

        elif not pygame.mouse.get_pressed()[0]:
            self.click = False

        self.button(self.icons['brush'], (1, 8), 'brush')
        self.button(self.icons['rectangle-brush'], (1, 15), 'rectangle-brush')
        self.button(self.icons['entity'], (1, 22), 'entity')

        if self.active_tool != 'entity':
            i = 0
            for b in self.le.world.tdefs:
                if b == None:
                    self.button(self.air, (self.le.res-6, 8), brush=i)
                else:
                    self.button(b['[0, 0, 0, 0]'], (self.le.res-6, 7*i+8), brush=i)
                i += 1
        else:
            i = 0
            for b in self.le.world.edefs:
                if b == None:
                    self.button(self.air, (self.le.res-6, 8), brush=i)
                else:
                    if isinstance(b, list):
                        b = b[0]
                    self.button(b, (self.le.res-6, 7*i+8), brush=i)
                i += 1
        

        

class LevelEditor:
    def __init__(self):

        pygame.init()

        self.win_scale = 8
        self.res = 128
        self.window = pygame.display.set_mode((self.res*self.win_scale, self.res*self.win_scale))
        self.screen = pygame.Surface((self.res, self.res))
        pygame.mouse.set_visible(False)

        self.editor = True

        self.world = World(self)
        self.editor_data = json.load(open('Assets/editor.json'))
        self.world.current_room = self.editor_data['current-room']
        self.world.load(self.editor_data['current-world'])

        self.gui = Gui(self)

        self.rect_painting = [False]

        self.ftiles_visible = True

        self.tick = 0



    def qbin(self, v):
        if v == '0':
            return 0
        else:
            return 1
        
    def draw_tiles(self, world):
        y = 0
        for row in world:
            x = 0
            for col in row:
                render_pos = ((x*5) - self.camera.x, (y*5) - self.camera.y)
                if render_pos[0] < -5 or render_pos[0] > self.res+5 or render_pos[1] < -5 or render_pos[1] > self.res+5:
                    pass
                else:
                    sprite_row = self.world.tdefs[int(col)]
                    if sprite_row != None:
                        other = [
                        self.qbin(world[y][x-1]),
                        self.qbin(world[y-1][x]),
                        self.qbin(world[y][x+1]),
                        self.qbin(world[y+1][x]),
                        ]
                        self.screen.blit(sprite_row[str(other)], render_pos)
                x += 1
            y += 1
    
    def draw_btiles(self, world):
        y = 0
        for row in world:
            x = 0
            for col in row:
                render_pos = ((x*5) - self.camera.x, (y*5) - self.camera.y)
                if render_pos[0] < -5 or render_pos[0] > self.res+5 or render_pos[1] < -5 or render_pos[1] > self.res+5:
                    pass
                else:
                    if world[y][x] != '0':
                        self.screen.blit(self.world.tdefs[int(self.world.worldb[y][x])]['bg'], ((x*5) - self.camera.x, (y*5) - self.camera.y))

                x += 1
            y += 1

    def draw_entities(self, entities):
        for e in entities:
            e.run()
    

    def paint_entity(self):
        if self.gui.active_brush == 0:
            self.screen.blit(self.gui.air, self.hover_tile.topleft)
        else:
            b = self.world.edefs[self.gui.active_brush]
            if isinstance(b, list):
                b = b[0]
            self.screen.blit(b, self.hover_tile.topleft)
        
        if pygame.mouse.get_pressed()[0]:
            rect = pygame.Rect(self.global_pos[0]*5, self.global_pos[1]*5, 5, 5)
            paint = True
            for e in self.world.entities:
                if rect.topleft == e.rect.topleft:
                    paint = False
                    if self.gui.active_brush == 0:
                        self.world.entities.remove(e)
            if paint:
                self.world.add_entity(str(self.gui.active_brush), rect)
    
    def paint(self):
        if self.gui.active_brush == 0:
            self.screen.blit(self.gui.air, self.hover_tile.topleft)
        else:
            self.screen.blit(self.world.tdefs[self.gui.active_brush]['[0, 0, 0, 0]'], self.hover_tile.topleft)
        

        if pygame.mouse.get_pressed()[0]:
            self.world.set_tile(self.global_pos, str(self.gui.active_brush))
        elif pygame.mouse.get_pressed()[2]:
            self.world.set_tile(self.global_pos, str(self.gui.active_brush), True)
    
    def rect_paint(self):
        if self.gui.active_brush == 0:
            self.screen.blit(self.gui.air, self.hover_tile.topleft)
        else:
            self.screen.blit(self.world.tdefs[self.gui.active_brush]['[0, 0, 0, 0]'], self.hover_tile.topleft)
        

        if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
            if not self.rect_painting[0]:
                self.rect_painting[0] = True
                self.rect_painting.append(self.hover_tile)
                self.rect_painting.append(self.global_pos)
                self.rect_painting.append(pygame.mouse.get_pressed()[2])
            else:
                pygame.draw.rect(self.screen, (0, 255, 0), [
                    self.rect_painting[1][0],
                    self.rect_painting[1][1],
                    self.hover_tile[0]-self.rect_painting[1][0]+5,
                    self.hover_tile[1]-self.rect_painting[1][1]+5
                ],1)
        elif self.rect_painting[0]:
            for y in range(self.global_pos[1] - self.rect_painting[2][1]+1):
                for x in range(self.global_pos[0] - self.rect_painting[2][0]+1):
                    self.world.set_tile((
                        x + self.rect_painting[2][0],
                        y + self.rect_painting[2][1]
                    ), str(self.gui.active_brush),
                    self.rect_painting[3])

            self.rect_painting = [False]


    def run(self):

        clock = pygame.time.Clock()
        running = True

        self.camera = pygame.Rect(0, 0, self.res, self.res)

        self.cam_speed = 1


        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    ed = open('Assets/editor.json', 'w')
                    ed.write(json.dumps(self.editor_data))
                    ed.close()
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_h:
                        self.ftiles_visible = not self.ftiles_visible
                
            keys = pygame.key.get_pressed()
            if keys[pygame.K_d]:
                self.camera.x += self.cam_speed
            if keys[pygame.K_a]:
                self.camera.x -= self.cam_speed
            if keys[pygame.K_s]:
                self.camera.y += self.cam_speed
            if keys[pygame.K_w]:
                self.camera.y -= self.cam_speed
            if keys[pygame.K_LSHIFT]:
                self.cam_speed = 3
            else:
                self.cam_speed = 1
            
            

            self.screen.fill((0, 0, 0))

            self.draw_btiles(self.world.worldb)
            if self.ftiles_visible:
                self.draw_tiles(self.world.world)
            self.draw_entities(self.world.entities)
            pygame.draw.rect(self.screen, (255, 255, 255), [-self.camera.x, -self.camera.y, len(self.world.world[0])*5-5, len(self.world.world)*5-5],1)


            

            self.gui.run()
            self.hover_tile = pygame.Rect(
            round((self.gui.mouse[0]+self.camera.x)/5)*5-self.camera.x,
            round((self.gui.mouse[1]+self.camera.y)/5)*5-self.camera.y,
            5,
            5
            )
            self.global_pos = [
            round((self.gui.mouse[0]+self.camera.x)/5),
            round((self.gui.mouse[1]+self.camera.y)/5)
            ]
            if not self.gui.collide_with_gui:
                if self.gui.active_tool == 'brush':
                    self.paint()
                elif self.gui.active_tool == 'rectangle-brush':
                    self.rect_paint()
                elif self.gui.active_tool == 'entity':
                    self.paint_entity()

            m = pygame.mouse.get_pos()
            pygame.gfxdraw.pixel(self.screen,
                                round(m[0]/self.win_scale),
                                round(m[1]/self.win_scale),
                                (170, 0, 255)
                                )
            if self.tick > 60:
                self.tick = 1
            else:
                self.tick += 1
            clock.tick(60)
            self.window.blit(
                pygame.transform.scale(self.screen, (self.res*self.win_scale, self.res*self.win_scale)),
                (0, 0)
                )
            pygame.display.flip()

if __name__ == '__main__':
    le = LevelEditor()
    le.run()