import sys
import time
import pygame
from models.Environment import Environment
from pygame.locals import *


class Game:
    def __init__(self, config):
        self.env = Environment(game=self, target_n_cars=config['sim']['target_n_cars'])
        self.config = config
        self.windowSize = config['game']['windowSize']
        self.interval = config['game']['interval']
        self.scale = config['game']['scale']
        self.last_refresh_time = 0
        self.controls = {
            K_UP: None,
            K_DOWN: None,
            K_RIGHT: None,
            K_LEFT: None,
            K_q: lambda: sys.exit()
        }
        self.frame = 0
        pygame.init()

    def setup(self):
        self.WINDOW = pygame.display.set_mode(self.windowSize)
        self.CAPTION = pygame.display.set_caption('Collision detection')
        self.SCREEN = pygame.display.get_surface()
        pygame.key.set_repeat(200, 200)
        pygame.display.update()
        self.env.spawn_cars(measurement_noise=self.config['sim']['measurement_noise'],
                            randomize=self.config['sim']['randomize'])

    def update(self):
        self.env.update_all()

    def draw(self):
        for car_mng in self.env.car_mngs:
            if self.config['game']['show']['car']:
                car_mng.car.draw_sprite(self.SCREEN)
            if self.config['game']['show']['pos']:
                pygame.draw.circle(self.SCREEN, (0, 0, 0), car_mng.sensor.last_position, 3)
            if self.config['game']['show']['vel']:
                pygame.draw.line(self.SCREEN, (0, 0, 255), car_mng.car.position.get(),
                                 car_mng.car.position.get() +
                                 self.config['game']['show']['vel_multiplier'] * car_mng.sensor.last_velocity, 3)
            if self.config['game']['show']['acc']:
                pygame.draw.line(self.SCREEN, (255, 0, 0), car_mng.car.position.get(),
                                 car_mng.car.position.get() +
                                 self.config['game']['show']['acc_multiplier'] * car_mng.sensor.last_acceleration, 3)

        for car_kf_repr in self.env.cars_kf_repr:
            kf_center, kf_rect = car_kf_repr
            if self.config['game']['show']['kf_mean']:
                pygame.draw.circle(self.SCREEN, (0, 0, 255), kf_center, 3)
            if self.config['game']['show']['kf_var']:
                pygame.draw.rect(self.SCREEN, (0, 0, 255), kf_rect, 3)

    def loop(self):
        print("Starting Main Loop")
        while True:
            # Event Detection
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if self.config['game']['enable_control']:
                        for control_key in self.controls.keys():
                            if keys[control_key]:
                                self.env.car_mngs[0].car.controls[control_key]()
            now = time.time()
            if now - self.last_refresh_time > self.interval:
                self.frame += 1
                self.SCREEN.fill((200, 200, 200))

                if self.frame % self.config['sim']['spawn_frame_interval'] == 0:
                    self.env.spawn_cars(measurement_noise=self.config['sim']['measurement_noise'],
                                        randomize=self.config['sim']['randomize'])

                if self.frame % self.config['sim']['report_frame_interval'] == 0:
                    self.env.get_report()

                self.update()
                self.draw()
                pygame.display.update()
                self.last_refresh_time = now

