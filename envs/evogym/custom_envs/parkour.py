import math
import numpy as np

from gym import error, spaces

from evogym import EvoWorld, WorldObject
from evogym.utils import *
from evogym.envs.base import EvoGymBase
from evogym.envs import BenchmarkBase

from gym.envs.registration import register

register(
    id = 'Parkour-v0',
    entry_point = 'custom_envs.parkour:Parkour',
    max_episode_steps=500
)

register(
    id = 'Parkour-v1',
    entry_point = 'custom_envs.parkour:ParkourFlip',
    max_episode_steps=500
)

class Parkour(BenchmarkBase):

    def __init__(self, body, connections, terrain):

        # make world
        self.world = self.build(terrain)
        self.world.add_from_array('robot', body, 1, terrain['start_height']+1, connections=connections)

        # init sim
        BenchmarkBase.__init__(self, self.world)

        # set action space and observation space
        num_actuators = self.get_actuator_indices('robot').size
        num_robot_points = self.object_pos_at_time(self.get_time(), "robot").size
        self.sight_dist = 10

        self.action_space = spaces.Box(low= 0.6, high=1.6, shape=(num_actuators,), dtype=np.float)
        self.observation_space = spaces.Box(low=-100.0, high=100.0, shape=(3 + num_robot_points + (2*self.sight_dist +1),), dtype=np.float)

        # terrain
        self.terrain_list = list(terrain['objects'].keys())

    def build(self, terrain):
        world = EvoWorld()

        file_grid_size = Pair(terrain['grid_width'], terrain['grid_height'])

        # read in objects
        for name, obj_data in terrain['objects'].items():

            obj = WorldObject()
            obj.load_from_parsed_json(name, obj_data, file_grid_size)
            world.add_object(obj)

        return world


    def step(self, action):

        # collect pre step information
        robot_pos_init = self.object_pos_at_time(self.get_time(), "robot")

        # step
        done = super().step({'robot': action})

        # collect post step information
        robot_pos_final = self.object_pos_at_time(self.get_time(), "robot")

        # observation
        obs = np.concatenate((
            self.get_vel_com_obs("robot"),
            self.get_ort_obs("robot"),
            self.get_relative_pos_obs("robot"),
            self.get_floor_obs("robot", self.terrain_list, self.sight_dist),
            ))
       
        # compute reward
        robot_com_pos_init = np.mean(robot_pos_init, axis=1)
        robot_com_pos_final = np.mean(robot_pos_final, axis=1)
        reward = (robot_com_pos_final[0] - robot_com_pos_init[0])
        
        # error check unstable simulation
        if done:
            # print("SIMULATION UNSTABLE... TERMINATING")
            reward -= 3.0

        # check if y coordinate is below lowest platform
        com = np.mean(robot_pos_final, 1)
        if com[1] < (5)*self.VOXEL_SIZE:
            reward -= 3.0
            done = True

        if com[0] > (self.world.grid_size.x)*self.VOXEL_SIZE:
            done = True

        # observation, reward, has simulation met termination conditions, debugging info
        return obs, reward, done, {}

    def reset(self):
        
        super().reset()

        # observation
        obs = np.concatenate((
            self.get_vel_com_obs("robot"),
            self.get_ort_obs("robot"),
            self.get_relative_pos_obs("robot"),
            self.get_floor_obs("robot", self.terrain_list, self.sight_dist),
            ))

        return obs



class ParkourFlip(BenchmarkBase):

    def __init__(self, body, connections, terrain):

        # make world
        self.world = self.build(terrain)
        self.world.add_from_array('robot', body, 1, terrain['start_height']+1, connections=connections)

        # init sim
        BenchmarkBase.__init__(self, self.world)

        # set action space and observation space
        num_actuators = self.get_actuator_indices('robot').size
        num_robot_points = self.object_pos_at_time(self.get_time(), "robot").size
        self.sight_dist = 10

        self.action_space = spaces.Box(low= 0.6, high=1.6, shape=(num_actuators,), dtype=np.float)
        self.observation_space = spaces.Box(low=-100.0, high=100.0, shape=(3 + num_robot_points + (2*self.sight_dist +1),), dtype=np.float)

        # terrain
        self.terrain_list = list(terrain['objects'].keys())

        self.num_flips = 0

    def build(self, terrain):
        world = EvoWorld()

        file_grid_size = Pair(terrain['grid_width'], terrain['grid_height'])

        # read in objects
        for name, obj_data in terrain['objects'].items():

            obj = WorldObject()
            obj.load_from_parsed_json(name, obj_data, file_grid_size)
            world.add_object(obj)

        return world


    def step(self, action):

        # collect pre step information
        pos_1 = self.object_pos_at_time(self.get_time(), "robot")
        ort_1 = self.object_orientation_at_time(self.get_time(), "robot")

        # step
        done = super().step({'robot': action})

        # collect post step information
        pos_2 = self.object_pos_at_time(self.get_time(), "robot")
        ort_2 = self.object_orientation_at_time(self.get_time(), "robot")

        # observation
        obs = np.concatenate((
            self.get_vel_com_obs("robot"),
            self.get_ort_obs("robot"),
            self.get_relative_pos_obs("robot"),
            self.get_floor_obs("robot", self.terrain_list, self.sight_dist),
            ))
       
        # compute reward
        com_1 = np.mean(pos_1, axis=1)
        com_2 = np.mean(pos_2, axis=1)
        move = (com_2[0] - com_1[0])

        # update flips
        flattened_ort_1 = self.num_flips + ort_1 / (2 * math.pi)
        # flattened_ort_1 = self.num_flips * 2 * math.pi + ort_1

        if ort_1 < math.pi/3 and ort_2 > 5*math.pi/3:
            self.num_flips -= 1
        if ort_1 > 5*math.pi/3 and ort_2 <  math.pi/3:
            self.num_flips += 1

        # if self.num_flips > -10:
        flattened_ort_2 = self.num_flips + ort_2 / (2 *  math.pi)
        # flattened_ort_2 = self.num_flips * 2 * math.pi + ort_2
        rotate = -(flattened_ort_2 - flattened_ort_1)

        reward = rotate if move>0 else -abs(rotate)
        reward += move if rotate>0 else -abs(move)

        # error check unstable simulation
        if done:
            reward -= -self.num_flips
            # reward -= 3.0

        # check if y coordinate is below lowest platform
        if com_2[1] < (5)*self.VOXEL_SIZE:
            # reward -= -self.num_flips
            reward -= 3.0
            done = True

        if com_2[0] > (self.world.grid_size.x)*self.VOXEL_SIZE:
            done = True

        # observation, reward, has simulation met termination conditions, debugging info
        return obs, reward, done, {}

    def reset(self):
        
        super().reset()

        self.num_flips = 0

        # observation
        obs = np.concatenate((
            self.get_vel_com_obs("robot"),
            self.get_ort_obs("robot"),
            self.get_relative_pos_obs("robot"),
            self.get_floor_obs("robot", self.terrain_list, self.sight_dist),
            ))

        return obs