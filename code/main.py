
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
        
        # Shooting Rest-Time
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.rest_duration = 400
        
        # Mask
        self.mask = pygame.mask.from_surface(self.image) # not really needed
    
    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks() # gives the time since laser is fired
            if current_time - self.laser_shoot_time >= self.rest_duration:
                self.can_shoot = True
    
    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt
        
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            laser = Laser((all_sprites, laser_sprites), laser_surf, self.rect.midtop)
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
        
        self.laser_timer()
    
    
    # player_rect.center = pygame.mouse.get_pos()
    # print(pygame.mouse.get_pressed())

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (random.randint(0, window_width), random.randint(0, window_height)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, groups, surf, pos):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
        self.speed = 500
    
    def update(self, dt):
        self.rect.centery -= self.speed * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, groups, surf, pos):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3500
        self.direction = pygame.Vector2(random.uniform(-0.4, 0.4), 1)
        self.speed = random.randint(250, 400)
    
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()

def collisions():
    global running
    
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        running = False
    
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True, pygame.sprite.collide_mask)
        if collided_sprites:
            laser.kill()

def display_score():
    current_time = pygame.time.get_ticks() // 100
    text_surf = font.render(str(current_time), True, '#e4e7ed')
    text_rect = text_surf.get_frect(midbottom = ((window_width / 2, window_height - 80)))
    display_surface.blit(text_surf, text_rect)

    pygame.draw.rect(display_surface, '#e4e7ed', text_rect.inflate(30, 30).move(0, -8), 5, 10)

# GENERAL SETUP
pygame.init()

window_width, window_height = 1280, 720
display_surface = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('SPACE SHOOTER')

running = True
clock = pygame.time.Clock()

# Surface Creations
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 30)


# Sprite Instances
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
for i in range(20):
    Star(all_sprites, star_surf)
player = Player(all_sprites)


# Custom Events - meteor event (Interval Timer)
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)


# GAME FLOW
while running:
    dt = clock.tick(60) / 1000 # clock.tick() returns in milliseconds [framerate control]
    # print(clock.get_fps()) # check fps
    
    # Event Loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x, y = random.randint(0, window_width), random.randint(-200, -100)
            Meteor((all_sprites, meteor_sprites), meteor_surf, (x, y))
    
    # Updates
    all_sprites.update(dt)
    collisions()
    
    # Draw Game
    display_surface.fill('#391142')    
    display_score()
    all_sprites.draw(display_surface)
    
    pygame.display.update()



pygame.quit()
