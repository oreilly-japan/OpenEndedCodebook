
import os
import copy
from itertools import count
import json
import pickle
import numpy as np

import matplotlib.pyplot as plt

import neat_cppn

class EvogymTerrainDecoder(neat_cppn.BaseCPPNDecoder):
    def __init__(self, max_width, first_platform=10):
        self.max_width = max_width
        self.base_height = 7
        self.first_platform = first_platform

        self.input_keys = [
            'x', 'platform', 'voxel', 'wall'
        ]

        self.output_keys = {
            'platform':
                ['flat', 'height', 'width'],
            'voxel':
                ['rigid', 'soft', 'empty'],
        }

    def decode(self, genome, config, terrain_param):

        for output_key in config.output_keys[0:]:
            genome.nodes[output_key].activation = 'sin'

        cppn = neat_cppn.FeedForwardNetwork.create(genome, config)

        sorts = []
        seed = sum(cppn.activate([0,0,0,0]))/6+0.5
        rs = np.random.RandomState(int(seed*2**32)-1)
        for _ in range(3):
            sort = list(range(3))
            rs.shuffle(sort)
            sorts.append(sort)
        sort_func = lambda l,s: [l[i] for i in s]

        voxel_projection = {0: 5, 1: 2, 2: 0}
        
        x, y = 0, 0
        y_max, y_min = 0, 0
        platforms = {}
        points = [(x+i,y) for i in range(self.first_platform)]
        types = [5] * self.first_platform
        neighbors = {
            (x+i,y): [(x+i+1,y)] if i==0
            else [(x+i-1,y)] if i==self.first_platform-1
            else [(x+i-1,y),(x+i+1,y)] for i in range(self.first_platform)}
        x += self.first_platform
        platform_idx = 1
        prev_voxel = 5
        # encode to platform by cppn
        while x<self.max_width:
            input_x = x / self.max_width * 3

            # determine voxel type
            rigid, soft, empty = sort_func(cppn.activate([input_x,0,1,0]), sorts[1])
            rigid, soft, empty = (rigid+1)*terrain_param.rigid_bias, (soft+1)*terrain_param.soft_bias, (empty+1)*terrain_param.empty_bias
            voxel_type = voxel_projection[np.argmax(np.array([rigid, soft, empty]))]

            # determine about platform 
            flat, height, width = sort_func(cppn.activate([input_x,1,0,0]), sorts[0])
            height = round(height * flat**2 * terrain_param.max_up_step) if height>0 \
                else round(height * flat**2 * terrain_param.max_down_step)
            width = width / 2 + 0.5
            width = int(width * terrain_param.max_empty_width)+1 if voxel_type==0 \
                else int(width * (terrain_param.max_soft_width-1))+2 if voxel_type==2 \
                else int((1 - width**2) * terrain_param.max_rigid_width)+1
            width = min(width, self.max_width - x)

            # print(f'x: {x}, y: {y}, voxel: {voxel_type}, width: {width}, height: {height}')

            if prev_voxel != 0 and (voxel_type == 0 or height != 0):
                if prev_voxel == 2:
                    points.append((x,y))
                    types.append(5)
                    neighbors[(x-1,y)].append((x,y))
                    neighbors[(x,y)] = [(x-1,y)]
                    x += 1
                    if x > self.max_width:
                        prev_voxel = 5
                        break

                platforms[f'platfotm{platform_idx}'] = {
                    'points': points,
                    'types': types,
                    'neighbors_points': neighbors}
                platform_idx += 1
                points,types,neighbors = [], [], {}

            if voxel_type == 5:
                y += height
                points.extend([(x+i,y) for i in range(width)])
                types.extend([5]*width)
                continuous = prev_voxel != 0 and height == 0
                if continuous:
                    neighbors[(x-1,y)].append((x,y))
                neighbors.update({
                    (x+i,y): [] if not continuous and width==1
                    else [(x+i-1,y)] if i==width-1
                    else [(x+i+1,y)] if i==0 and not continuous
                    else [(x+i-1,y),(x+i+1,y)] for i in range(width)
                })

            elif voxel_type == 2:
                y += height

                continuous = prev_voxel == 5 and height == 0
                if prev_voxel == 2 and height == 0:
                    points.append((x,y))
                    types.append(5)
                    neighbors[(x-1,y)].append((x,y))
                    neighbors[(x,y)] = [(x-1,y)]
                    continuous = True
                    x += 1

                elif prev_voxel == 0 or height != 0:
                    points.append((x,y))
                    types.append(5)
                    neighbors[(x,y)] = []
                    continuous = True
                    x += 1

                points.extend([(x+i,y) for i in range(width)])
                types.extend([2]*width)
                if continuous:
                    neighbors[(x-1,y)].append((x,y))
                neighbors.update({
                    (x+i,y): [(x+i-1,y)] if i==width-1
                    else [(x+i+1,y)] if i==0 and not continuous
                    else [(x+i-1,y),(x+i+1,y)] for i in range(width)
                })

            y_min = min(y_min, y)
            y_max = max(y_max, y)

            x += width
            prev_voxel = voxel_type

        if len(points) == 0:
            points.append((x,y))
            types.append(5)
            neighbors[(x,y)] = []
            x += 1

        if len(points) > 0:
            if prev_voxel == 2:
                points.append((x,y))
                types.append(5)
                neighbors[(x-1,y)].append((x,y))
                neighbors[(x,y)] = [(x-1,y)]
                x += 1

            platforms[f'platfotm{platform_idx}'] = {
                'points': points,
                'types': types,
                'neighbors_points': neighbors}

        grid_width = x
        grid_height = y_max-y_min + self.base_height
        start_height = self.base_height - y_min

        for platform in platforms.values():
            points = platform.pop('points')
            neighbors_points = platform.pop('neighbors_points')

            platform['indices'] = [x+(y+start_height)*grid_width for x,y in points]
            platform['neighbors'] = {
                str(x1+(y1+start_height)*grid_width): 
                    [x2+(y2+start_height)*grid_width for x2,y2 in nei] 
                    for (x1,y1),nei in neighbors_points.items()
            }

        terrain = {
            'grid_width': grid_width,
            'grid_height': grid_height,
            'start_height': start_height,
            'objects': platforms
        }

        return terrain

