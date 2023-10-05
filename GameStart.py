import os
import random
import math
import pygame
from pygame import mixer
import button
from os import listdir
from os.path import isfile, join

from pygame.sprite import Group

pygame.init()
mixer.init()

pygame.display.set_caption("Python Game")
clock = pygame.time.Clock()
font = pygame.font.Font('srcs\Players\Font\Planes_ValMore.ttf', 36)  # Define the font and font size  # Create a text surface

WIDTH, HEIGHT = 1280, 800
FPS = 120
PLAYER_VEL = 5  # toc do nhan vat

window = pygame.display.set_mode((WIDTH, HEIGHT))
mypath = os.path.dirname(os.path.realpath(__file__))
# Function dao nguoc anh
def flip(sprites):  
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction = False):
    path = join(mypath ,"srcs", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]    # Load tat ca file anh trong srcs

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()     # Load anh 

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0,0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites
    return all_sprites


def get_block(size):
    path = join(mypath ,"srcs", "Tilesets", "tilesetgrass.png")
    image = pygame.image.load(path).convert_alpha()         # Load anh cua block
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(32, 0 , size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 255, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("Players", "Dude_Monster", 32, 32, True)
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0  
        self.y_vel = 0
        self.mask = None
        self.direction = "left"         # Chinh huong nhin cua nhan vat
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        
    # Hanh dong nhay
    def jump(self):
        
        self.y_vel = -self.GRAVITY * 9
        self.animation_count = 0
        self.jump_count += 1


    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    # Dap xuong mat dat
    def landed(self):
        self.y_vel = 0
        self.fall_count = 0
        self.jump_count = 0
    
    # Cung dau vao vat the
    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def move_left (self, vel):
        self.x_vel = -vel               # Di chuyen trai thi phai di nguoc truc hoanh
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right (self, vel):
        self.x_vel = vel   
        if self.direction != "right":           
            self.direction = "right"
            self.animation_count = 0

    def update_sprite(self):
        # Khong di chuyen thi load "dung yen"
        sprite_sheet = "idle"       
        if self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump1"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        # Lay ten hanh dong de tim kiem hoat anh trong srcs
        sprite_sheet_name = sprite_sheet + "_" + self.direction     
        # Lay hoat anh cua hanh dong
        sprites = self.SPRITES[sprite_sheet_name]                   
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)

        self.sprite = sprites[sprite_index] 
        self.animation_count += 1
        if self.animation_count >= len(sprites) * self.ANIMATION_DELAY:
            self.animation_count = 0
        
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)           # Quan trong trong perfect pixel collition 


    def loop(self, fps):
        self.y_vel += min (1, (self.fall_count / FPS ) * self.GRAVITY )  # effect trong luc khi nhay
        self.move(self.x_vel, self.y_vel)
        self.fall_count += 2
        self.update_sprite()
        


    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__ (self,x , y, width, height, name = None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height) , pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

# Check xem nhan vat co sap va cham hay khong
def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()

    collided_object = None

    for obj in objects:
        if pygame.sprite.collide_mask(obj, player):  # Use the built-in rect collision detection
            collided_object = obj  # Return the colliding object
            break
    player.move(-dx, 0)
    player.update()
    return collided_object

# Dam nhiem su va cham giua player va vat the    
def handle_vertical_collision(player, objects, dy):
    collied_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
        collied_objects.append(obj)
    return collied_objects



# Dam nhiem viec di chuyen
def handle_move(player, objects):
    keys = pygame.key.get_pressed()  # Get the currently pressed keys

    player.x_vel = 0
    # Check for collisions and update velocity
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)
    if not collide_left and keys[pygame.K_a] :
            player.move_left(PLAYER_VEL)
    if not collide_right and keys[pygame.K_d]:
            player.move_right(PLAYER_VEL)

    handle_vertical_collision(player, objects, player.y_vel)



def get_background(name):
    image = pygame.image.load(join(mypath ,"srcs", "Background", "nature_1", name))     # Lay anh cua background tu thu muc srcs/background
    _, _, width, height = image.get_rect()                                      # Lay width, height cua background
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)
    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x):
    # In background
    for tile in background:
        window.blit(bg_image, tile)

    # In vat the
    for obj in objects:
        obj.draw(window, offset_x)

    # In nhan vat
    player.draw(window, offset_x)
    pygame.display.update()


    # In FPS
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
    window.blit(fps_text, (5, 5))

    pygame.display.update()

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    window.blit(img, (x, y))


