import sys
import yaml
import numpy as np
from game import Game
from models.Environment import Environment

np.set_printoptions(precision=3, suppress=True)

measurement_noise = 1
N = 1000

try:
    with open('config/default.yaml') as dcf:
        config = yaml.safe_load(dcf)
except:
    print("Default config missing")
    sys.exit()

game = Game(config)
game.setup()
env = Environment(game=game, target_n_cars=1)
env.spawn_cars(measurement_noise=measurement_noise, randomize=True)

measured_vectors = []
while N > 0:
    # input()
    N -= 1
    env.update_all()
    if len(env.car_mngs) > 0:
        m = env.car_mngs[0].sensor.get_last()  # last_measure
    state_vector = np.array([m[0][0], m[1][0], m[2][0], m[0][1], m[1][1], m[2][1]])
    # print(state_vector)
    measured_vectors.append(state_vector)
    if env.alive_cars_count == 0:
        print("car is gone")
        break

cov = np.cov(measured_vectors, rowvar=False)
print(cov.shape)
print(cov)