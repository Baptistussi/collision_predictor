import sys
import yaml
import argparse
from game import Game


def update_configs(default: dict, custom: dict):
    for k, v in custom.items():
        if isinstance(v, dict):
            if k not in default:
                default[k] = dict()
            update_configs(default[k], custom[k])
        else:
            default[k] = custom[k]

def main():
    try:
        with open('config/default.yaml') as dcf:
            config = yaml.safe_load(dcf)
    except:
        print("Default config missing")
        sys.exit()

    parser = argparse.ArgumentParser(
        prog='Collision predictor',
        description='Example project for learning Kalman filters'
    )
    parser.add_argument('-c', '--config')
    args = parser.parse_args()

    # Open and load the config file
    if args.config:
        with open(args.config) as cf:
            custom_config = yaml.safe_load(cf)
            update_configs(config, custom_config)

    game = Game(config)
    game.setup()
    game.loop()


if __name__ == "__main__":
    main()
