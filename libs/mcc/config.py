import os
from configparser import ConfigParser

from neat_cppn.config import ConfigParameter, UnknownConfigItemError, write_pretty_params

def make_config(genome1, genome2, config_file, extra_info=None, custom_config=None):
    config = MCCConfig(genome1,
                       genome2,
                       config_file,
                       extra_info=extra_info,
                       custom_config=custom_config)
    return config


class MCCConfig(object):
    """A simple container for user-configurable parameters of MCC."""

    __params = [ConfigParameter('generation', int),
                ConfigParameter('genome1_pop_size', int),
                ConfigParameter('genome2_pop_size', int),
                ConfigParameter('genome1_criterion', int),
                ConfigParameter('genome2_criterion', int),
                ConfigParameter('genome1_offspring_size', int),
                ConfigParameter('genome2_offspring_size', int),
                ConfigParameter('genome1_limit', int),
                ConfigParameter('genome2_limit', int)]

    def __init__(self, genome1_type, genome2_type, filename, extra_info=None, custom_config=None):
        # Check that the provided types have the required methods.
        assert hasattr(genome1_type, 'parse_config')
        assert hasattr(genome2_type, 'parse_config')


        self.genome1_type = genome1_type
        self.genome2_type = genome2_type

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

        # MCC configuration
        if not parameters.has_section('MCC'):
            raise RuntimeError("'MCC' section not found in MCC configuration file.")

        param_list_names = []
        for p in self.__params:
            if p.default is None:
                setattr(self, p.name, p.parse('MCC', parameters))
            else:
                try:
                    setattr(self, p.name, p.parse('MCC', parameters))
                except Exception:
                    setattr(self, p.name, p.default)
                    warnings.warn("Using default {!r} for '{!s}'".format(p.default, p.name),
                                  DeprecationWarning)
            param_list_names.append(p.name)
        param_dict = dict(parameters.items('MCC'))
        unknown_list = [x for x in param_dict if x not in param_list_names]
        if unknown_list:
            if len(unknown_list) > 1:
                raise UnknownConfigItemError("Unknown (section 'MCC') configuration items:\n" +
                                             "\n\t".join(unknown_list))
            raise UnknownConfigItemError(
                "Unknown (section 'MCC') configuration item {!s}".format(unknown_list[0]))

        # Parse type sections.
        genome1_dict = dict(parameters.items(genome1_type.__name__))
        self.genome1_config = genome1_type.parse_config(genome1_dict)

        genome2_dict = dict(parameters.items(genome2_type.__name__))
        self.genome2_config = genome2_type.parse_config(genome2_dict)

    def save(self, filename):
        with open(filename, 'w') as f:
            f.write('# The `MCC` section specifies parameters particular to the MCC algorithm\n')
            f.write('# or the experiment itself.  This is the only required section.\n')
            f.write('[MCC]\n')
            write_pretty_params(f, self, self.__params)

            f.write('\n[{0}]\n'.format(self.genome1_type.__name__))
            self.genome1_type.write_config(f, self.genome1_config)

            f.write('\n[{0}]\n'.format(self.genome2_type.__name__))
            self.genome2_type.write_config(f, self.genome2_config)
