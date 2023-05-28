import math
from dataclasses import dataclass


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
        return math.sqrt(self.x ** 2 + self.y ** 2)


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
        # print(f"\r{self.accel:.3f}", end='')
