from models.CarManager import CarManager


class Environment:
    def __init__(self, game, target_n_cars=0):
        self.game = game
        self.target_n_cars = target_n_cars
        self.car_mngs = list()
        self.cars_kf_repr = None
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

    def check_collisions(self):
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

