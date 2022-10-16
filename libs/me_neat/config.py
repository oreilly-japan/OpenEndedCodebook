import os
from configparser import ConfigParser

import neat_cppn
from neat_cppn.config import ConfigParameter, UnknownConfigItemError, write_pretty_params

def make_config(config_file, extra_info=None, custom_config=None):
    config = MEConfig(neat_cppn.DefaultGenome,
                      config_file,
                      extra_info=extra_info,
                      custom_config=custom_config)
    return config


class MEConfig:
    """A simple container for user-configurable parameters of ME-NEAT."""

    __params = [ConfigParameter('offspring_size', int),
                ConfigParameter('fitness_criterion', str),
                ConfigParameter('fitness_threshold', float),
                ConfigParameter('no_fitness_termination', bool, False)]

    def __init__(self, genome_type, filename, extra_info=None, custom_config=None):
        # Check that the provided types have the required methods.
        assert hasattr(genome_type, 'parse_config')

        self.genome_type = genome_type

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

        # ME-NEAT configuration
        if not parameters.has_section('ME-NEAT'):
            raise RuntimeError("'ME-NEAT' section not found in ME-NEAT configuration file.")

        param_list_names = []
        for p in self.__params:
            if p.default is None:
                setattr(self, p.name, p.parse('ME-NEAT', parameters))
            else:
                try:
                    setattr(self, p.name, p.parse('ME-NEAT', parameters))
                except Exception:
                    setattr(self, p.name, p.default)
                    warnings.warn("Using default {!r} for '{!s}'".format(p.default, p.name),
                                  DeprecationWarning)
            param_list_names.append(p.name)
        param_dict = dict(parameters.items('ME-NEAT'))
        unknown_list = [x for x in param_dict if x not in param_list_names]
        if unknown_list:
            if len(unknown_list) > 1:
                raise UnknownConfigItemError("Unknown (section 'ME-NEAT') configuration items:\n" +
                                             "\n\t".join(unknown_list))
            raise UnknownConfigItemError(
                "Unknown (section 'ME-NEAT') configuration item {!s}".format(unknown_list[0]))

        # Parse type sections.
        genome_dict = dict(parameters.items(genome_type.__name__))
        self.genome_config = genome_type.parse_config(genome_dict)

    def save(self, filename):
        with open(filename, 'w') as f:
            f.write('# The `ME-NEAT` section specifies parameters particular to the ME-NEAT algorithm\n')
            f.write('# or the experiment itself.  This is the only required section.\n')
            f.write('[ME-NEAT]\n')
            write_pretty_params(f, self, self.__params)

            f.write('\n[{0}]\n'.format(self.genome_type.__name__))
            self.genome_type.write_config(f, self.genome_config)
