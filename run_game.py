__author__ = 'leif'

import os
import pytmx
import pygame
import physics
import itertools
from pygame.locals import *
import pyscroll
from castlebats.buttons import *


RESOURCE_PATH = 'resources'

key_map = {
    K_LEFT: P1_LEFT,
    K_RIGHT: P1_RIGHT,
    K_UP: P1_UP,
    K_DOWN: P1_DOWN,
    K_q: P1_ACTION1,
    K_w: P1_ACTION2,
}


def load_map(filename):
    return pytmx.load_pygame(os.path.join(RESOURCE_PATH, filename))


def load_image(filename):
    return pygame.image.load(os.path.join(RESOURCE_PATH, filename))


# simple wrapper to keep the screen resizeable
def init_screen(width, height):
    return pygame.display.set_mode((width, height), pygame.RESIZABLE)


class Game:
    def __init__(self):
        self.buffer_size = None
        self.map_buffer = None
        self.running = False
        self.actors = {}

        self.init_buffer([screen.get_width() / 2, screen.get_height() / 2])

        self.tmx_data = load_map('level.tmx')
        map_data = pyscroll.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.buffer_size)
        self.bg = load_image('exterior-parallaxBG1.png')

        geometry = []
        for obj in self.tmx_data.objectgroups[0]:
            bbox = (0, obj.x, obj.y, 0, obj.width, obj.height)
            geometry.append(bbox)

        self.physicsgroup = physics.PlatformerPhysicsGroup(1, 1/60., 9.8, [], geometry)

        self.new_hero()

    def new_hero(self):
        hero = Hero()
        obj = self.tmx_data.get_object_by_name('hero')
        hero.body.bbox.move(0, obj.x, obj.y)
        self.add_actor(hero)

    def add_actor(self, actor):
        self.actors[actor.name] = actor
        self.physicsgroup.bodies.append(actor.body)

    def init_buffer(self, size):
        self.map_buffer = pygame.Surface(size)
        self.buffer_size = self.map_buffer.get_size()

    def draw(self, surface):
        sprites = []

        self.draw_bg(self.map_buffer)

        hero = self.actors['hero']
        bx, by = self.map_buffer.get_size()
        cx_, cy_, cz_ = hero.body.bbox.bottomcenter
        cx = cy_
        cy = cz_ - 72
        for actor in self.actors.values():
            rect = self.physicsgroup.toRect(actor.body.bbox)
            d, w, h = hero.body.bbox.size
            xx, yy = rect.topleft
            xx = xx - cx + (bx / 2)
            yy = yy - cy + (by / 2)
            x = xx - hero.axis.y + (w / 2)
            y = yy - hero.axis.z
            sprites.append((actor.image, pygame.Rect(x, y, w, h), 0))

        self.map_layer.draw(self.map_buffer, surface.get_rect(), sprites)

        #pygame.draw.rect(self.map_buffer, (0, 255, 0, 128), (xx, yy-40, w, h), 1)

        pygame.transform.scale(self.map_buffer, surface.get_size(), surface)

    def draw_bg(self, surface):
        surface.blit(self.bg, (0,0))
        surface.blit(self.bg, (self.bg.get_width(),0))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                break

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                    break

            elif event.type == VIDEORESIZE:
                init_screen(event.w, event.h)
                self.init_buffer([screen.get_width() / 2, screen.get_height() / 2])
                self.map_layer.set_size(self.buffer_size)

            self.actors['hero'].handle_input(event)

    def update(self, dt):
        x, y, z = self.actors['hero'].body.bbox.topcenter
        self.map_layer.center((y, z - 72))
        self.physicsgroup.update(dt)
        for actor in self.actors.values():
            actor.update(dt)

        hero = self.actors['hero']
        if not hero.alive:
            self.new_hero()

    def run(self):
        clock = pygame.time.Clock()
        self.running = True

        try:
            while self.running:
                td = clock.tick(60)
                self.handle_input()
                self.update(td)
                self.update(td)
                self.draw(screen)
                pygame.display.flip()

        except KeyboardInterrupt:
            self.running = False


