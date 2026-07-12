import pygame
from os import listdir
import json

from Assets.spritesheet import spritesheet
from Assets.entity import Entity
from Assets.misc import Light

alphabet = 'abcdefghijklmnopqrstuvwxyz'


class World:
    def __init__(self, gm):
        self.gm = gm

        self.tss = spritesheet('Assets/Graphics/tiles.png')
        self.tdefs = [
            None,
            self.load_tile_row(0, 5),
            self.load_tile_row(5, 5),
            self.load_tile_row(10, 5),
            self.load_tile_row(15, 5),
            self.load_tile_row(20, 5),
            self.load_tile_row(25, 5),
        ]
        key = (255, 255, 255)
        self.ess = spritesheet('Assets/Graphics/entities.png')
        self.edefs = [
            None,
            self.ess.image_at([0, 0, 5, 5], key),
            self.ess.image_at([5, 0, 5, 5], key),
            self.ess.image_at([10, 0, 5, 5], key),
            self.ess.image_at([15, 0, 5, 5], key),
            self.ess.image_at([20, 0, 5, 5], key),
            self.ess.image_at([0, 5, 5, 7], key),
            self.load_pineapple(),
            self.ess.image_at([25, 0, 5, 5], key),
            self.ess.image_at([30, 0, 5, 5], key),
            self.ess.image_at([35, 0, 5, 5], key),
            self.ess.image_at([40, 0, 5, 5], key),
            self.ess.image_at([45, 0, 5, 5], key),
            self.ess.image_at([40, 5, 5, 7], key),
            self.ess.image_at([45, 5, 5, 7], key),
        ]


        self.world = []
        self.properties = []
        self.worldb = []

        self.entities = []
        self.dentities = []

        self.lights = []

        self.emitters = []

        self.world_name = ''
        self.current_room = '0'
        self.tiles = []
        
        self.load('Test_World')
    
    def load_pineapple(self):
        frames = []
        for f in range(7):
            frames.append( self.ess.image_at([5*f+5, 5, 5, 7], (255, 255, 255)) )
        return frames
    
    def load_tile_row(self, y, s):
        key = (255, 255, 255)
        row = {
            '[0, 0, 0, 0]':self.tss.image_at([ 0, y, s, s ], key),
            '[0, 0, 1, 1]':self.tss.image_at([ s, y, s, s ], key),
            '[1, 0, 0, 1]':self.tss.image_at([ s*2, y, s, s ], key),
            '[0, 1, 1, 0]':self.tss.image_at([ s*3, y, s, s ], key),
            '[1, 1, 0, 0]':self.tss.image_at([ s*4, y, s, s ], key),
            '[0, 1, 1, 1]':self.tss.image_at([ s*5, y, s, s ], key),
            '[1, 0, 1, 1]':self.tss.image_at([ s*6, y, s, s ], key),
            '[1, 1, 0, 1]':self.tss.image_at([ s*7, y, s, s ], key),
            '[1, 1, 1, 0]':self.tss.image_at([ s*8, y, s, s ], key),
            '[1, 0, 0, 0]':self.tss.image_at([ s*9, y, s, s ], key),
            '[0, 1, 0, 0]':self.tss.image_at([ s*10, y, s, s ], key),
            '[0, 0, 1, 0]':self.tss.image_at([ s*11, y, s, s ], key),
            '[0, 0, 0, 1]':self.tss.image_at([ s*12, y, s, s ], key),
            '[1, 0, 1, 0]':self.tss.image_at([ s*13, y, s, s ], key),
            '[0, 1, 0, 1]':self.tss.image_at([ s*14, y, s, s ], key),
            '[1, 1, 1, 1]':self.tss.image_at([ s*15, y, s, s ], key),
            'bg':self.tss.image_at([ s*16, y, s, s ], key),

            
        }
        return row
    
    def load(self, file):
        self.world_name = file
        prop = open(f'Assets/Worlds/{self.world_name}/world.json')
        self.properties = json.load(prop)
        prop.close()
        file = open(f'Assets/Worlds/{self.world_name}/{self.current_room}.txt')
        directory = listdir(f'Assets/Worlds/{self.world_name}/')

        self.tiles = []

        w = file.read().splitlines()
        self.world = []
        x, y = 0, 0
        for r in w:
            self.world.append([*r])
            x = 0
            for c in r:
                if c != '0':
                    mx, my = int(x/5), int(y/5)
                    other = [
                        self.gm.qbin(w[my][mx-1]),
                        self.gm.qbin(w[my-1][mx]),
                        self.gm.qbin(w[my][mx+1]),
                        self.gm.qbin(w[my+1][mx]),
                        ]

                    if other != [1, 1, 1, 1]:
                        self.tiles.append(pygame.Rect(x, y, 5, 5))
                x += 5
            y += 5

        file.close()

        if not f'{self.current_room}b.txt' in directory:
            t = ''
            self.worldb = []
            for y in self.world:
                t += '0'*len(y) + '\n'
                self.worldb.append(y[:])

            file = open(f'Assets/Worlds/{self.world_name}/{self.current_room}b.txt', 'w')
            file.write(t)
            file.close()
            
        else:
            file = open(f'Assets/Worlds/{self.world_name}/{self.current_room}b.txt')

            w = file.read().splitlines()
            self.worldb = []
            x, y = 0, 0
            for r in w:
                self.worldb.append([*r])

            file.close()

        self.entities = []
        self.dentities = []
        self.lights = []
        self.emitters = []
        if not f'{self.current_room}e.txt' in directory:
            e = ''
            for y in self.world:
                e += '0'*len(y) + '\n'

            file = open(f'Assets/Worlds/{self.world_name}/{self.current_room}e.txt', 'w')
            file.write(e)
            file.close()
        else:
            file = open(f'Assets/Worlds/{self.world_name}/{self.current_room}e.txt')
            e = file.read().splitlines()
            file.close()
            x, y = 0, 0
            for r in e:
                x = 0
                for c in r:
                    if c != '0':
                        entity = self.add_entity(c, pygame.Rect(x, y, 5, 5))
                        if c == '6':
                            ll = Light(23, (15, 15, 0))
                            ll.rect.x = x-9
                            ll.rect.y = y-7
                            self.lights.append(ll)
                        elif c == '7':
                            pl = Light(11, (20, 20, 20))
                            pl.rect.x = x-3
                            pl.rect.y = y-2
                            entity.other['light'] = pl
                            self.lights.append(pl)
                        elif c == '9' or c == 'a':
                            self.tiles.append(pygame.Rect(x, y+3, 5, 2))
                        elif c == 'b':
                            ucl = Light(7, (10, 30, 30))
                            ucl.rect.x = x-1
                            ucl.rect.y = y-1
                            entity.other['light'] = ucl
                            self.lights.append(ucl)
                            if not self.gm.editor:
                                self.gm.phys.add_emitter(ucl.rect.center, (1,2), .5, (0, 3, 3), 10, 30)

                    x += 5
                y += 5

    def set_tile(self, pos, tile, bg=False):
        if pos[0] > len(self.world[0])-2 or pos[0] < 0 or pos[1] > len(self.world)-2 or pos[1] < 0:
            pass
        else:
            if bg:
                self.worldb[pos[1]][pos[0]] = tile
            else:
                self.world[pos[1]][pos[0]] = tile
    
    def add_entity(self, id, rect):
        if id in alphabet:
            id = str(alphabet.find(id)+10)
        entity = Entity(self.gm)
        entity.id = id
        entity.rect = rect
        if id == '7':
            entity.ani = {
                'base':self.load_pineapple()
            }
            entity.ani_state[0] = 'base'
            entity.ani_speed = 10
        else:
            entity.aniB = False
        self.entities.append(entity)
        return entity
    
    def save(self):
        file = open(f'Assets/Worlds/{self.world_name}/{self.current_room}.txt', 'w')
        world = ''
        for y in self.world:
            for x in y:
                world += x
            world += '\n'
        file.write(world)
        file.close()

        file = open(f'Assets/Worlds/{self.world_name}/{self.current_room}b.txt', 'w')
        worldb = ''
        for y in self.worldb:
            for x in y:
                worldb += x
            worldb += '\n'
        file.write(worldb)
        file.close()

        file = open(f'Assets/Worlds/{self.world_name}/{self.current_room}e.txt', 'w')
        entities = ''
        x, y = 0, 0
        
        for r in self.world:
            x = 0
            for c in r:
                m = [False]
                for e in self.entities:
                    if e.rect.x == x and e.rect.y == y:
                        m[0] = True
                        id = e.id
                        if int(id) > 9:
                            id = alphabet[int(id)-10]
                        m.append(id)
                if m[0]:
                    entities += m[1]
                else:
                    entities += '0'
                x += 5
            y += 5
            entities += '\n'
        file.write(entities)
        file.close()