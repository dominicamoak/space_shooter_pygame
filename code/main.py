
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
            laser_sound.play()
        
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
        self.original_surf = surf
        self.image = self.original_surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3500
        self.direction = pygame.Vector2(random.uniform(-0.4, 0.4), 1)
        self.speed = random.randint(250, 400)
        
        # Transform
        self.rotation = 0
        self.rotation_speed = random.randint(10, 25)
    
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
            
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

class Explosions(pygame.sprite.Sprite):
    def __init__(self, groups, frames, pos):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
    
    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

def collisions():
    global running, game_state, score, final_score
    
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        damage_sound.play()
        game_state = 'game_over'
    
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True, pygame.sprite.collide_mask)
        if collided_sprites:
            score += 10
            final_score = score
            laser.kill()
            Explosions(all_sprites, explosion_frames, laser.rect.midtop)
            explosion_sound.play()

def display_score(score):
    # current_time = pygame.time.get_ticks() // 100
    text_surf = font.render(str(score), True, '#e4e7ed')
    text_rect = text_surf.get_frect(midbottom = ((window_width - 75, window_height - 650)))
    display_surface.blit(text_surf, text_rect)

    pygame.draw.rect(display_surface, '#e4e7ed', text_rect.inflate(30, 30).move(0, -8), 5, 10)

def display_final_score(final_score):
    text_surf = final_score_font.render('Your Score: ' + str(final_score), True, '#e4e7ed')
    text_rect = text_surf.get_frect(center = (window_width / 2, window_height - 500))
    display_surface.blit(text_surf, text_rect)

def game_over_menu(events):
    global running, game_state

    play_text_surf = menu_font.render('Play Again', True, '#e4e7ed')
    play_text_rect = play_text_surf.get_frect(center= (window_width / 2, window_height - 400))
    display_surface.blit(play_text_surf, play_text_rect)
    
    exit_text_surf = menu_font.render('Exit Game', True, '#e4e7ed')
    exit_text_rect = exit_text_surf.get_frect(center= (window_width / 2, window_height - 300))
    display_surface.blit(exit_text_surf, exit_text_rect)
    
    # Event Loop
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if play_text_rect.collidepoint(event.pos):
                # reset everything, start game over
                reset_game()
                game_state = 'playing'
            
            if exit_text_rect.collidepoint(event.pos):
                running = False

def init_game():
    global all_sprites, meteor_sprites, laser_sprites
    global player, score
    
    score = 0
    
    # Sprite Instances
    all_sprites = pygame.sprite.Group()
    meteor_sprites = pygame.sprite.Group()
    laser_sprites = pygame.sprite.Group()
    for i in range(20):
        Star(all_sprites, star_surf)
    player = Player(all_sprites)

def reset_game():
    init_game()

def game_sound(new_state):
    global game_state, game_music
    
    if new_state == 'playing':
        game_music.set_volume(0.2)
    if new_state == 'game_over':
        game_music.set_volume(0.02)


# GENERAL SETUP
pygame.init()

window_width, window_height = 1280, 720
display_surface = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('SPACE SHOOTER')

running = True
game_state = 'playing' # playing, game_over
previous_state = 'none'
clock = pygame.time.Clock()
score = 0
final_score = 0

# Surface Creations / Imports
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 30)
final_score_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
menu_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 75)
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]

# Sounds
laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.2)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
explosion_sound.set_volume(0.2)
damage_sound = pygame.mixer.Sound(join('audio', 'damage.ogg'))
damage_sound.set_volume(0.2)
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.play(loops= -1) # play indefinitely


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
    events = pygame.event.get()
    
    if game_state != previous_state:
        game_sound(game_state)
        previous_state = game_state
    
    if game_state == 'playing':
        dt = clock.tick(60) / 1000 # clock.tick() returns in milliseconds [framerate control]
        # print(clock.get_fps()) # check fps
    
        # Event Loop
        for event in events:
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
        display_score(score)
        all_sprites.draw(display_surface)
    
    elif game_state == 'game_over':
        # draw score to screen
        # show play again and Exit text to player
        # when played again, reset everything and game_state = playing
        # when exit, running = false
        
        # Draw Game
        display_surface.fill('#391142')
        display_final_score(score)
        game_over_menu(events)
        
    pygame.display.update()



pygame.quit()
