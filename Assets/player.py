import pygame
import pygame.gfxdraw
from pygame.math import Vector2 as vec2
from random import uniform, randint

from Assets.spritesheet import spritesheet
from Assets.entity import Entity
from Assets.misc import Light


class Player:
    def __init__(self, gm):
        self.gm = gm

        self.spawn_pos = vec2(10, 10)
        self.rect = pygame.Rect(self.spawn_pos[0], self.spawn_pos[1], 4, 8)
        self.tospawn()

        self.ss = spritesheet('Assets/Graphics/Player/sprites.png')
        key = (255, 255, 255)
        self.ani = {
            'idle':[self.ss.image_at([0, 0, 6, 8], key)],
            'walk':[
                self.ss.image_at([6, 0, 6, 8], key),
                self.ss.image_at([0, 0, 6, 8], key)
                ],
            'jump':[self.ss.image_at([6, 0, 6, 8], key)],
            'ghost':[
                self.ss.image_at([0, 8, 7, 7], key),
                self.ss.image_at([7, 8, 7, 7], key),
                self.ss.image_at([14, 8, 7, 7], key),
                self.ss.image_at([21, 8, 7, 7], key),
                self.ss.image_at([28, 8, 7, 7], key),
                self.ss.image_at([35, 8, 7, 7], key),
            ]
        }
        self.ani_state = ['idle', 0, False]
        self.ani_speed = 5



        self.jump_dust = Entity(self.gm)
        self.jump_dust.ss = spritesheet('Assets/Graphics/Player/jump_particle.png')
        self.jump_dust.ani = {
            'jump':[
                self.jump_dust.ss.image_at([0, 0, 6, 5], key),
                self.jump_dust.ss.image_at([6, 0, 6, 5], key),
                self.jump_dust.ss.image_at([12, 0, 6, 5], key),
                self.jump_dust.ss.image_at([18, 0, 6, 5], key)
            ]
        }
        self.jump_dust.ani_state[0] = 'jump'
        self.jump_dust.ani_speed = 4

        self.light = Light(15, (10, 10, 10))

        self.pineapples = 0
        self.collect_animation = [False, 8]

        self.ghost_ani = False
        self.last_death_pos = vec2(0, 0)
        self.last_death_del = vec2(0, 0)
        
        
    def tospawn(self):
        for e in self.gm.world.entities:
            if e.id == '1':
                self.spawn_pos = e.rect.topleft
        self.reload()

    def reload(self):
        self.last_death_pos = vec2(self.rect.x, self.rect.y)
        self.rect = pygame.Rect(self.spawn_pos[0], self.spawn_pos[1], 4, 8)
        
        self.movement = [0, 0]
        self.joy_movementx = 0
        self.vel = [0.0, 0.0]
        self.air_timer = 0
        self.collisions = self._move()
        self.dusts = []
    
    def hit(self):
        self.gm.audio.player_hit.play()

        for e in self.gm.world.entities:
            if e.id == '12':
                e.id = '11'
        self.reload()
        self.ghost_ani = True
        
    
    def _collision_test(self):
        hit_list = []
        for t in self.gm.world.tiles:
            if self.rect.colliderect(t):
                hit_list.append(t)
        return hit_list
    
    def _move(self):
        collision_types = {'top':False, 'bottom':False, 'right':False, 'left':False}
        self.rect.x += self.movement[0]
        hit_list = self._collision_test()
        for t in hit_list:
            if self.movement[0] > 0:
                self.rect.right = t.left
                collision_types['right'] = True
            elif self.movement[0] < 0:
                self.rect.left = t.right
                collision_types['left'] = True
        self.rect.y += self.movement[1]
        hit_list = self._collision_test()
        for t in hit_list:
            if self.movement[1] > 0:
                self.rect.bottom = t.top
                collision_types['bottom'] = True
            elif self.movement[1] < 0:
                self.rect.top = t.bottom
                collision_types['top'] = True
        
        return collision_types
    

    def _collect_animation(self):
        if self.collect_animation[0]:
            if self.gm.tick % 2 == 0:
                self.collect_animation[1] -= 1
            
            if self.collect_animation[1] > 7:
                size = 10
            else:
                size = self.collect_animation[1]
            pygame.draw.circle(self.gm.screen,
            (255, 255, 255),
            [self.rect.centerx-self.gm.camera.x, self.rect.centery-self.gm.camera.y],
            size,
            1
            )
            if self.collect_animation[1] == 0:
                self.collect_animation = [False, 8]
    
    def _ghost_ani(self):
        if self.ghost_ani:
            self.last_death_del = self.last_death_pos-self.spawn_pos
            self.last_death_del = self.last_death_del.as_polar()
            self.last_death_del = vec2(self.last_death_del[0], self.last_death_del[1])
            self.last_death_del.x = max(self.last_death_pos.distance_to(self.spawn_pos) / 10, 2)
            self.last_death_del.y += 150
            self.last_death_del.from_polar(self.last_death_del)
            self.last_death_pos = self.last_death_del+self.last_death_pos

            self.rect.topleft = self.last_death_pos
            self.gm.phys.add_p(pygame.Rect(self.rect.centerx, self.rect.centery, 2, 2), [uniform(-1, 1), 1], (10, 50, 100))
        if self.rect.collidepoint(self.spawn_pos):
            self.ghost_ani = False

    
    def _animate(self):
        if self.air_timer > 6:
            self.ani_state[0] = 'jump'
            self.ani_state[1] = 0
        elif self.movement[0] > 0:
            self.ani_state[2] = False
            self.ani_state[0] = 'walk'
        elif self.movement[0] < 0:
            self.ani_state[2] = True
            self.ani_state[0] = 'walk'
        elif self.ghost_ani:
            self.ani_state[0] = 'ghost'
        else:
            self.ani_state[0] = 'idle'
            self.ani_state[1] = 0


        if self.gm.tick % self.ani_speed == 0:
            if self.ani_state[1] == len(self.ani[self.ani_state[0]]) - 1:
                self.ani_state[1] = 0
            else:
                self.ani_state[1] += 1
        
        
        surf = self.ani[self.ani_state[0]][self.ani_state[1]]
        if self.ghost_ani:
            surf = pygame.transform.rotate(surf, self.last_death_del.y)
        self.gm.screen.blit(
            pygame.transform.flip(surf, self.ani_state[2], False),
            (self.rect.x-self.gm.camera.x-1, self.rect.y-self.gm.camera.y)
            )
    
    def run_dusts(self):
        for d in self.dusts:
            if d.ani_state[0] == 'jump' and d.ani_state[1] == 3:
                self.dusts.remove(d)
            d.run()
    
    def add_jump_dust(self):
        jdc = Entity(self.gm)
        jdc.rect.midbottom = [self.rect.centerx, self.rect.bottom+1]
        jdc.ss = self.jump_dust.ss
        jdc.ani = self.jump_dust.ani
        jdc.ani_state = self.jump_dust.ani_state
        jdc.ani_state[1] = 0
        jdc.ani_speed = self.jump_dust.ani_speed

        self.dusts.append(jdc)
    
    def jump(self):
        if self.air_timer < 6 and not self.gm.ending_level and not self.ghost_ani and not self.gm.end:
            self.gm.audio.player_jump.play()
            self.add_jump_dust()

            self.vel[1] = -2.1


    
    def entity_collisions(self):
        for e in self.gm.world.entities:
            if self.rect.colliderect(e.rect):
                if e.id == '2':
                    self.hit()
                elif e.id == '3':
                    e.id = '4'
                    self.gm.audio.door_open.play()
                elif e.id == '5':
                    self.spawn_pos = [e.rect.x, e.rect.y-3]
                elif e.id == '7':
                    self.gm.audio.player_collect.play()
                    self.collect_animation[0] = True
                    self.gm.world.lights.remove(e.other['light'])
                    self.gm.world.entities.remove(e)
                    self.pineapples += 1
                elif e.id == '11':
                    self.gm.audio.player_up_crystal.play()
                    self.collect_animation[0] = True
                    for p in range(randint(3, 5)):
                        prect = self.rect.copy()
                        size = randint(1, 2)
                        prect.width = size
                        prect.height = size
                        self.gm.phys.add_p(prect, [uniform(-1, 1), uniform(1.0, 2.0)], (24, 101, 120))
                    e.id = '12'
                    self.vel[1] = -1.5
            else:
                if e.id == '4':
                    e.id = '3'
                    self.gm.audio.door_close.play()

    

    def run_light(self):
        self.light.rect.center = self.rect.center
        self.gm.screen.blit(self.light.surf, [self.light.rect.x-self.gm.camera.x, self.light.rect.y-self.gm.camera.y], special_flags=pygame.BLEND_ADD)

        
    
    def run(self):
        if not self.ghost_ani and not self.gm.ending_level:
            self.movement = [0, 0]
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT] or self.joy_movementx == 1:
                self.movement[0] += 1
            if keys[pygame.K_LEFT] or self.joy_movementx == -1:
                self.movement[0] -= 1
                
            
            
            self.movement[0] += self.vel[0]
            self.movement[1] += self.vel[1]
            self.collisions = self._move()
            
            if self.collisions['bottom']:
                self.vel[1] = 0
                self.air_timer = 0
                self.vel[0] = 0
            else:
                self.air_timer += 1
                self.vel[1] += self.gm.phys.gravity
                if self.vel[1] > 3:
                    self.vel[1] = 3
            
            if self.collisions['top']:
                self.vel[1] = 0
            
            self.entity_collisions()
            if self.pineapples == self.gm.world.properties['rooms'][self.gm.world.current_room]['pineapples'] and not self.gm.to_next_level:
                self.gm.to_next_level = True
                self.gm.ending_level = True
                self.cs_circle_size = 100
            if self.gm.to_next_level and not self.gm.ending_level:
                if self.gm.world.properties['rooms'][self.gm.world.current_room]['next'] != 'END':
                    self.gm.to_next_level = False
                    self.gm.beginning_level = True
                    self.pineapples = 0
                    self.gm.world.current_room = self.gm.world.properties['rooms'][self.gm.world.current_room]['next']
                    self.gm.world.load(self.gm.world.world_name)
                    self.tospawn()
                    self.gm.camera.center = [self.rect.x+100, self.rect.y+100]
                else:
                    self.gm.end = True
        
        
            self._collect_animation()
            self.run_dusts()
            
        self._ghost_ani()
        self._animate()
        
            
    