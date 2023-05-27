import sys
import time
import math
import pygame
import random

from models.Environment import Environment
from pygame.locals import *


class Game:
    def __init__(self):
        self.env = Environment(game=self, target_n_cars=10)
        self.windowSize = (1200, 800)
        self.interval = 1./20
        self.scale = 8
        self.last_refresh_time = 0
        self.controls = {
            # K_UP: lambda: self.ego_car.control('UP'),
            # K_DOWN: lambda: self.ego_car.control('DOWN'),
            # K_RIGHT: lambda: self.ego_car.control('RIGHT'),
            # K_LEFT: lambda: self.ego_car.control('LEFT'),
            K_q: lambda: sys.exit()
        }
        self.frame = 0
        pygame.init()
    
    def setup(self):
        self.WINDOW = pygame.display.set_mode(self.windowSize) 
        self.CAPTION = pygame.display.set_caption('Collision detection')
        self.SCREEN = pygame.display.get_surface()
        # pygame.key.set_repeat(200, 200)
        pygame.display.update()
        self.env.spawn_cars()

    def update(self):
        self.env.update_all()

    def draw(self):
        for car_mng in self.env.car_mngs:
            car_mng.car.draw_sprite(self.SCREEN)

        for car_kf_repr in self.env.cars_kf_repr:
            kf_center, kf_rect = car_kf_repr
            # pygame.draw.circle(self.SCREEN, (255, 0, 0), self.sensor.last_position, 3)
            pygame.draw.circle(self.SCREEN, (0, 0, 255), kf_center, 3)
            pygame.draw.rect(self.SCREEN, (0, 0, 255), kf_rect, 3)

        # pygame.draw.line(self.SCREEN, (0, 0, 255), self.ego_car.position.get(),
        #                  self.ego_car.position.get() + 5*self.sensor.last_velocity,
        #                  3)
        # pygame.draw.line(self.SCREEN, (255, 0, 0), self.ego_car.position.get(),
        #                  self.ego_car.position.get() + 50*self.sensor.last_acceleration,
        #                  3)

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
                    for control_key in self.controls.keys():
                        if keys[control_key]:
                            self.controls[control_key]()
            now = time.time()
            if now - self.last_refresh_time > self.interval:
                self.frame += 1
                self.SCREEN.fill((200, 200, 200))

                if self.frame % 10 == 0:
                    self.env.spawn_cars()

                if self.frame % 100 == 0:
                    self.env.get_report()

                self.update()
                self.draw()
                pygame.display.update()
                self.last_refresh_time = now


def main():
    game = Game()
    game.setup()
    game.loop()


if __name__ == "__main__":
    main()
