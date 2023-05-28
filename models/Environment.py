from models.Basics import segments_distance, check_collision
from models.CarManager import CarManager, SelfDrivingCarManager


class Environment:
    def __init__(self, game, target_n_cars=0):
        self.game = game
        self.target_n_cars = target_n_cars
        self.car_mngs = list()
        self.cars_kf_repr = list()
        # Stats:
        self.alive_cars_count = 0
        self.total_cars_count = 0
        self.collision_count = 0
    
    def spawn_cars(self, n_cars=None, **kwargs):
        if n_cars is None:
            n_cars = self.target_n_cars - self.alive_cars_count
        if 'randomize' not in kwargs:
            kwargs['randomize'] = True

        for _ in range(n_cars):
            self.car_mngs.append(CarManager(env=self, **kwargs))
        self.alive_cars_count += n_cars
        self.total_cars_count += n_cars

    def spawn_self_driving_cars(self, n_cars=None, **kwargs):
        if n_cars is None:
            n_cars = self.target_n_cars - self.alive_cars_count
        if 'randomize' not in kwargs:
            kwargs['randomize'] = True

        for _ in range(n_cars):
            self.car_mngs.append(SelfDrivingCarManager(env=self, **kwargs))
        self.alive_cars_count += n_cars
        self.total_cars_count += n_cars

    def check_collisions(self):
        cars = [car_mng.car for car_mng in self.car_mngs]
        for i in range(len(cars)):
            for j in range(i+1, len(cars)):
                if check_collision(cars[i], cars[j]):
                    if not cars[i].crashed and not cars[j].crashed:
                        self.collision_count += 1
                        print(f"{self.collision_count} collisions")
                    cars[i].update_collision()
                    cars[j].update_collision()

    def update_all(self):
        self.check_collisions()
        if len(self.car_mngs) > 0:
            self.cars_kf_repr = [car_mng.update() for car_mng in self.car_mngs]

    def get_report(self):
        print(f"cars alive: {self.alive_cars_count}\t total spawned cars: {self.total_cars_count}\t collisions: {self.collision_count}")

