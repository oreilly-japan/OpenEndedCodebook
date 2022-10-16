import math
import itertools
import random

from neat_cppn.config import ConfigParameter, write_pretty_params

class PathGene:
    def __init__(self, key, start_gene=False):
        self.key = key
        self.start_gene = start_gene
        self.pathpoint = None
        self.horizontal = None

    def __str__(self):
        direction = 'h' if self.horizontal else 'v'
        s = f'(({self.pathpoint[0]},{self.pathpoint[1]}),{direction})'
        return s

    def copy(self):
        new_gene = self.__class__(self.key, self.start_gene)
        new_gene.pathpoint = self.pathpoint
        new_gene.horizontal = self.horizontal
        return new_gene

    def init_attributes(self, width, height):
        if self.start_gene:
            self.pathpoint = (0,0)
        else:
            self.pathpoint = (random.randrange(0,width), random.randrange(0,height))
        self.horizontal = bool(random.getrandbits(1))

    def mutate(self, config):
        if not self.start_gene:
            shift = random.choice(config.path_shift_candidates)
            self.pathpoint = (self.pathpoint[0]+shift[0], self.pathpoint[1]+shift[1])
        self.horizontal = bool(random.getrandbits(1))

class WallGene:
    def __init__(self, key, depth):
        self.key = key
        self.wall_location = None
        self.passage_location = None
        self.horizontal = None

    def __str__(self):
        direction = 'h' if self.horizontal else 'v'
        s = f'({self.wall_location: =.1f},{self.passage_location: =.1f},{direction})'
        return s

    def copy(self):
        new_gene = self.__class__(self.key, self.depth)
        new_gene.wall_location = self.wall_location
        new_gene.passage_location = self.passage_location
        new_gene.horizontal = self.horizontal

    def init_attributes(self):
        self.wall_location = min(0.9999, random.random())
        self.passage_location = min(0.9999, random.random())
        self.horizontal = bool(random.getrandbits(1))

    def mutate(self, config):
        scale = config.wall_mutate_scale
        self.wall_location = max(0, min(0.9999, self.wall_location + random.uniform(-scale,scale)))
        self.passage_location = max(0, min(0.9999, self.passage_location + random.uniform(-scale,scale)))
        self.horizontal = bool(random.getrandbits(1))



