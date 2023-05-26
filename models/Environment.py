from models.CarManager import CarManager


class Environment:
    def __init__(self, game, n_cars=0):
        self.game = game
        self.n_cars = n_cars
        self.car_mngs = list()
        self.cars_kf_repr = None
    
    def spawn_cars(self, n_cars=None):
        if n_cars is None:
            n_cars = self.n_cars
        for _ in range(n_cars):
            self.car_mngs.append(CarManager(self.game.scale, self.game.windowSize, randomize=True))

    def update_all(self):
        if len(self.car_mngs) > 0:
            self.cars_kf_repr = [car_mng.update() for car_mng in self.car_mngs]

