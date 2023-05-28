import numpy as np
from models.Basics import GameObject


class ObjectSensor:
    def __init__(self, obj: GameObject, measurement_noise: float):
        self.obj = obj
        self.measurement_noise = measurement_noise
        self.measurements = []
        self.last_position = np.array([0, 0])
        self.last_velocity = np.array([0, 0])
        self.last_acceleration = np.array([0, 0])

    def measure(self):
        noise = np.array([np.random.normal(0, self.measurement_noise),
                          np.random.normal(0, self.measurement_noise)])

        measured_position = np.array([self.obj.position.x, self.obj.position.y] + noise)

        # remove the oldest measurement and add new
        self.measurements.insert(0, measured_position)
        if len(self.measurements) > 3:
            self.measurements.pop(-1)

        # calculate velocity and acceleration
        velocity, accel = None, None
        if len(self.measurements) >= 2:
            velocity = self.measurements[0] - self.measurements[1]
        if len(self.measurements) >= 3:
            accel = velocity - self.last_velocity


        # update state
        self.last_position = measured_position
        if velocity is not None:
            self.last_velocity = velocity
        if accel is not None:
            self.last_acceleration = accel

        #print(f"{measured_position}, {velocity}, {accel}")
        return self.last_position, self.last_velocity, self.last_acceleration

    def get_last(self):
        return self.last_position, self.last_velocity, self.last_acceleration