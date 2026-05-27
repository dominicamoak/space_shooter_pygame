
import pygame
import random
from os.path import join

# MAIN CLASSES
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'player.png')).convert_alpha()
        self.rect = self.image.get_frect(center = (window_width / 2, window_height / 2))
        self.direction = pygame.Vector2()
        self.speed = 300
        
    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt
        
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE]:
            print('fire laser')
    
    
    # player_rect.center = pygame.mouse.get_pos()
    # print(pygame.mouse.get_pressed())

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (random.randint(0, window_width), random.randint(0, window_height)))



# GENERAL SETUP
pygame.init()

window_width, window_height = 1280, 720
display_surface = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('SPACE SHOOTER')

running = True
clock = pygame.time.Clock()

# Surface
surf = pygame.Surface((100,300))
surf.fill('yellow')

# Sprite Instances
all_sprites = pygame.sprite.Group()
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
for i in range(20):
    Star(all_sprites, star_surf)

player = Player(all_sprites)


meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
meteor_rect = meteor_surf.get_frect(center = (window_width / 2, window_height / 2))

laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
laser_rect = laser_surf.get_frect(bottomleft = (20, window_height - 20))

# GAME FLOW
while running:
    dt = clock.tick(60) / 1000 # clock.tick() returns in milliseconds [framerate control]
    # print(clock.get_fps()) # check fps
    
    # Event Loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    all_sprites.update(dt)
    
    #Draw Game
    display_surface.fill('#391142')
    
    all_sprites.draw(display_surface)
    
    pygame.display.update()



pygame.quit()