class TerrainParams:
    def __init__(self, key,
                 rigid_bias=1,
                 soft_bias=0,
                 empty_bias=0,
                 max_rigid_width=10,
                 max_soft_width=3,
                 max_empty_width=1,
                 max_down_step=0,
                 max_up_step=0,):

        self.key = key
        self.rigid_bias = rigid_bias
        self.soft_bias = soft_bias
        self.empty_bias = empty_bias
        self.max_rigid_width = max_rigid_width
        self.max_soft_width = max_soft_width
        self.max_empty_width = max_empty_width
        self.max_down_step = max_down_step
        self.max_up_step = max_up_step

    def reproduce(self, key):
        rigid_bias      = max(0, min( 1, self.rigid_bias      + np.random.normal(0.05, 0.1)))
        soft_bias       = max(0, min( 1, self.soft_bias       + np.random.normal(0.05, 0.1)))
        empty_bias      = max(0, min( 1, self.empty_bias      + np.random.normal(0.05, 0.1)))
        max_rigid_width = max(1, min(10, self.max_rigid_width + np.random.normal(0.00, 0.8)))
        max_soft_width  = max(1, min( 8, self.max_soft_width  + np.random.normal(0.15, 0.8)))
        max_empty_width = max(1, min( 7, self.max_empty_width + np.random.normal(0.15, 0.8)))
        max_down_step   = max(0, min( 4, self.max_down_step   + np.random.normal(0.10, 0.2)))
        max_up_step     = max(0, min( 3, self.max_up_step     + np.random.normal(0.10, 0.2)))

        child = TerrainParams(
            key,
            max_down_step=max_down_step,
            max_up_step=max_up_step,
            rigid_bias=rigid_bias,
            soft_bias=soft_bias,
            empty_bias=empty_bias,
            max_rigid_width=max_rigid_width,
            max_soft_width=max_soft_width,
            max_empty_width=max_empty_width,
        )
        return child

    def save(self, path):
        filename = os.path.join(path, 'terrain_params.json')
        params = {
            'max_down_step': self.max_down_step,
            'max_up_step': self.max_up_step,
            'rigid_bias': self.rigid_bias,
            'soft_bias': self.soft_bias,
            'empty_bias': self.empty_bias,
            'max_rigid_width': self.max_rigid_width,
            'max_soft_width': self.max_soft_width,
            'max_empty_width': self.max_empty_width
        }
        with open(filename, 'w') as f:
            json.dump(params, f)


