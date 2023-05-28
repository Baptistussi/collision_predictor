import math
import numpy as np
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


def check_collision(car_a, car_b):
    '''
    Check if car_a and car_b are in collision.
    Collision is detected when, on both x and y coordinates, the smallest point of the front car comes
    before the biggest point of the back car.
    '''
    car_a_edges_x = car_a.edges_split[0]
    car_a_edges_y = car_a.edges_split[1]
    car_b_edges_x = car_b.edges_split[0]
    car_b_edges_y = car_b.edges_split[1]

    def assure_first_smallest(first, second):
        if not min(first) < min(second):
            return second, first
        else:
            return first, second

    car_a_edges_x, car_b_edges_x = assure_first_smallest(car_a_edges_x, car_b_edges_x)
    car_a_edges_y, car_b_edges_y = assure_first_smallest(car_a_edges_y, car_b_edges_y)

    return max(car_a_edges_x) > min(car_b_edges_x) and max(car_a_edges_y) > min(car_b_edges_y)


def segments_distance(seg1, seg2):
    """
        distance between two segments in the plane:
        one segment is (x11, y11) to (x12, y12)
        the other is   (x21, y21) to (x22, y22)
    """

    if segments_intersect(seg1, seg2):
        return 0
    # try each of the 4 vertices w/the other segment
    distances = [
        point_segment_distance(seg1[0], seg2),
        point_segment_distance(seg1[1], seg2),
        point_segment_distance(seg2[0], seg1),
        point_segment_distance(seg2[1], seg1)
    ]
    return min(distances)


def segments_intersect(seg1, seg2):
    """
        whether two segments in the plane intersect:
        one segment is ((x11, y11) , (x12, y12))
        the other is   ((x21, y21) , (x22, y22))
    """
    ((x11, y11), (x12, y12)) = seg1
    ((x21, y21), (x22, y22)) = seg2
    dx1 = x12 - x11
    dy1 = y12 - y11
    dx2 = x22 - x21
    dy2 = y22 - y21
    delta = dx2 * dy1 - dy2 * dx1
    if delta == 0:
        return False  # parallel segments
    s = (dx1 * (y21 - y11) + dy1 * (x11 - x21)) / delta
    t = (dx2 * (y11 - y21) + dy2 * (x21 - x11)) / (-delta)
    return (0 <= s <= 1) and (0 <= t <= 1)


def point_segment_distance(p, seg):
    (px, py) = p
    ((x1, y1), (x2, y2)) = seg

    dx = x2 - x1
    dy = y2 - y1
    if dx == dy == 0:  # the segment's just a point
        return math.hypot(px - x1, py - y1)

    # Calculate the t that minimizes the distance.
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)

    # See if this represents one of the segment's
    # end points or a point in the middle.
    if t < 0:
        dx = px - x1
        dy = py - y1
    elif t > 1:
        dx = px - x2
        dy = py - y2
    else:
        near_x = x1 + t * dx
        near_y = y1 + t * dy
        dx = px - near_x
        dy = py - near_y

    return math.hypot(dx, dy)
