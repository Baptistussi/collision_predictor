# collision_predictor
Simple self-driving cars simulation using pygame applying Kalman Filters for avoiding collisions

## Preparing the environment:

$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt

## Running the simulation:

$ python main.py -c config/<config_file>.yaml

## Changing the settings:

You can edit or create new config files under config/ to tweak parameters on the simulation.
A reference for all possible options is in default.yaml
Avoid changing default.yaml (specially deleting options) since this file is used as a reference whenever you run any other simulation.

## Work in progress

This program is yet incomplete, future changes include:

- Correcting conceptual mistakes on the Kalman Filter class
- Writing a better collision detection algorithm
- Creating a simple control system to allow the cars to seek a flag
- Write better decision making when a future collision is detected. Currently, it just brakes the car.