import math
import random
import numpy as np
from dataclasses import dataclass

import pygame
from pygame.locals import *


@dataclass
class Vector2:
    x: float = 0
    y: float = 0
    
    def __repr__(self):
        return self.x, self.y

    def get(self):
        return self.x, self.y
    
    @property
    def abs(self):
        return math.sqrt(self.x**2 + self.y**2)


@dataclass
class GameObject:
    position: Vector2
    velocity: Vector2
    speed: float = 0
    accel: float = 0
    rotation_angle: float = 0
    steering_angle: float = 0
    friction_coef: float = 0.008
    reverse: bool = False
    
    def update(self):
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y
        self.speed = self.velocity.abs * (-1 if self.reverse else 1)
        self.speed += self.accel 
        self.speed *= 1 - self.friction_coef
        self.velocity.x = self.speed * math.cos(self.rotation_angle)
        self.velocity.y = self.speed * math.sin(self.rotation_angle)
        self.rotation_angle += self.steering_angle * self.speed
        self.accel *= 0.9
        self.steering_angle *= 0.7
        #print(f"\r{self.accel:.3f}", end='')


class Car(GameObject):
    color_options = ["blue", "green", "pink", "red", "yellow"]
    accel_incr = 0.12
    brake_accel = 0.4
    steering_vel = 0.009
    max_accel: float = 0.5
    max_steering_angle: float = math.pi / 4
    
    def __init__(self, *args, scale=10, color=None, **kwargs):
        super().__init__(*args, **kwargs)
        color = random.choice(self.color_options)
        self.img = pygame.image.load(f"assets/{color}_car.png").convert_alpha()
        self.img = pygame.transform.scale(self.img, (3*scale, 5*scale))
        
        if color is None:
            color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        self.color = color
    
    def draw_sprite(self, surface):
        rot_img = pygame.transform.rotate(self.img, math.degrees(-self.rotation_angle - math.pi/2))
        surface.blit(rot_img, (
                                    self.position.x - self.img.get_size()[0]/2,
                                    self.position.y - self.img.get_size()[1]/2,
                                ) )
    
    def control(self, direction: str):        
        if direction == 'UP':
            if self.speed > 0:
                self.reverse = False
                self.accel += self.accel_incr
            else:
                self.accel += self.brake_accel
            self.accel = min(self.accel, self.max_accel)
        elif direction == 'DOWN':
            if self.speed < 0:
                self.reverse = True
                self.accel -= self.accel_incr
            else:
                self.accel -= self.brake_accel
            self.accel = max(self.accel, -self.max_accel)
        elif direction == 'RIGHT':
            self.steering_angle += self.steering_vel
        elif direction == 'LEFT':
            self.steering_angle -= self.steering_vel


class ObjectSensor:
    def __init__(self, obj: GameObject, measurement_noise: float):
        self.obj = obj
        self.measurement_noise = measurement_noise
        self.measurements = [np.array([0, 0]), np.array([0, 0]), np.array([0, 0])]
        self.last_position = np.array([0, 0])
        self.last_velocity = np.array([0, 0])
        self.last_acceleration = np.array([0, 0])

    def measure(self):
        noise = np.array([np.random.normal(0, self.measurement_noise),
                          np.random.normal(0, self.measurement_noise)])

        measured_position = np.array([self.obj.position.x, self.obj.position.y] + noise)

        # remove the oldest measurement and add new
        self.measurements.pop(0)
        self.measurements.append(measured_position)

        # calculate velocity and acceleration
        velocity = self.measurements[-2] - self.measurements[-3]
        accel = velocity - self.last_velocity

        # save state
        self.last_position = measured_position
        self.last_velocity = velocity
        self.last_acceleration = accel

        #print(f"{measured_position}, {velocity}, {accel}")
        return measured_position, velocity, accel
