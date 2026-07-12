import pygame



class Audio:
    def __init__(self):

        self.player_jump = pygame.mixer.Sound('Assets/Audio/Player/jump.wav')
        self.player_hit = pygame.mixer.Sound('Assets/Audio/Player/hit.wav')
        self.player_collect = pygame.mixer.Sound('Assets/Audio/Player/collect.wav')
        self.player_collect.set_volume(.2)
        self.player_up_crystal = pygame.mixer.Sound('Assets/Audio/Player/up_crystal.wav')
        self.player_up_crystal.set_volume(.2)

        self.door_open = pygame.mixer.Sound('Assets/Audio/Door/open.wav')
        self.door_open.set_volume(.15)
        self.door_close= pygame.mixer.Sound('Assets/Audio/Door/close.wav')
        self.door_close.set_volume(.15)

        self.random = pygame.mixer.Sound('Assets/Audio/Music/random.wav')
        self.random.set_volume(.3)
        self.noise = pygame.mixer.Sound('Assets/Audio/Music/white-noise.wav')
        self.noise.set_volume(.2)
        self.noise.play()
