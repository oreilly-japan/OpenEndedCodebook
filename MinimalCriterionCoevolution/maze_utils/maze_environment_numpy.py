import numpy as np

MAX_AGENT_SPEED = 5.0
MAX_ANGULAR_VELOCITY = 8.0


class Agent:
    def __init__(self, location, heading=0, speed=0, angular_vel=0, radius=5.0, range_finder_range=100.0):
        self.heading = heading
        self.speed = speed
        self.angular_vel = angular_vel
        self.radius = radius
        self.range_finder_range = range_finder_range
        self.location = location

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
        self.angular_vel  += (control_signals[0] - 0.5) * 2
        self.speed        += (control_signals[1] - 0.5) * 2

        self.speed = np.clip(self.speed, -MAX_AGENT_SPEED, MAX_AGENT_SPEED)
        self.angular_vel = np.clip(self.angular_vel, -MAX_ANGULAR_VELOCITY, MAX_ANGULAR_VELOCITY)

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
    def __init__(self, init_location, init_heading, walls, exit_point, exit_range=5.0):
        self.walls = walls
        self.exit_point = exit_point
        self.exit_range = exit_range
        self.init_location = init_location
        self.init_heading = init_heading
        self.agent = None
        self.exit_found = None

    def reset(self):
        self.agent = Agent(location=self.init_location, heading=self.init_heading)

        self.exit_found = False
        # The initial distance of agent from exit
        self.initial_distance = self.agent.distance_to_exit(self.exit_point)

        # Update sensors
        self.agent.update_rangefinder_sensors(self.walls)
        self.agent.update_radars(self.exit_point)

    def agent_distance_to_exit(self):
        return self.agent.distance_to_exit(self.exit_point)

    def create_net_inputs(self):
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
        self.agent.heading += self.agent.angular_vel
        self.agent.heading = self.agent.heading%360

        # find the next location of the agent
        new_loc = self.agent.location + vel

        if not self.test_wall_collision(new_loc):
            self.agent.location = new_loc

        # update agent's sensors
        self.agent.update_rangefinder_sensors(self.walls)
        self.agent.update_radars(self.exit_point)

        # check if agent reached exit point
        distance = self.agent.distance_to_exit(self.exit_point)
        self.exit_found = (distance < self.exit_range)

        return self.exit_found

    @staticmethod
    def make_environment(start_point, walls, exit_point, init_heading=0):
        return MazeEnvironment(
            init_location=np.array(start_point),
            init_heading=init_heading,
            walls=np.reshape(np.vstack(walls),(-1,2,2)),
            exit_point=np.array(exit_point)
        )
