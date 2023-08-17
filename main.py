import pygame, sys, time
import random
from os import path

from pygame import key
from pygame import transform

# konstanty a fce neinteragujici s pygame

BLACK = (0, 0, 0)
PURPLE = (150, 10, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
POOP = (60, 50, 8)

WIDTH = 900
HEIGHT = 900

FPS = 30

folder = path.dirname(__file__)
data = path.join(folder, "data")

# fce interagujici s pygame

# start pygame + start modulu
pygame.init()
pygame.mixer.init()


# nastaveni okna aj.

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bunny")


class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pygame.image.load(filename).convert_alpha()

    def one_image(self, x, y, w, h):
        image = pygame.Surface((w, h))
        image.blit(self.spritesheet, (0, 0), (x, y, w, h))
        return pygame.transform.scale2x(image)


# kralik PNG
bun = Spritesheet(path.join(data, "rabbit2.png"))
# bobek PNG
poop_pic = Spritesheet(path.join(data, "poop.png"))
# kytka PNG
plant_pic = Spritesheet(path.join(data, "plant.png"))

# grafika a hudba
ground = pygame.image.load(path.join(data, "grass.jpg")).convert()


class Bunny(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.orient = 0
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.running = False
        self.delay = 100
        self.speed = 10
        self.width = 72
        self.height = 72
        # doplnene atributy
        self.orient_eat = 4
        self.can_run = True
        self.poop_size = 1
        self.eating = False
        self.eating_start = 0
        self.eat_target = None
        self.kousnuti_frame = 0

        self.animate_stand()

        self.rect = self.image.get_rect()
        self.rect.bottom = 372
        self.rect.x = WIDTH / 2
        self.poopshiftx = (0, 23, 0, -23)
        self.poopshifty = (30, 20, -17, 20)
        # eating range
        self.xboxik = self.rect.midtop[0]
        self.yboxik = self.rect.midtop[1]
        self.box_x = 72
        self.box_y = 45
        self.offset_box_x = 0
        self.offset_box_y = 45

    def update(self):

        keystate = pygame.key.get_pressed()
        if self.can_run:
            if keystate[pygame.K_RSHIFT]:
                self.speed = 20
                self.delay = 50
            else:
                self.speed = 10
                self.delay = 100

            if keystate[pygame.K_RIGHT]:
                self.rect.x += self.speed
                self.orient = 3
                # self.orient_eat = self.orient + 4
                self.running = True
                self.xboxik = self.rect.midright[0]
                self.yboxik = self.rect.midright[1]
                self.box_x = 45
                self.box_y = 72
                self.offset_box_x = -45
                self.offset_box_y = 0
                self.animate_run()
            elif keystate[pygame.K_LEFT]:
                self.rect.x -= self.speed
                self.orient = 1
                # self.orient_eat = self.orient + 4
                self.running = True
                self.xboxik = self.rect.midleft[0]
                self.yboxik = self.rect.midleft[1]
                self.box_x = 45
                self.box_y = 72
                self.offset_box_x = 45
                self.offset_box_y = 0
                self.animate_run()
            elif keystate[pygame.K_UP]:
                self.rect.y -= self.speed
                self.orient = 0
                # self.orient_eat = self.orient + 4
                self.running = True
                self.xboxik = self.rect.midtop[0]
                self.yboxik = self.rect.midtop[1]
                self.box_x = 72
                self.box_y = 45
                self.offset_box_x = 0
                self.offset_box_y = 45
                self.animate_run()
            elif keystate[pygame.K_DOWN]:
                self.rect.y += self.speed
                self.orient = 2
                # self.orient_eat = self.orient + 4
                self.running = True
                self.xboxik = self.rect.midbottom[0]
                self.yboxik = self.rect.midbottom[1]
                self.box_x = 72
                self.box_y = 45
                self.offset_box_x = 0
                self.offset_box_y = -45
                self.animate_run()
            else:
                self.running = False
                self.frame = 0

        eating_range = boxik(
            self.xboxik,
            self.yboxik,
            self.box_x,
            self.box_y,
            self.offset_box_x,
            self.offset_box_y,
        )
        my_sprites.add(eating_range)

        # osetreni vybehnuti mimo obrazovku
        if self.rect.left > WIDTH:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = WIDTH

        if self.rect.bottom < 0:
            self.rect.top = HEIGHT
        elif self.rect.top > HEIGHT:
            self.rect.bottom = 0
        # bobkovani - muze i pri jedeni (kralici bezne delaji)
        if keystate[pygame.K_SPACE]:
            poop = Poop(
                self.rect.center[0] + self.poopshiftx[self.orient],
                self.rect.center[1] + self.poopshifty[self.orient],
                self.poop_size,
            )
            poop_sprites.add(poop)

        if pygame.sprite.spritecollide(eating_range, plant_sprites, False):
            # print("kolize")
            # kralik papa kytku
            if keystate[pygame.K_RETURN]:
                self.frame = 0
                self.orient_eat = self.orient + 4
                self.eating = True
                self.kousnuti = 0

        if self.eating:
            self.can_run = False
            eat_target = pygame.sprite.spritecollide(eating_range, plant_sprites, False)
            self.animate_eat(eat_target)
            if self.kousnuti > 12:
                self.eating = False
                self.poop_size *= 1.25
                eat_target = None
                self.can_run = True
            else:
                if pygame.time.get_ticks() - self.eating_start > 50:
                    # print("Koušu po: ", self.kousnuti, ".")
                    self.kousnuti += 1
                    self.animate_eat(eat_target)

        if not self.running and not self.eating:
            self.animate_stand()

    def animate_stand(self):
        self.image = bun.one_image(
            0, self.orient * self.height, self.width, self.height
        )
        self.image.set_colorkey(BLUE)

    def animate_run(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.delay:
            self.frame = (self.frame + 1) % 4
            self.image = bun.one_image(
                self.frame * self.width,
                self.orient * self.height,
                self.width,
                self.height,
            )
            self.image.set_colorkey(BLUE)
            self.last_update = now

    def animate_eat(self, target):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.delay:
            self.kousnuti_frame = (self.kousnuti_frame) % 4
            self.image = bun.one_image(
                self.kousnuti_frame * self.width,
                self.orient_eat * self.height,
                self.width,
                self.height,
            )
            self.image.set_colorkey(BLUE)
            self.last_update = now
            self.eating_start = now
            # print(self.kousnuti)
            self.kousnuti_frame += 1
            # print(self.kousnuti)
        if target == None:
            pass
        else:
            for p in target:
                if p.eaten_cycle_counter == 0:
                    p.eat()
                else:
                    if self.kousnuti % 3 == 0:
                        p.eaten_cycle_counter += 1

    # def animate_eat(self, target):
    #     if target == None:
    #         pass
    #     now = pygame.time.get_ticks()
    #     if now - self.last_update > self.delay:
    #         self.kousnuti = (self.kousnuti) % 4
    #         self.image = bun.one_image(
    #             self.kousnuti * self.width,
    #             self.orient_eat * self.height,
    #             self.width,
    #             self.height,
    #         )
    #         self.image.set_colorkey(BLUE)
    #         self.last_update = now
    #         # print(self.kousnuti)
    #         self.kousnuti += 1
    #         # print(self.kousnuti)

    #     for p in target:
    #         p.eat()


class Plant(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.mini_ratio = 0.25
        self.image = plant_pic.one_image(0, 0, 128, 128)
        self.image = pygame.transform.scale(
            self.image, (128 * self.mini_ratio, 128 * self.mini_ratio)
        )
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.orient = True
        self.last_update = pygame.time.get_ticks()
        self.eat_start = 0
        self.eat_bite_time = 0
        self.eaten = False
        self.eaten_cycle_counter = 0

    def update(self):
        if pygame.time.get_ticks() - self.last_update > 250:
            self.image = pygame.transform.flip(self.image, True, False)
            self.last_update = pygame.time.get_ticks()

        if self.eaten:
            if pygame.time.get_ticks() - self.eat_bite_time > 280:
                self.image = pygame.transform.scale(
                    self.image, (128 * self.mini_ratio, 128 * self.mini_ratio)
                )
                self.eat_bite_time = pygame.time.get_ticks()
                self.mini_ratio = self.mini_ratio / 2
                self.image.set_colorkey(BLACK)
                self.rect.center = self.rect.center
                self.last_update = pygame.time.get_ticks()
                self.eaten_cycle_counter += 1

            if pygame.time.get_ticks() - self.eat_start > 1000:
                self.kill()

    def eat(self):
        self.eat_start = pygame.time.get_ticks()
        self.eat_bite_time = pygame.time.get_ticks()
        self.eaten = True
        self.eaten_cycle_counter += 1


class Poop(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.image = poop_pic.one_image(0, 0, 10, 10)
        self.image = pygame.transform.scale(self.image, (size * 10, size * 10))
        self.image.set_colorkey(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speedx = random.randint(-15, 15) / 10.0
        self.speedy = random.randint(-15, 15) / 10.0
        self.dec = 0.1
        self.start = pygame.time.get_ticks()

    def update(self):
        if round(self.speedx, 2) > 0:
            self.rect.x += self.speedx
            self.speedx -= self.dec
        elif round(self.speedx, 2) < 0:
            self.rect.x += self.speedx
            self.speedx += self.dec
        if round(self.speedy) > 0:
            self.rect.y += self.speedy
            self.speedy -= self.dec
        elif round(self.speedy) < 0:
            self.rect.y += self.speedy
            self.speedy += self.dec

        if pygame.time.get_ticks() - self.start > 30000:
            self.kill()


class boxik(pygame.sprite.Sprite):
    def __init__(self, x, y, box_x, box_y, offset_x=0, offset_y=-18):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((box_x, box_y))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x + offset_x, y + offset_y)
        self.start = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.start > 30:
            self.kill()


# hodiny FPS-clock
clock = pygame.time.Clock()

# kolekce spritu
my_sprites = pygame.sprite.Group()
poop_sprites = pygame.sprite.Group()
plant_sprites = pygame.sprite.Group()
# kralik
bunny = Bunny()
# kytky
plants_num = random.randint(5, 20)  # nahodny pocet kytek
# # generator kytek
for p in range(0, plants_num):
    rand_x = random.randint(32, WIDTH - 32)
    rand_y = random.randint(32, HEIGHT - 32)
    plant = Plant(rand_x, rand_y)
    plant_sprites.add(plant)
    # osetreni duplicit v plant_sprites -> nebude generovat pres sebe
    # if pygame.sprite.spritecollide(plant, plant_sprites, True):
    #     plant.kill()
    # else:
    #     plant_sprites.add(plant)

my_sprites.add(bunny)


running = True

while running:
    # FPS kontrola
    clock.tick(FPS)

    # Event
    for event in pygame.event.get():
        # print(event)
        if event.type == pygame.QUIT:
            running = False

    # if pygame.sprite.spritecollide(my_sprites, plant_sprites, True):
    #     print("Kolize")

    # Update
    poop_sprites.update()
    plant_sprites.update()
    my_sprites.update()

    # Render
    screen.fill(BLACK)
    screen.blit(ground, (0, 0))
    poop_sprites.draw(screen)
    plant_sprites.draw(screen)
    my_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
