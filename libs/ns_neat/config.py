import os
from configparser import ConfigParser

import neat_cppn
from neat_cppn.config import ConfigParameter, UnknownConfigItemError, write_pretty_params

def make_config(config_file, extra_info=None, custom_config=None):
    config = NSConfig(neat_cppn.DefaultGenome,
                      neat_cppn.DefaultReproduction,
                      neat_cppn.DefaultSpeciesSet,
                      neat_cppn.DefaultStagnation,
                      config_file,
                      extra_info=extra_info,
                      custom_config=custom_config)
    return config


class NSConfig:
    """A simple container for user-configurable parameters of NS-NEAT."""

    __params = [ConfigParameter('pop_size', int),
                ConfigParameter('fitness_criterion', str),
                ConfigParameter('fitness_threshold', float),
                ConfigParameter('reset_on_extinction', bool),
                ConfigParameter('no_fitness_termination', bool, False),

                ConfigParameter('metric', str),
                ConfigParameter('threshold_init', float),
                ConfigParameter('threshold_floor', float),
                ConfigParameter('neighbors', int),
                ConfigParameter('mcns', float)]

    def __init__(self, genome_type, reproduction_type, species_set_type, stagnation_type, filename, extra_info=None, custom_config=None):
        # Check that the provided types have the required methods.
        assert hasattr(genome_type, 'parse_config')
        assert hasattr(reproduction_type, 'parse_config')
        assert hasattr(species_set_type, 'parse_config')
        assert hasattr(stagnation_type, 'parse_config')

        self.genome_type = genome_type
        self.reproduction_type = reproduction_type
        self.species_set_type = species_set_type
        self.stagnation_type = stagnation_type

        if not os.path.isfile(filename):
            raise Exception('No such config file: ' + os.path.abspath(filename))

        self.extra_info = extra_info

        parameters = ConfigParser()
        with open(filename) as f:
            if hasattr(parameters, 'read_file'):
                parameters.read_file(f)
            else:
                parameters.readfp(f)

        if custom_config is not None:
            # [(section, key, value), ...]
            for cfg in custom_config:
                assert len(cfg) == 3, 'Invalid custom config input'
                section, key, value = cfg
                parameters[section][key] = str(value)

        # NS-NEAT configuration
        if not parameters.has_section('NS-NEAT'):
            raise RuntimeError("'NS-NEAT' section not found in NS-NEAT configuration file.")

        param_list_names = []
        for p in self.__params:
            if p.default is None:
                setattr(self, p.name, p.parse('NS-NEAT', parameters))
            else:
                try:
                    setattr(self, p.name, p.parse('NS-NEAT', parameters))
                except Exception:
                    setattr(self, p.name, p.default)
                    warnings.warn("Using default {!r} for '{!s}'".format(p.default, p.name),
                                  DeprecationWarning)
            param_list_names.append(p.name)
        param_dict = dict(parameters.items('NS-NEAT'))
        unknown_list = [x for x in param_dict if x not in param_list_names]
        if unknown_list:
            if len(unknown_list) > 1:
                raise UnknownConfigItemError("Unknown (section 'NS-NEAT') configuration items:\n" +
                                             "\n\t".join(unknown_list))
            raise UnknownConfigItemError(
                "Unknown (section 'NS-NEAT') configuration item {!s}".format(unknown_list[0]))

        # Parse type sections.
        genome_dict = dict(parameters.items(genome_type.__name__))
        self.genome_config = genome_type.parse_config(genome_dict)

        species_set_dict = dict(parameters.items(species_set_type.__name__))
        self.species_set_config = species_set_type.parse_config(species_set_dict)

        stagnation_dict = dict(parameters.items(stagnation_type.__name__))
        self.stagnation_config = stagnation_type.parse_config(stagnation_dict)

        reproduction_dict = dict(parameters.items(reproduction_type.__name__))
        self.reproduction_config = reproduction_type.parse_config(reproduction_dict)

    def save(self, filename):
        with open(filename, 'w') as f:
            f.write('# The `NS-NEAT` section specifies parameters particular to the NS-NEAT algorithm\n')
            f.write('# or the experiment itself.  This is the only required section.\n')
            f.write('[NS-NEAT]\n')
            write_pretty_params(f, self, self.__params)

            f.write('\n[{0}]\n'.format(self.genome_type.__name__))
            self.genome_type.write_config(f, self.genome_config)

            f.write('\n[{0}]\n'.format(self.species_set_type.__name__))
            self.species_set_type.write_config(f, self.species_set_config)

            f.write('\n[{0}]\n'.format(self.stagnation_type.__name__))
            self.stagnation_type.write_config(f, self.stagnation_config)

            f.write('\n[{0}]\n'.format(self.reproduction_type.__name__))
            self.reproduction_type.write_config(f, self.reproduction_config)
