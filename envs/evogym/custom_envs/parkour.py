import numpy as np

from gym import error, spaces

from evogym import EvoWorld, WorldObject
from evogym.utils import *
from evogym.envs.base import EvoGymBase
from evogym.envs.traverse import StairsBase

from gym.envs.registration import register

register(
    id = 'Parkour-v0',
    entry_point = 'custom_envs.parkour:Parkour',
    max_episode_steps=500
)

class Parkour(StairsBase):

    def __init__(self, body, connections, terrain):

        # make world
        self.world = self.build(terrain)
        self.world.add_from_array('robot', body, 1, terrain['start_height']+1, connections=connections)

        # init sim
        StairsBase.__init__(self, self.world)

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
        reward = super().get_reward(robot_pos_init, robot_pos_final)
        
        # error check unstable simulation
        if done:
            # print("SIMULATION UNSTABLE... TERMINATING")
            reward -= 3.0

        # check if y coordinate is below lowest platform
        com = np.mean(robot_pos_final, 1)
        if com[1] < (3)*self.VOXEL_SIZE:
            reward -= 3.0
            done = True

        if com[0] > (self.world.grid_size.x)*self.VOXEL_SIZE:
            done = True

        # observation, reward, has simulation met termination conditions, debugging info
        return obs, reward, done, {}

    def reset(self):
        
        EvoGymBase.reset(self)

        # observation
        obs = np.concatenate((
            self.get_vel_com_obs("robot"),
            self.get_ort_obs("robot"),
            self.get_relative_pos_obs("robot"),
            self.get_floor_obs("robot", self.terrain_list, self.sight_dist),
            ))

        return obs




from evogym import is_connected, has_actuator, get_full_connectivity

def main():

    robot = np.array([
        [4, 4, 4, 4, 4],
        [4, 4, 4, 4, 4],
        [4, 4, 4, 4, 4],
        [4, 4, 4, 4, 4],
        [4, 4, 4, 4, 4]
    ])
    connectivity = get_full_connectivity(robot)
    # structure = (robot, connectivity)

    grid_size = (100, 1)
    blocks = [x for x in range(100)]
    types = [5]*100
    neighbors = {str(x): [x+1] if x==0 else [x-1] if x==99 else [x-1, x+1] for x in range(100)}

    terrain = {
        'grid_width': grid_size[0],
        'grid_height': grid_size[1],
        'objects': {
            'ground': {
                'indices': blocks,
                'types': types,
                'neighbors': neighbors,
            }
        }
    }


    env = Mutable(robot, connectivity, terrain)

    while True:
        action = env.action_space.sample()-1
        obs, reward, done, info = env.step(action)
        env.render()

        if done:
            env.reset()

    env.close()


if __name__=='__main__':
    main()