class MazeGenomeConfig:
    """Sets up and holds configuration information for the MazeGenome class."""

    def __init__(self, params):

        self._params = [ConfigParameter('init_maze_width', int),
                        ConfigParameter('init_maze_height', int),
                        ConfigParameter('wall_add_prob', float),
                        ConfigParameter('wall_delete_prob', float),
                        ConfigParameter('wall_mutate_prob', float),
                        ConfigParameter('path_add_prob', float),
                        ConfigParameter('path_delete_prob', float),
                        ConfigParameter('path_mutate_prob', float),
                        ConfigParameter('expand_width_prob', float),
                        ConfigParameter('expand_height_prob', float),
                        ConfigParameter('wall_mutate_prob_individ', float),
                        ConfigParameter('wall_mutate_scale', float),
                        ConfigParameter('path_shift_range', int),
                        ConfigParameter('single_structural_mutation', bool, 'true'),
                        ConfigParameter('region_max_width', int),
                        ConfigParameter('region_max_height', int),
                        ConfigParameter('region_min_width', int),
                        ConfigParameter('region_min_height', int),
                        ConfigParameter('maze_scaler', int),
                        ConfigParameter('max_timesteps', int)]


        # Use the configuration data to interpret the supplied parameters.
        for p in self._params:
            setattr(self, p.name, p.interpret(params))

        self.path_indexer = itertools.count(0)
        self.wall_indexer = itertools.count(0)

        self.mutate_options = {
            'mutate_wall_attributes': {
                'func_name': 'mutate_wall_attr',
                'prob': self.wall_mutate_prob,
            },
            'mutate_add_wall': {
                'func_name': 'mutate_add_wall',
                'prob': self.wall_add_prob,
            },
            'mutate_delete_wall': {
                'func_name': 'mutate_delete_wall',
                'prob': self.wall_delete_prob,
            },
            'mutate_path_attributes': {
                'func_name': 'mutate_path_attr',
                'prob': self.path_mutate_prob,
            },
            'mutate_add_path': {
                'func_name': 'mutate_add_path',
                'prob': self.path_add_prob,
            },
            'mutate_delete_path': {
                'func_name': 'mutate_delete_path',
                'prob': self.path_delete_prob,
            },
            'mutate_expand_width': {
                'func_name': 'mutate_expand_width',
                'prob': self.expand_width_prob,
            },
            'mutate_expand_height': {
                'func_name': 'mutate_expand_height',
                'prob': self.expand_height_prob,
            },
        }

        rng = self.path_shift_range
        rad = 2*rng+1
        self.path_shift_candidates = [(i//rad-rng, i%rad-rng) for i in range(rad**2) if i!=(2*rad+rng)]

    def save(self, f):
        write_pretty_params(f, self, self._params)

    def get_new_path_key(self):
        new_id = next(self.path_indexer)
        return new_id

    def get_new_wall_key(self):
        new_id = next(self.wall_indexer)
        return new_id



class MazeGenome:

    @classmethod
    def parse_config(cls, param_dict):
        param_dict['wall_gene_type'] = WallGene
        param_dict['path_gene_type'] = PathGene
        return MazeGenomeConfig(param_dict)

    @classmethod
    def write_config(cls, f, config):
        config.save(f)

    def __str__(self):
        s = f'Key: {self.key}\nFitness: {self.fitness: =.3f}'
        s += f'\nMaze size: ({self.maze_size[0]},{self.maze_size[1]})'
        s += '\nWall:'
        for wall_gene in self.wall_genes:
            s += f' {wall_gene}'
        s += '\nPath:'
        for path_gene in self.path_genes:
            s += f' {path_gene}'
        return s

    def __init__(self, key):
        self.key = key
        self.maze_size = None
        self.wall_genes = []
        self.path_genes = []
        self.fitness = None

        self.subregion_num = None

    def configure_new(self, config):
        self.maze_size = [config.init_maze_width, config.init_maze_height]
        self.wall_genes.append(self.create_wall(config.get_new_wall_key()))
        self.path_genes.insert(0, self.create_path(0, start_gene=True))

    def create_path(self, path_key, start_gene=False):
        gene = PathGene(path_key, start_gene=start_gene)
        gene.init_attributes(self.maze_size[0], self.maze_size[1])
        return gene

    def create_wall(self, wall_key):
        gene = WallGene(wall_key, depth=int(math.log2(len(self.wall_genes)+1))+1)
        gene.init_attributes()
        return gene

    def mutate(self, config):
        if config.single_structural_mutation:

            options = [option['func_name'] for option in config.mutate_options.values()]
            weights = [option['prob'] for option in config.mutate_options.values()]

            valid = False
            while not valid:
                mutate_func_name = random.choices(options, k=1, weights=weights)[0]

                mutate_func = getattr(self, mutate_func_name, None)
                assert mutate_func is not None, f'{mutate_func_name} is not defined in MazeGenome class'

                valid = mutate_func(config)

        else:
            for mutate_option in config.mutate_options.values():
                if random.random()<mutate_option['prob']:
                    mutate_func_name = mutate_option['func_name']

                    mutate_func = getattr(self, mutate_func_name, None)
                    assert mutate_func is not None, f'{mutate_func_name} is not defined in MazeGenome class'

                    mutate_func(config)

    def mutate_wall_attr(self, config):
        values = [random.random() for _ in range(len(self.wall_genes))]
        definitive_idx = random.randrange(0,len(self.wall_genes))
        values[definitive_idx] = 1
        for i in range(len(self.wall_genes)):
            if values[i] < config.wall_mutate_prob_individ:
                self.wall_genes[i].mutate(config)
        return True

    def mutate_add_wall(self, config):
        if self.subregion_num is not None and len(self.wall_genes)>=self.subregion_num:
            return False
        key = config.get_new_wall_key()
        insert_idx = random.randint(0,len(self.wall_genes))
        new_gene = self.create_wall(key)
        self.wall_genes.insert(insert_idx, new_gene)
        return True

    def mutate_delete_wall(self, config):
        if len(self.wall_genes)<2:
            return False

        delete_idx = random.randrange(0,len(self.wall_genes))
        del self.wall_genes[delete_idx]
        return True

    def mutate_path_attr(self, config):
        valid = False
        invalid_count = 0
        while not valid and invalid_count<50:
            path_attrs = [(path_gene.pathpoint, path_gene.horizontal) for path_gene in self.path_genes]

            mutate_idx = random.randrange(0,len(self.path_genes))

            clone = self.path_genes[mutate_idx].copy()
            # clone.mutate(config)
            clone.init_attributes(self.maze_size[0], self.maze_size[1])

            path_attrs[mutate_idx] = (clone.pathpoint, clone.horizontal)
            valid = self.check_path_validity(path_attrs, self.maze_size)

            invalid_count += 1

        if valid:
            self.path_genes[mutate_idx] = clone
        return valid

    def mutate_add_path(self, config):
        key = config.get_new_path_key()
        valid = False
        invalid_count = 0
        idx_candidates = list(range(1,len(self.path_genes)+1))
        while not valid and invalid_count<10:
            path_attrs = [(path_gene.pathpoint, path_gene.horizontal) for path_gene in self.path_genes]

            # insert_idx = random.randint(1,len(self.path_genes))
            insert_idx = random.choices(idx_candidates, k=1, weights=idx_candidates)[0]

            new_gene = self.create_path(key)
            path_attrs.insert(insert_idx, (new_gene.pathpoint, new_gene.horizontal))

            valid = self.check_path_validity(path_attrs, self.maze_size)

            invalid_count += 1

        if valid:
            self.path_genes.insert(insert_idx, new_gene)
        return valid

    def mutate_delete_path(self, config):
        if len(self.path_genes)<2:
            return False

        valid = False
        invalid_count = 0
        while not valid and invalid_count<50:
            path_attrs = [(path_gene.pathpoint, path_gene.horizontal) for path_gene in self.path_genes]

            delete_idx = random.randrange(1,len(self.path_genes))
            path_attrs.pop(delete_idx)

            valid = self.check_path_validity(path_attrs, self.maze_size)

            invalid_count += 1

        if valid:
            del self.path_genes[delete_idx]
        return valid

    def mutate_expand_width(self, config):
        self.maze_size[0] += 1
        return True

    def mutate_expand_height(self, config):
        self.maze_size[1] += 1
        return True

    def get_maze_area(self):
        return self.maze_size[0]*self.maze_size[1]

    def get_juncture_num(self):
        return len(self.path_genes) + \
            len([1 for i in range(len(self.path_genes)-1) if self.path_genes[i].horizontal==self.path_genes[i+1].horizontal])

    def get_path_length(self):
        return sum([abs(self.path_genes[i+1].pathpoint[0]-self.path_genes[i].pathpoint[0]) + \
                    abs(self.path_genes[i+1].pathpoint[1]-self.path_genes[i].pathpoint[1])\
                    for i in range(len(self.path_genes)-1)]) + \
                abs(self.maze_size[0]-1-self.path_genes[-1].pathpoint[0]) + abs(self.maze_size[1]-1-self.path_genes[-1].pathpoint[1])

    @staticmethod
    def check_path_validity(pathways, maze_size):

        point_history = []
        end_p = (maze_size[0]-1, maze_size[1]-1)
        end_horizontal = None

        for pathway in pathways[::-1]:
            cur_p = pathway[0]
            cur_horizontal = pathway[1]

            if cur_p[0]<0 or cur_p[1]<0 or cur_p[0]>=maze_size[0] or cur_p[1]>=maze_size[1]\
               or end_p==(0,0) or cur_p==(maze_size[0]-1, maze_size[1]-1)\
               or cur_p[0]==end_p[0] or cur_p[1]==end_p[1]:
                return False

            points = []
            if cur_horizontal:
                points.extend([x+cur_p[1]*maze_size[1] for x in range(cur_p[0], end_p[0], 1 if cur_p[0]<end_p[0] else -1)])
                points.extend([end_p[0]+y*maze_size[1] for y in range(cur_p[1], end_p[1], 1 if cur_p[1]<end_p[1] else -1)])
            else:
                points.extend([cur_p[0]+y*maze_size[1] for y in range(cur_p[1], end_p[1], 1 if cur_p[1]<end_p[1] else -1)])
                points.extend([x+end_p[1]*maze_size[1] for x in range(cur_p[0], end_p[0], 1 if cur_p[0]<end_p[0] else -1)])
            for p in points:
                if p in point_history:
                    return False
            point_history.extend(points)
            end_p = cur_p
            end_horizontal = cur_horizontal
        return True
