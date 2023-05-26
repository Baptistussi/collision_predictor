import math
import random
import numpy as np
from dataclasses import dataclass
from kalman import CarSystemKF

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
    
    def __init__(self, *args, scale=10, **kwargs):
        super().__init__(*args, **kwargs)
        color = random.choice(self.color_options)
        self.img = pygame.image.load(f"assets/{color}_car.png").convert_alpha()
        self.img = pygame.transform.scale(self.img, (3*scale, 5*scale))

    @property
    def size(self):
        return self.img.get_size()
    
    def draw_sprite(self, surface):
        rot_img = pygame.transform.rotate(self.img, math.degrees(-self.rotation_angle - math.pi/2))
        surface.blit(rot_img, (
                                    self.position.x - self.size[0]/2,
                                    self.position.y - self.size[1]/2,
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


class CarManager:
    def __init__(self, scale, window_size, randomize=False, interval=1/20, measurement_noise=5):
        self.kf_center = None
        self.kf_rect = None

        if randomize:
            position = Vector2(random.randint(1, window_size[0]),
                               random.randint(1, window_size[1]))
            velocity = Vector2(0, 0)
            accel = 1
            steering_angle = random.random() * 2 * math.pi
        else:
            position = Vector2(500, 500)
            velocity = Vector2(0, 0)
            accel = 0
            steering_angle = 0

        self.car = Car(position, velocity, accel=accel, steering_angle=steering_angle, scale=scale)
        self.sensor = ObjectSensor(self.car, measurement_noise=measurement_noise)
        self.kalman_filter = CarSystemKF(self.car, dt=interval)

    def update(self):
        self.car.update()
        measure = self.sensor.measure()
        mean, var = self.kalman_filter.update(measure)

        # Make Kalman Filter result representation:
        kf_center = (mean[0][0], mean[3][0])
        kf_var = (var[0][0] * 30, var[3][3] * 30)
        self.kf_rect = (kf_center[0] - kf_var[0] / 2, kf_center[1] - kf_var[1] / 2, kf_var[0], kf_var[1])
        self.kf_center = (kf_center[0], kf_center[1])

        return self.kf_center, self.kf_rect

