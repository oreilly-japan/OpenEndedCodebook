import os
import numpy as np

MAX_AGENT_SPEED = 3.0
MAX_ANGULAR_VELOCITY = 3.0

class Agent:
    def __init__(self, location, heading=0, radius=8.0, range_finder_range=100.0,
            max_speed=3.0, max_angular_vel=3.0, speed_scale=1.0, angular_scale=1.0):
        self.heading = heading
        self.radius = radius
        self.range_finder_range = range_finder_range
        self.location = location
        self.max_speed = max_speed
        self.max_angular_vel = max_angular_vel
        self.speed_scale = speed_scale
        self.angular_scale = angular_scale

        self.speed = 0
        self.angular_vel = 0

        # defining the range finder sensors
        self.range_finder_angles = np.array([-90.0, -45.0, 0.0, 45.0, 90.0, -180.0])

        # defining the radar sensors
        self.radar_angles = np.array([[315.0, 405.0], [45.0, 135.0], [135.0, 225.0], [225.0, 315.0]])

        # the list to hold range finders activations
        self.range_finders = None
        # the list to hold pie-slice radar activations
        self.radar = None

    def get_obs(self):
        obs = list(self.range_finders) + list(self.radar)
        return obs

    def apply_control_signals(self, control_signals):
        self.angular_vel  += (control_signals[0] - 0.5)*self.angular_scale
        self.speed        += (control_signals[1] - 0.5)*self.speed_scale

        self.speed = np.clip(self.speed, -self.max_speed, self.max_speed)
        self.angular_vel = np.clip(self.angular_vel, -self.max_angular_vel, self.max_angular_vel)

    def distance_to_exit(self, exit_point):
        return np.linalg.norm(self.location-exit_point)

    def update_rangefinder_sensors(self, walls):

        range_finder_angles = (self.range_finder_angles + self.heading) / 180 * np.pi

        A = np.expand_dims(walls[:,0,:], axis=0)
        B = np.expand_dims(walls[:,1,:], axis=0)

        location = np.expand_dims(self.location, axis=0)
        finder_points = location + self.range_finder_range * np.vstack([np.cos(range_finder_angles), np.sin(range_finder_angles)]).T

        C = np.expand_dims(location, axis=1)
        D = np.expand_dims(finder_points, axis=1)

        AC = A-C
        DC = D-C
        BA = B-A

        rTop = AC[:,:,1] * DC[:,:,0] - AC[:,:,0] * DC[:,:,1]
        sTop = AC[:,:,1] * BA[:,:,0] - AC[:,:,0] * BA[:,:,1]
        Bot = BA[:,:,0] * DC[:,:,1] - BA[:,:,1] * DC[:,:,0]

        with np.errstate(divide='ignore', invalid='ignore'):
            r = np.where(Bot==0, 0, rTop / Bot)
            s = np.where(Bot==0, 0, sTop / Bot)

        distances = np.where((Bot!=0) & (r>0) & (r<1) & (s>0) & (s<1),
            np.linalg.norm(A + np.expand_dims(r, axis=-1) * BA - C, axis=-1), self.range_finder_range)
        self.range_finders = np.min(distances, axis=1) / self.range_finder_range

    def update_radars(self, exit_point):
        exit_angle = np.arctan2(exit_point[0]-self.location[0], exit_point[1]-self.location[1]) % np.pi
        radar_angles = (self.radar_angles + self.heading) /180 *np.pi

        radar_range = radar_angles[:,1]-radar_angles[:,0]
        radar_diff = (exit_angle-radar_angles[:,0])%(2*np.pi)
        radar = np.zeros(self.radar_angles.shape[0])
        radar[radar_diff<radar_range] = 1
        self.radar = radar


