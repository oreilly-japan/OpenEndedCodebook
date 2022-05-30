import neat
from neat.config import *
from .genome import DefaultGenome
from .reproduction import DefaultReproduction

def make_config(config_file, extra_info=None, custom_config=None):
    config = neat.Config(DefaultGenome,
                         DefaultReproduction,
                         neat.DefaultSpeciesSet,
                         neat.DefaultStagnation,
                         config_file,
                         extra_info=extra_info,
                         custom_config=custom_config)
    return config
