import math
import time
import random
import numpy as np

import pygame
from pygame.locals import *

from kalman import CarSystemKF
from models.Basics import GameObject, Vector2
from models.Sensor import ObjectSensor


class Car(GameObject):
    color_options = ["blue", "green", "pink", "red", "yellow"]
    accel_incr = 0.12
    brake_accel = 0.4
    steering_vel = 0.009
    max_accel: float = 0.5
    max_steering_angle: float = math.pi / 4
    
    def __init__(self, *args, scale=10, **kwargs):
        super().__init__(*args, **kwargs)
        self.crashed = False
        self.crashed_time = None
        self.scale = scale
        color = random.choice(self.color_options)
        self.img = pygame.image.load(f"assets/{color}_car.png").convert_alpha()
        self.img = pygame.transform.scale(self.img, (3*scale, 5*scale))

        self.controls = {
            K_UP: lambda: self.control('UP'),
            K_DOWN: lambda: self.control('DOWN'),
            K_RIGHT: lambda: self.control('RIGHT'),
            K_LEFT: lambda: self.control('LEFT')
        }

    def __repr__(self):
        return f"{self.edges}"

    @property
    def size(self):
        return self.img.get_size()

    @property
    def edges(self):
        return (
            (self.position.x - self.size[0] / 2, self.position.y - self.size[1] / 2),
            (self.position.x - self.size[0] / 2, self.position.y + self.size[1] / 2),
            (self.position.x + self.size[0] / 2, self.position.y - self.size[1] / 2),
            (self.position.x + self.size[0] / 2, self.position.y + self.size[1] / 2),
        )

    @property
    def edges_split(self):
        return (
            (self.position.x + self.size[0] / 2, self.position.x - self.size[0] / 2),
            (self.position.y + self.size[1] / 2, self.position.y - self.size[1] / 2)
        )

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

    def update_collision(self):
        if not self.crashed:
            self.crashed = True
            self.crashed_time = time.time()
            self.img = pygame.image.load(f"assets/crash.png").convert_alpha()
            self.img = pygame.transform.scale(self.img, (8 * self.scale, 8 * self.scale))


class CarManager:
    def __init__(self, env, randomize=False, interval=1/20, measurement_noise=5):
        self.env = env
        self.kf_center = None
        self.kf_rect = None

        if randomize:
            position = Vector2(random.randint(1, env.game.windowSize[0]),
                               random.randint(1, env.game.windowSize[1]))
            velocity = Vector2(0, 0)
            accel = 1
            steering_angle = random.random() * 2 * math.pi
        else:
            position = Vector2(500, 500)
            velocity = Vector2(0, 0)
            accel = 0
            steering_angle = 0

        self.car = Car(position, velocity, accel=accel, steering_angle=steering_angle, scale=env.game.scale)
        self.sensor = ObjectSensor(self.car, measurement_noise=measurement_noise)
        self.kalman_filter = CarSystemKF(self, dt=interval)

    def update(self):
        # check for collision
        if self.car.crashed and time.time() - self.car.crashed_time > 0.4:
            self.delete()

        # check for leaving the window
        car_edges_x = self.car.edges_split[0]
        car_edges_y = self.car.edges_split[1]
        if max(car_edges_x) < 0 or \
                min(car_edges_x) > self.env.game.windowSize[0] or \
                max(car_edges_y) < 0 or \
                min(car_edges_y) > self.env.game.windowSize[1]:
            self.delete()

        self.car.update()
        measure = self.sensor.measure()
        mean, var = self.kalman_filter.update(measure)

        # Make Kalman Filter result representation:
        kf_repr = self.make_repr(mean, var)

        return kf_repr

    @staticmethod
    def make_repr(mean, var, var_multiplier=30):
        center = (mean[0][0], mean[3][0])
        var = (var[0][0] * var_multiplier, var[3][3] * var_multiplier)
        point = (center[0], center[1])
        rect = (center[0] - var[0] / 2, center[1] - var[1] / 2, var[0], var[1])

        return point, rect

    def delete(self):
        self.env.alive_cars_count -= 1
        if self in self.env.car_mngs:
            self.env.car_mngs.remove(self)


class SelfDrivingCarManager(CarManager):
    def __init__(self, *args, look_ahead_time: float = 10, **kwargs):
        super().__init__(*args,  **kwargs)
        '''
        This Kalman Filter instance is set with a greater dt, thus it can make predictions of further ahead position
        It's not used to update with current measures since that's already done by the regular Kalman Filter on the
        parent object.
        '''
        self.predictor_kf: CarSystemKF = CarSystemKF(self, dt=look_ahead_time)  # this kf instance is set to predict

    def update(self):
        super().update()
        ut = np.zeros((1, 1))
        last_mean, last_sigma = self.kalman_filter.kf.last_mean, self.kalman_filter.kf.last_sigma
        predicted_mean, predicted_sigma = self.predictor_kf.kf.predict(ut, last_mean=last_mean, last_sigma=last_sigma)

        # Make predictor Kalman Filter result representation:
        future_repr = self.make_repr(predicted_mean, predicted_sigma, 1)

        return future_repr
