import neat

def make_config(config_file, extra_info=None, custom_config=None):
    config = neat.Config(neat.DefaultGenome,
                         neat.DefaultReproduction,
                         neat.DefaultSpeciesSet,
                         neat.DefaultStagnation,
                         config_file,
                         extra_info=extra_info,
                         custom_config=custom_config)
    return config