def main(window):
    background, bg_image = get_background("origbig.png")     # Lay background, va anh cua background 
    
    block_size = 100

    game_paused = True
    menu_state = "main"

    player = Player(100, 100 , 50 ,50)
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH // block_size, WIDTH * 2 // block_size)]
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size), Block(0, HEIGHT - block_size * 4, block_size)]

    offset_x = 0
    srcoll_area_width = 200

    #Load hinh anh cua menu
    bg_menu = pygame.image.load(join(mypath,"srcs", "Menu", "Background","background1.jpg")).convert_alpha()
    resume_img = pygame.image.load(join(mypath,"srcs", "Menu", "Button", "button_resume.png")).convert_alpha()
    options_img = pygame.image.load(join(mypath,"srcs", "Menu", "Button", "button_options.png")).convert_alpha()
    quit_img = pygame.image.load(join(mypath,"srcs", "Menu", "Button","button_quit.png")).convert_alpha()
    video_img = pygame.image.load(join(mypath,"srcs", "Menu", "Button","button_video.png")).convert_alpha()
    audio_img = pygame.image.load(join(mypath,"srcs", "Menu", "Button","button_audio.png")).convert_alpha()
    keys_img = pygame.image.load(join(mypath,"srcs", "Menu", "Button","button_keys.png")).convert_alpha()
    back_img = pygame.image.load(join(mypath,"srcs", "Menu", "Button","button_back.png")).convert_alpha()
    vol_up_img = pygame.image.load(join(mypath,"srcs", "Menu", "Button","vol_up.png")).convert_alpha()
    vol_down_img = pygame.image.load(join(mypath,"srcs", "Menu", "Button","vol_down.png")).convert_alpha()


    a = 250
    b = 50

    # In hinh anh menu
    resume_button = button.Button(304 + a, 125 + b, resume_img, 1)
    options_button = button.Button(297 + a, 250 + b, options_img, 1)
    quit_button = button.Button(336 + a, 375 + b, quit_img, 1)
    video_button = button.Button(226 + a, 75 + b, video_img, 1)
    audio_button = button.Button(225 + a, 200 + b, audio_img, 1)
    keys_button = button.Button(246 + a, 325 + b, keys_img, 1)
    # back_button = button.Button(332 + a, 450 + b, back_img, 1)
    back_button = button.Button(325 + a, 325 + b, back_img, 1)
    vol_up_button = button.Button(700, 250, vol_up_img, 1)
    vol_down_button = button.Button(400, 250, vol_down_img, 1)
    back_button2 = button.Button(575, 400, back_img, 1)
    
    
    esc_text = "Press ESC to pause"
    text_width, text_height = font.size(esc_text)  # Get the width and height of the text
    x = WIDTH - text_width

    # Backgound music
    mixer.music.load(join(mypath, "srcs", "Musics", "bg_music.mp3"))
    volume = 0.5
    mixer.music.set_volume(volume)
    mixer.music.play(-1)

    # Sound Effect
    jump_fx = mixer.Sound('srcs/Musics/jump.mp3')
    jump_fx.set_volume(volume)
    
    run = True
    while run:
        clock.tick(FPS)

        window.blit(bg_menu, (0,0))

        if game_paused == True:
            # Pause music when in menu
            pygame.mixer.music.pause()

            #check menu state
            if menu_state == "main":
                #draw pause window buttons
                if resume_button.draw(window):
                    pygame.mixer.music.unpause()
                    game_paused = False
                if options_button.draw(window):
                    menu_state = "options"
                if quit_button.draw(window):
                    run = False
            #check if the options menu is open 
            if menu_state == "options":
                #draw the different options buttons
                if video_button.draw(window):
                    print("Video Settings")
                if audio_button.draw(window):
                    menu_state = "audio"
                    print("Audio Settings")
                # if keys_button.draw(window):
                #     print("Change Key Bindings")
                if back_button.draw(window):
                    menu_state = "main"
            if menu_state == "audio":
                if vol_up_button.draw(window):
                    volume += 0.1
                    if volume > 1.0:
                        volume = 1.0
                    mixer.music.set_volume(volume)
                    print(volume)
                if vol_down_button.draw(window):
                    volume -= 0.1
                    if volume < 0.0:
                        volume = 0.0
                    mixer.music.set_volume(volume)
                    print(volume)
                if back_button2.draw(window):
                    menu_state = "options"

        else:
            player.loop(FPS)
            handle_move(player, objects)
            # In hinh anh cua game
            draw(window, background, bg_image, player, objects, offset_x)
            draw_text(esc_text, font, (255, 255, 255), x, 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 1:
                    jump_fx.play()
                    player.jump()
                if event.key == pygame.K_ESCAPE:
                    game_paused = True 
                

        if(player.rect.right - offset_x >= WIDTH - srcoll_area_width and player.x_vel > 0) or (
                player.rect.left - offset_x <= srcoll_area_width and player.x_vel < 0):
            offset_x += player.x_vel

        pygame.display.update()

    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)
