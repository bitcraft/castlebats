__author__ = 'leif'

import os
import pytmx
import pygame
import physics
import itertools
import threading
from pygame.locals import *
import pyscroll
from castlebats.buttons import *


RESOURCE_PATH = 'resources'
GRAVITY = 10.2
TIMESTEP = 1/120.
MOVE_POWER = 2
JUMP_POWER = 1.5
TARGET_FPS = 40

KEY_MAP = {
    K_LEFT: P1_LEFT,
    K_RIGHT: P1_RIGHT,
    K_UP: P1_UP,
    K_DOWN: P1_DOWN,
    K_q: P1_ACTION1,
    K_w: P1_ACTION2,
}

SOUND_FILES = {
    'sword': 'sword2.wav',
}


MUSIC_FILES = {
    'dungeon': 'dungeon.ogg'
}


def load_map(filename):
    return pytmx.load_pygame(os.path.join(RESOURCE_PATH, filename))


def load_image(filename):
    return pygame.image.load(os.path.join(RESOURCE_PATH, filename))


def load_sound(name):
    return pygame.mixer.Sound(os.path.join(RESOURCE_PATH, SOUND_FILES[name]))


def play_music(name):
    pygame.mixer.music.load(os.path.join(RESOURCE_PATH, MUSIC_FILES[name]))
    pygame.mixer.music.play(-1)


# simple wrapper to keep the screen resizeable
def init_screen(width, height):
    return pygame.display.set_mode((width, height), pygame.RESIZABLE)


class Game:
    def __init__(self):
        self.buffer_size = None
        self.map_buffer = None
        self.running = False
        self.actors = set()
        self.time = 0
        self.hero = None
        self.body_mapping = {}
        self.actors_lock = threading.Lock()
        self._add_queue = set()
        self._remove_queue = set()

        self.init_buffer([screen.get_width() / 2, screen.get_height() / 2])

        self.tmx_data = load_map('level.tmx')
        map_data = pyscroll.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.buffer_size, (0, 0, 0))
        self.bg = load_image('exterior-parallaxBG1.png')

        geometry = []
        for obj in self.tmx_data.objectgroups[0]:
            bbox = (0, obj.x, obj.y, 0, obj.width, obj.height)
            geometry.append(bbox)

        self.physicsgroup = physics.PlatformerPhysicsGroup(1, TIMESTEP, GRAVITY, [], geometry)
        self.new_hero()

    def new_hero(self):
        hero = Hero()
        obj = self.tmx_data.get_object_by_name('hero')
        hero.body.bbox.move(0, obj.x, obj.y)
        self.add_actor(hero)
        self.hero = hero

    def add_actor(self, actor):
        if self.actors_lock.acquire(False):
            actor.group = self
            self.body_mapping[actor.body] = actor
            self.actors.add(actor)
            self.physicsgroup.add(actor.body)
            self.actors_lock.release()
        else:
            self._add_queue.add(actor)

    def remove_actor(self, actor):
        if self.actors_lock.acquire(False):
            actor.group = None
            del self.body_mapping[actor.body]
            self.actors.remove(actor)
            self.physicsgroup.remove(actor.body)
            self.actors_lock.release()
        else:
            self._remove_queue.add(actor)

    def init_buffer(self, size):
        self.map_buffer = pygame.Surface(size)
        self.buffer_size = self.map_buffer.get_size()

    def draw(self, surface):
        self.draw_bg(self.map_buffer)
        bx, by = self.map_buffer.get_size()
        cx_, cy_, cz_ = self.hero.body.bbox.bottomcenter
        cx = cy_
        cy = cz_ - 72
        sprites = []
        for actor in self.actors:
            rect = self.physicsgroup.to_rect(actor.body.bbox)
            d, w, h = self.hero.body.bbox.size
            xx, yy = rect.topleft
            xx = xx - cx + (bx / 2)
            yy = yy - cy + (by / 2)
            x = xx - self.hero.axis.y + (w / 2)
            y = yy - self.hero.axis.z
            sprites.append((actor.image, pygame.Rect(x, y, w, h), 0))

        self.map_layer.draw(self.map_buffer, surface.get_rect(), sprites)
        pygame.transform.scale(self.map_buffer, surface.get_size(), surface)

    def draw_bg(self, surface):
        surface.blit(self.bg, (0, 0))
        surface.blit(self.bg, (self.bg.get_width(), 0))

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

            self.hero.handle_input(event)

    def update(self, dt):
        self.time += dt

        x, y, z = self.hero.body.bbox.topcenter
        self.map_layer.center((y, z - 72))
        self.physicsgroup.update(dt)

        with self.actors_lock:
            for actor in self.actors:
                if actor.alive:
                    actor.update(dt)

                if actor.body.bbox.bottom > 1800:
                    actor.alive = False

                # do not add else here
                if not actor.alive:
                    self.remove_actor(actor)
                    if actor is self.hero:
                        self.new_hero()

        for actor in self._remove_queue:
            self.remove_actor(actor)

        for actor in self._add_queue:
            self.add_actor(actor)

        self._remove_queue = set()
        self._add_queue = set()

        if self.time >= 5000:
            self.time -= 5000
            bat = Bat()
            bat.body.bbox[:3] = (0, self.hero.body.bbox.y - 500, self.hero.body.bbox.z)
            self.add_actor(bat)

    def run(self):
        clock = pygame.time.Clock()
        play_music('dungeon')
        self.running = True

        try:
            while self.running:
                td = clock.tick(60)
                self.handle_input()
                self.update(td)
                self.update(td)
                self.update(td)
                self.draw(screen)
                pygame.display.flip()

        except KeyboardInterrupt:
            self.running = False

        pygame.mixer.music.stop()

    def actorcollide(self, actor):
        # return actor colliding with another actor
        for body in self.physicsgroup.test_collision_bbox(actor.body.bbox):
            yield self.body_mapping[body]

    def bboxcollide(self, bbox):
        # return actor colliding with bbox
        for body in self.physicsgroup.test_collision_bbox(bbox):
            yield self.body_mapping[body]