class EnvironmentEvogym:
    def __init__(self, key, cppn_genome, terrain_params):
        self.key = key
        self.cppn_genome = cppn_genome
        self.terrain_params = terrain_params
        self.terrain = None

    def make_terrain(self, decode_function, genome_config):
        terrain = decode_function(self.cppn_genome, genome_config, self.terrain_params)
        self.terrain = terrain
        for platform in terrain['objects'].values():
            indices = platform['indices']
            for i,nei in platform['neighbors'].items():
                for n in nei:
                    assert n in indices, f'{i}: n'

    def archive(self):
        pass

    def admitted(self, config):
        pass

    def save(self, path):
        cppn_file = os.path.join(path, 'cppn_genome.pickle')
        with open(cppn_file, 'wb') as f:
            pickle.dump(self.cppn_genome, f)

        self.terrain_params.save(path)

        terrain_json = os.path.join(path, 'terrain.json')
        with open(terrain_json, 'w') as f:
            json.dump(self.terrain, f)

        terrain_figure = os.path.join(path, 'terrain.jpg')
        self.save_terrain_figure(terrain_figure)

    def save_terrain_figure(self, filename):
        width, height = self.terrain['grid_width'], self.terrain['grid_height']+5
        fig, ax = plt.subplots(figsize=(width/8, height/8))
        for platform in self.terrain['objects'].values():
            for idx, t in zip(platform['indices'],platform['types']):
                x = idx % width
                y = idx // width

                if t==2:
                    color = [0.7,0.7,0.7]
                else:
                    color = 'k'
                ax.fill_between([x,x+1], [y+1, y+1], [y, y], fc=color)

        ax.set_xlim([0,width])
        ax.set_ylim([0,height])
        ax.grid()
        plt.savefig(filename, bbox_inches='tight')
        plt.close()

    def get_env_info(self, config):

        env_kwargs = dict(**config.robot, terrain=self.terrain)

        make_env_kwargs = {
            'env_id': config.env_id,
            'env_kwargs': env_kwargs,
            'seed': 0,
        }
        return make_env_kwargs

    def reproduce(self, config):
        key = config.get_new_env_key()
        child_cppn = config.reproduce_cppn_genome(self.cppn_genome)
        child_params = config.reproduce_terrain_params(self.terrain_params)
        child = EnvironmentEvogym(key, child_cppn, child_params)
        child.make_terrain(config.decode_cppn, config.neat_config.genome_config)
        return child



class EnvrionmentEvogymConfig:
    def __init__(self,
                 robot,
                 neat_config,
                 env_id='Parkour-v0',
                 max_width=80,
                 first_platform=10):

        self.env_id = env_id
        self.robot = robot
        self.neat_config = neat_config
        self.env_indexer = count(0)
        self.cppn_indexer = count(0)
        self.params_indexer = count(0)

        decoder = EvogymTerrainDecoder(max_width, first_platform=first_platform)
        self.decode_cppn = decoder.decode
    
    def get_new_env_key(self):
        return next(self.env_indexer)

    def make_init(self):
        cppn_key = self.get_new_env_key()
        cppn_genome = self.neat_config.genome_type(cppn_key)
        cppn_genome.configure_new(self.neat_config.genome_config)

        params_key = next(self.params_indexer)
        terrain_params = TerrainParams(params_key)

        env_key = next(self.env_indexer)
        environment = EnvironmentEvogym(env_key, cppn_genome, terrain_params)
        environment.make_terrain(self.decode_cppn, self.neat_config.genome_config)
        return environment

    def reproduce_cppn_genome(self, genome):
        key = next(self.cppn_indexer)
        child = copy.deepcopy(genome)
        child.mutate(self.neat_config.genome_config)
        child.key = key
        return child

    def reproduce_terrain_params(self, terrain_params):
        key = next(self.params_indexer)
        child = terrain_params.reproduce(key)
        return child