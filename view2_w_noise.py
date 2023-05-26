import sys
import time
import math
import pygame
import random
from models import Car, Vector2, ObjectSensor
from pygame.locals import *


class Game:
    def __init__(self):
        self.windowSize = (1200,800)
        self.freq = 20
        self.scale = 8
        self.last_refresh_time = 0
        self.controls = {
            K_UP: lambda: self.ego_car.control('UP'),
            K_DOWN: lambda: self.ego_car.control('DOWN'),
            K_RIGHT: lambda: self.ego_car.control('RIGHT'),
            K_LEFT: lambda: self.ego_car.control('LEFT'),
        }
        pygame.init()
    
    def setup(self):
        self.WINDOW = pygame.display.set_mode(self.windowSize) 
        self.CAPTION = pygame.display.set_caption('Collision detection')
        self.SCREEN = pygame.display.get_surface()
        pygame.display.update()
        self.ego_car = Car(position=Vector2(500,500), velocity=Vector2(0,0), scale=self.scale)
        self.sensor = ObjectSensor(self.ego_car, measurement_noise=1)

    def update_all(self):
        self.ego_car.update()
        self.sensor.measure()

    def draw_all(self):
        self.ego_car.draw_sprite(self.SCREEN)
        pygame.draw.circle(self.SCREEN, (0, 0, 0), self.sensor.last_position, 3)
        pygame.draw.line(self.SCREEN, (0, 0, 255), self.ego_car.position.get(),
                         self.ego_car.position.get() + 5*self.sensor.last_velocity,
                         3)
        pygame.draw.line(self.SCREEN, (255, 0, 0), self.ego_car.position.get(),
                         self.ego_car.position.get() + 50*self.sensor.last_acceleration,
                         3)

    def loop(self):
        print("Starting Main Loop")
        pygame.key.set_repeat(200, math.floor(1/self.freq))
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
            if now - self.last_refresh_time > 1./self.freq:
                self.SCREEN.fill((200, 200, 200))
                self.update_all()
                self.draw_all()
                pygame.display.update()
                self.last_refresh_time = now

def main():
    game = Game()
    game.setup()
    game.loop()

if __name__ == "__main__":
    main()