class CastleBatsSprite(pygame.sprite.Sprite):
    animations = {}
    sounds = {}

    def __init__(self):
        super().__init__()
        self.group = None
        self.axis = None
        self.image = None
        self.flip = False
        self.alive = True
        self.state = []
        self.animation_timer = 0
        self.current_animation = []

    @classmethod
    def load_animations(cls):
        s = load_image(cls.sprite_sheet)

        for name, ttl, tiles in cls.image_animations:
            frames = []
            for x1, y1, w, h, ax, ay in tiles:
                image = pygame.Surface((w, h))
                image.blit(s, (0, 0), (x1, y1, w, h))
                image.set_colorkey(image.get_at((0, 0)))
                frames.append((image, physics.Vector3(0, ax, ay)))
            cls.animations[name] = ttl, frames

    @classmethod
    def load_sounds(cls):
        for name in cls.required_sounds:
            cls.sounds[name] = load_sound(name)

    def update(self, dt):
        if self.animation_timer > 0:
            self.animation_timer -= dt
            if self.animation_timer <= 0:
                try:
                    self.set_frame(next(self.current_animation))
                except StopIteration:
                    self.set_animation('idle')

    def set_frame(self, frame):
        self.animation_timer, frame = frame
        self.image, axis = frame
        self.axis = axis.copy()
        if self.flip:
            w, h = self.image.get_size()
            self.image = pygame.transform.flip(self.image, 1, 0)
            self.axis.y = w - self.axis.y

    def set_animation(self, name, func=None):
        self.animation_timer, animation = self.animations[name]

        if func:
            if len(animation) == 1:
                animation = func(animation[0])
            else:
                animation = func(animation)

        self.current_animation = zip(itertools.repeat(self.animation_timer), animation)
        self.set_frame(next(self.current_animation))


class Hero(CastleBatsSprite):
    sprite_sheet = 'elisa-spritesheet1.png'
    required_sounds = ['sword']
    name = 'hero'

    image_animations = [
        ('idle',      100, ((10, 10, 34, 44, 15, 42), )),
        ('attacking', 250, ((34, 254, 52, 52, 15, 48), )),
        ('walking',   300, ((304, 132, 36, 40, 15, 38),
                            (190, 130, 28, 44, 14, 40),
                            (74, 132, 32, 40, 15, 38),
                            (190, 130, 28, 44, 14, 40))),
    ]

    def __init__(self):
        super().__init__()
        bbox = physics.BBox((0, 0, 0, 32, 32, 40))
        self.body = physics.Body3(bbox, (0, 0), (0, 0))
        self.load_animations()
        self.load_sounds()
        self.change_state('idle')

    def update(self, dt):
        super().update(dt)

    def change_state(self, state):
        self.state.append(state)

        if 'attacking' in self.state:
            self.sounds['sword'].stop()
            self.sounds['sword'].play()
            self.set_animation('attacking')
            self.state.remove('attacking')

            x, y, z = self.body.bbox[:3]
            x -= 30
            y -= 30
            z -= 30
            d, w, h = 60, 60, 60
            bbox = physics.BBox((x, y, z, d, w, h))
            for actor in self.group.bboxcollide(bbox):
                if actor is not self:
                    actor.alive = False

        elif 'walking' in self.state:
            self.set_animation('walking', itertools.cycle)

        elif 'idle' in self.state:
            self.set_animation('idle', itertools.repeat)

    def handle_input(self, event):
        # big ugly bunch of if statements... poor man's state machine
        try:
            button = KEY_MAP[event.key]
        except (KeyError, AttributeError):
            return

        if abs(self.body.vel.z) < .1:
            try:
                self.state.remove('jumping')
            except ValueError:
                pass

        if 'idle' in self.state:
            if event.type == KEYDOWN:
                if button == P1_LEFT:
                    self.state.remove('idle')
                    self.change_state('walking')
                    self.flip = True
                    self.body.vel.y = -MOVE_POWER
                elif button == P1_RIGHT:
                    self.state.remove('idle')
                    self.change_state('walking')
                    self.flip = False
                    self.body.vel.y = MOVE_POWER
                elif button == P1_UP and 'jumping' not in self.state:
                    self.change_state('jumping')
                    self.body.vel.z = -JUMP_POWER
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
                    self.body.vel.z = -JUMP_POWER


class Bat(CastleBatsSprite):
    sprite_sheet = 'bat.png'
    name = 'bat'

    image_animations = [
        ('flying',    700, ((8, 5, 19, 23, 15, 0), (42, 5, 19, 16, 16, 5))),
    ]

    def __init__(self):
        super().__init__()
        bbox = physics.BBox((0, 0, 0, 20, 20, 20))
        self.body = physics.Body3(bbox, (0, 0), (0, 0), gravity=False)
        self.load_animations()
        self.change_state('flying')
        self.body.vel.y = 1.0

    def change_state(self, state):
        self.state.append(state)

        if 'flying' in self.state:
            self.set_animation('flying', itertools.cycle)


if __name__ == '__main__':
    screen = init_screen(900, 500)
    pygame.display.set_caption('Castle Bats')
    pygame.font.init()
    pygame.mixer.init(buffer=0)

    game = Game()
    try:
        game.run()
    except:
        pygame.quit()
        raise