class Hero(pygame.sprite.Sprite):
    sprite_sheet = 'elisa-spritesheet1.png'
    name = 'hero'

    image_animations = [
        ('idle',      100, ((10, 10, 34, 44, 15, 42), )),
        ('attacking', 200, ((34, 254, 52, 52, 25, 48), )),
        ('walking',   300, ((304, 132, 36, 40, 15, 38), (190, 130, 28, 44, 14, 40), (74, 132, 32, 40, 15, 38), (190, 130, 28, 44, 14, 40)))
    ]

    def __init__(self):
        bbox = physics.BBox((0, 0, 0, 32, 32, 40))
        self.body = physics.Body3(bbox, (0, 0), (0, 0), 0)
        self.animations = {}
        self.state = set()
        self.axis = None
        self.image = None
        self.alive = True
        self.flip = True
        self.animation_timer = 0
        self.current_animation = None
        self.load_animations()
        self.set_animation('idle')

    def set_frame(self, frame):
        self.animation_timer, frame = frame
        self.image, axis = frame
        self.axis = axis.copy()
        if self.flip:
            w, h = self.image.get_size()
            self.image = pygame.transform.flip(self.image, 1, 0)
            self.axis.y = w - self.axis.y

    def load_animations(self):
        s = load_image(self.sprite_sheet)

        self.animations = {}
        for name, ttl, tiles in self.image_animations:
            frames = []
            for x1, y1, w, h, ax, ay in tiles:
                image = pygame.Surface((w, h))
                image.blit(s, (0, 0), (x1, y1, w, h))
                image.set_colorkey(image.get_at((0, 0)))
                frames.append((image, physics.Vector3(0, ax, ay)))
            self.animations[name] = ttl, frames

        self.set_animation('idle', itertools.repeat)
        self.state.add('idle')

    def set_animation(self, name, func=None):
        self.animation_timer, animation = self.animations[name]

        if func:
            if len(animation) == 1:
                animation = func(animation[0])
            else:
                animation = func(animation)

        self.current_animation = zip(itertools.repeat(self.animation_timer), animation)
        self.set_frame(next(self.current_animation))

    def update(self, dt):
        if self.animation_timer > 0:
            self.animation_timer -= dt
            if self.animation_timer <= 0:
                try:
                    self.set_frame(next(self.current_animation))
                except StopIteration:
                    self.set_animation('idle')

        if self.body.bbox.bottom > 1800:
            self.alive = False

    def change_state(self, state):
        self.state.add(state)

        if 'attacking' in self.state:
            self.set_animation('attacking')
            self.state.remove('attacking')

        elif 'walking' in self.state:
            self.set_animation('walking', itertools.cycle)

        elif 'idle' in self.state:
            self.set_animation('idle', itertools.repeat)

    def handle_input(self, event):
        # big ugly bunch of if statements... poor man's state machine
        try:
            button = key_map[event.key]
        except (KeyError, AttributeError):
            return

        if abs(self.body.vel.z) < .1:
            try:
                self.state.remove('jumping')
            except KeyError:
                pass

        if 'idle' in self.state:
            if event.type == KEYDOWN:
                if button == P1_LEFT:
                    self.state.remove('idle')
                    self.change_state('walking')
                    self.flip = True
                    self.body.vel.y = -2
                elif button == P1_RIGHT:
                    self.state.remove('idle')
                    self.change_state('walking')
                    self.flip = False
                    self.body.vel.y = 2
                elif button == P1_UP and 'jumping' not in self.state:
                    self.change_state('jumping')
                    self.body.vel.z = -3
                elif button == P1_ACTION1:
                    self.change_state('attacking')

        elif 'walking' in self.state:
            if event.type == KEYUP:
                if button == P1_LEFT:
                    self.state.remove('walking')
                    self.change_state('idle')
                    self.body.vel.y = 0
                elif button == P1_RIGHT:
                    self.state.remove('walking')
                    self.change_state('idle')
                    self.body.vel.y = 0
                elif button == P1_UP and 'jumping' not in self.state:
                    self.change_state('jumping')
                    self.body.vel.z = -3


class Level:
    def __init__(self):
        pass


if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    screen = init_screen(900, 600)
    pygame.display.set_caption('Castle Bats')

    game = Game()
    try:
        game.run()
    except:
        pygame.quit()
        raise