class MazeEnvironment:
    def __init__(self, init_location, walls, exit_point, init_heading=180, exit_range=5.0, agent_kwargs={}):
        self.walls = walls
        self.exit_point = exit_point
        self.exit_range = exit_range
        self.init_location = init_location
        self.init_heading = init_heading
        self.agent_kwargs = agent_kwargs
        self.agent = None
        self.exit_found = None

    def reset(self):
        self.agent = Agent(location=self.init_location, heading=self.init_heading, **self.agent_kwargs)

        self.exit_found = False
        # The initial distance of agent from exit
        self.initial_distance = self.agent.distance_to_exit(self.exit_point)

        # Update sensors
        self.agent.update_rangefinder_sensors(self.walls)
        self.agent.update_radars(self.exit_point)

    def get_distance_to_exit(self):
        return self.agent.distance_to_exit(self.exit_point)

    def get_agent_location(self):
        return self.agent.location.copy()

    def get_observation(self):
        return self.agent.get_obs()

    def test_wall_collision(self, location):

        A = self.walls[:,0,:]
        B = self.walls[:,1,:]
        C = np.expand_dims(location, axis=0)
        BA = B-A

        uTop = np.sum( (C - A) * BA, axis=1)
        uBot = np.sum(np.square(BA), axis=1)

        u = uTop / uBot

        dist1 = np.minimum(
            np.linalg.norm(A - C, axis=1),
            np.linalg.norm(B - C, axis=1))
        dist2 = np.linalg.norm(A + np.expand_dims(u, axis=-1) * BA - C, axis=1)

        distances = np.where((u<0) | (u>1), dist1, dist2)

        return np.min(distances) < self.agent.radius


    def update(self, control_signals):
        if self.exit_found:
            # Maze exit already found
            return True

        # Apply control signals
        self.agent.apply_control_signals(control_signals)

        # get X and Y velocity components
        vel = np.array([np.cos(self.agent.heading/180*np.pi) * self.agent.speed,
                        np.sin(self.agent.heading/180*np.pi) * self.agent.speed])

        # Update current Agent's heading (we consider the simulation time step size equal to 1s
        # and the angular velocity as degrees per second)
        self.agent.heading = (self.agent.heading + self.agent.angular_vel) % 360

        # find the next location of the agent
        new_loc = self.agent.location + vel

        if not self.test_wall_collision(new_loc):
            self.agent.location = new_loc

        # update agent's sensors
        self.agent.update_rangefinder_sensors(self.walls)
        self.agent.update_radars(self.exit_point)

        # check if agent reached exit point
        distance = self.get_distance_to_exit()
        self.exit_found = (distance < self.exit_range)

        return self.exit_found

    @staticmethod
    def read_environment(ROOT_DIR, maze_name, maze_kwargs={}, agent_kwargs={}):
        """
        The function to read maze environment configuration from provided
        file.
        Arguments:
            file_path: The path to the file to read maze configuration from.
        Returns:
            The initialized maze environment.
        """
        maze_file = os.path.join(ROOT_DIR, 'envs', 'maze', 'maze_files', f'{maze_name}.txt')

        index = 0
        walls = []
        maze_agent, maze_exit = None, None
        with open(maze_file, 'r') as file:
            for line in file.readlines():
                line = line.strip()
                if len(line) == 0:
                    # skip empty lines
                    continue

                elif index == 0:
                    # read the agent's position
                    loc = np.array(list(map(float, line.split(' '))))
                elif index == 1:
                    # read the maze exit location
                    maze_exit = np.array(list(map(float, line.split(' '))))
                else:
                    # read the walls
                    wall = np.array(list(map(float, line.split(' '))))
                    walls.append(wall)

                # increment cursor
                index += 1

        walls = np.reshape(np.vstack(walls), (-1,2,2))

        # create and return the maze environment
        return MazeEnvironment(
            init_location=loc,
            walls=walls,
            exit_point=maze_exit,
            **maze_kwargs,
            agent_kwargs=agent_kwargs)

    @staticmethod
    def make_environment(start_point, walls, exit_point, maze_kwargs={}, agent_kwargs={}):
        return MazeEnvironment(
            init_location=np.array(start_point),
            walls=np.reshape(np.vstack(walls),(-1,2,2)),
            exit_point=np.array(exit_point),
            **maze_kwargs,
            agent_kwargs=agent_kwargs
        )
