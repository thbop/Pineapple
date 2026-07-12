#Imports
import pygame
import pygame.gfxdraw
from random import randint

from Assets.world import *
from Assets.player import *
from Assets.physics import *
from Assets.entity import *
from Assets.audio import Audio
from Assets.misc import *



class Game:
    def __init__(self):
        """The main game class. This runs the game"""

        pygame.init()
        pygame.mouse.set_visible(False)
        pygame.display.set_caption('Pineapple')
        icon = pygame.image.load('Assets/Graphics/icon.png')
        pygame.display.set_icon(icon)

        self.win_scale = 8
        self.res = 128
        self.window = pygame.display.set_mode((self.res*self.win_scale, self.res*self.win_scale))
        self.screen = pygame.Surface((self.res, self.res))
        
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        pygame.mixer.init()

        self.audio = Audio()

        # sets editor = False because some files must draw a distiction like respawn entity blit
        self.editor = False

        self.phys = Physics(self)
        self.phys.winds.append((0.02, -.15))

        self.world = World(self)
        # self.world.current_room = '4'
        # self.world.load(self.world.world_name)

        self.grades = Grades(self)
        # Manual grade loading
        # self.grades.add(color=(33, 21, 21), blend=pygame.BLEND_SUB)
        # self.grades.add(tex='Assets/Graphics/Grades/magical.png', blend=pygame.BLEND_ADD)

        # Loads grades from world.json
        self._load_grades()

        self.player = Player(self)
        self.camera = pygame.Rect(5, 5, self.res, self.res)

        # Used for driving animation
        self.tick = 1
    
        self.text_ss = spritesheet('Assets/Graphics/text.png')

        self.cs_circle = pygame.Surface((self.res, self.res))
        self.cs_circle.set_colorkey((255, 255, 255))

        self.cs_circle_size = 0
        self.cs_circle_timer = 0

        self.ending_level = False
        self.beginning_level = True
        self.to_next_level = False

        self.end = False
        self.end_m = 'Thank you so much for playing! '
        self.end_mani = ['', 0]

        self.musicc = [0, 0]


    def Text(self, text, pos=[0, 0], blit=True):
        chars = 'abcdefghijklmnopqrstuvwxyz1234567890.,:;!?/ '
        text = text.lower()
        width = 1
        width *= len(text)*4
        surf = pygame.Surface((width, 5))
        surf.fill((255, 255, 255))
        surf.set_colorkey((255, 255, 255))
        i = 0
        for c in text:
            surf.blit(
                self.text_ss.image_at([ chars.find(c)*3, 0, 3, 5 ], (255, 255, 255)),
                (i, 0)
                )
            i += 4
        if blit:
            self.screen.blit(surf, pos)
        else:
            return surf

    def _load_grades(self):
        for g in self.world.properties['world']['grades']:
            if g['blend'] == 'add':
                blend = pygame.BLEND_ADD
            elif g['blend'] == 'sub':
                blend = pygame.BLEND_SUB
            elif g['blend'] == 'mult':
                blend = pygame.BLEND_MULT
            self.grades.add(color=g['color'], tex=g['tex'], blend=blend)
    

    def _level_trans(self):
        # print(self.cs_circle_timer, self.cs_circle_size)
        if self.ending_level:
            if self.cs_circle_size == 10:
                self.cs_circle_size = 10
                self.cs_circle_timer += 1
            else:
                self.cs_circle_size -= 5
            if self.cs_circle_timer > 60:
                self.cs_circle_size -= 1
            
            if self.cs_circle_size < 0:
                self.cs_circle_size = 0
                self.cs_circle_timer = 0

                self.ending_level = False
        elif self.beginning_level:
            if self.cs_circle_size == 10:
                self.cs_circle_size = 10
                self.cs_circle_timer += 1
            else:
                self.cs_circle_size += 5
            if self.cs_circle_timer > 60:
                self.cs_circle_size += 1
            
            if self.cs_circle_size > 128:
                self.cs_circle_size = 100
                self.cs_circle_timer = 0

                self.beginning_level = False

        if self.beginning_level or self.ending_level or self.to_next_level:
            self.cs_circle.fill((0, 0, 0))
            pygame.draw.circle(self.cs_circle, (255, 255, 255), (self.player.rect.centerx-self.camera.x, self.player.rect.centery-self.camera.y), self.cs_circle_size)
            self.screen.blit(self.cs_circle, (0, 0))

    def _end(self):
        if self.end:
            self.screen.fill((0, 0, 0))
            self.Text(self.end_mani[0], pos=[64-(self.end_mani[1]*2), 50])

            if self.tick % 5 == 0 and self.end_mani[1] < len(self.end_m)-1:
                self.end_mani[0] += self.end_m[self.end_mani[1]]
                self.end_mani[1] += 1

        
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
        """Draws background tiles"""
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
    
    def draw_lights(self, lights):
        for l in lights:
            self.screen.blit(l.surf, [l.rect.x-self.camera.x, l.rect.y-self.camera.y], special_flags=pygame.BLEND_ADD)
    
    def _draw_tile_rects(self, tiles):
        """Not used function. Collision tiles are stored as a list of rects for ease, this displays that list"""
        for t in tiles:
            pygame.draw.rect(self.screen, (255, 0, 0), [t.x - self.camera.x, t.y - self.camera.y, t.width, t.height], 1)
    

    def _generate_rain(self):
        for i in range(2):
                yvel = randint(2, 4)
                if i == 1:
                    self.phys.add_p(
                        pygame.Rect(randint(-10, len(self.world.world[0])*5+10), -5, 1, yvel),
                        [0, yvel/1.5],
                        (8, 40, 53)
                        )
                else:
                    self.phys.add_p(
                        pygame.Rect(randint(-10, len(self.world.world[0])*5+10), -5, 1, yvel),
                        [0, yvel/2],
                        '#2474ad',
                        False
                        )




    def run(self):

        clock = pygame.time.Clock()
        running = True



        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.player.jump()
                
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        self.player.jump()
                if event.type == pygame.JOYAXISMOTION:
                    if event.instance_id == 0 and event.axis == 0:
                        self.player.joy_movementx = round(event.value)

            if not self.end:
                self.camera.x += (self.player.rect.x-self.camera.x-48)/20
                self.camera.y += (self.player.rect.y-self.camera.y-48)/20
                
                # Camera world clamping
                if self.camera.left < 5:
                    self.camera.x = 5
                if self.camera.top < 5:
                    self.camera.y = 5
                if self.camera.right > len(self.world.world[0])*5-10:
                    self.camera.right = len(self.world.world[0])*5-10
                if self.camera.bottom > len(self.world.world)*5-10:
                    self.camera.bottom = len(self.world.world)*5-10

                self.screen.fill(self.world.properties['world']['sky'])
                # Draws the background particles
                self.phys.bparticles = self.phys.run(self.phys.bparticles)

                # Draws the background tiles
                self.draw_btiles(self.world.worldb)

                # Draws the lights together so that they can blit add each other
                self.player.run_light()
                self.draw_lights(self.world.lights)

                self.draw_tiles(self.world.world)
                self.draw_entities(self.world.entities)

                self.player.run()

                # Shows the stats on pineapple collection
                self.Text(f"{self.player.pineapples}/{self.world.properties['rooms'][self.world.current_room]['pineapples']}", [3, 3])
                
                # Using world.json, decides whether rain should be displayed
                if self.world.properties['world']['weather'] == 'rain':
                    self._generate_rain()
                self.phys.fparticles = self.phys.run(self.phys.fparticles, True)


            clock.tick(60)
            if self.tick > 60:
                self.tick = 1
                self.musicc[0] += 1
                self.musicc[1] += 1
            else:
                self.tick += 1
            
            if self.musicc[0] > randint(20, 30):
                self.musicc[0] = 0
                self.audio.random.play()
            elif self.musicc[1] > 8:
                self.musicc[1] = 0
                self.audio.noise.play()
            
            # print(self.musicc)

            self._level_trans()
            self._end()
            self.grades.run()

            # Blits scaled screen (128, 128) to the actual window
            self.window.blit(
                pygame.transform.scale(self.screen, (self.res*self.win_scale, self.res*self.win_scale)),
                (0, 0)
                )
            pygame.display.flip()

if __name__ == '__main__':
    gm = Game()
    gm.run()