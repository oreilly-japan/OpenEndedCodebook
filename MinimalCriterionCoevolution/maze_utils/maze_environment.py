#
# This is a definition of a maze environment simulation engine. It provides
# routines to read maze configuration and build related simulation environment
# from it. Also it provides method to simulate the behavior of the navigating agent
# and interaction with his sensors.
#
import math

import geometry

# The maximal allowed speed for the maze solver agent
MAX_AGENT_SPEED = 10.0
MAX_ANGULAR_VELOCITY = 15.0

class Agent:
    """
    This is the maze navigating agent
    """
    def __init__(self, location, heading=0, speed=0, angular_vel=0, radius=5.0, range_finder_range=100.0):
        """
        Creates new Agent with specified parameters.
        Arguments:
            location:               The agent initial position within maze
            heading:                The heading direction in degrees.
            speed:                  The linear velocity of the agent.
            angular_vel:            The angular velocity of the agent.
            radius:                 The agent's body radius.
            range_finder_range:     The maximal detection range for range finder sensors.
        """
        self.heading = heading
        self.speed = speed
        self.angular_vel = angular_vel
        self.radius = radius
        self.range_finder_range = range_finder_range
        self.location = location

        # defining the range finder sensors
        self.range_finder_angles = [-90.0, -45.0, 0.0, 45.0, 90.0, -180.0]

        # defining the radar sensors
        self.radar_angles = [(315.0, 405.0), (45.0, 135.0), (135.0, 225.0), (225.0, 315.0)]

        # the list to hold range finders activations
        self.range_finders = [None] * len(self.range_finder_angles)
        # the list to hold pie-slice radar activations
        self.radar = [None] * len(self.radar_angles)


class MazeEnvironment:
    """
    This class encapsulates the maze simulation environment.
    """
    def __init__(self, init_location, init_heading, walls, exit_point, exit_range=5.0):
        """
        Creates new maze environment with specified walls and exit point.
        Arguments:
            agent:      The maze navigating agent
            walls:      The maze walls
            exit_point: The maze exit point
            exit_range: The range arround exit point marking exit area
        """
        self.walls = walls
        self.exit_point = exit_point
        self.exit_range = exit_range
        self.init_location = init_location
        self.init_heading = init_heading
        self.agent = None
        self.location_sample_rate = -1
        self.exit_found = None

    def reset(self):
        self.agent = Agent(location=self.init_location, heading=self.init_heading)

        self.exit_found = False
        # The initial distance of agent from exit
        self.initial_distance = self.agent_distance_to_exit()

        # Update sensors
        self.update_rangefinder_sensors()
        self.update_radars()

    def agent_distance_to_exit(self):
        """
        The function to estimate distance from maze solver agent to the maze exit.
        Returns:
            The distance from maze solver agent to the maze exit.
        """
        return self.agent.location.distance(self.exit_point)

    def test_wall_collision(self, loc):
        """
        The function to test if agent at specified location collides with any
        of the maze walls.
        Arguments:
            loc: The new agent location to test for collision.
        Returns:
            The True if agent at new location will collide with any of the maze walls.
        """
        for w in self.walls:
            if w.distance(loc) < self.agent.radius:
                return True

        return False

    def create_net_inputs(self):
        """
        The function to create the ANN input values from the simulation environment.
        Returns:
            The list of ANN inputs consist of values get from solver agent sensors.
        """
        inputs = []
        # The range finders
        for ri in self.agent.range_finders:
            inputs.append(ri)

        # The radar sensors
        for rs in self.agent.radar:
            inputs.append(rs)

        return inputs

    def apply_control_signals(self, control_signals):
        """
        The function to apply control signals received from control ANN to the
        maze solver agent.
        Arguments:
            control_signals: The control signals received from the control ANN
        """
        self.agent.angular_vel  += (control_signals[0] - 0.5) * 5
        self.agent.speed        += (control_signals[1] - 0.5) * 5

        # constrain the speed & angular velocity
        if self.agent.speed > MAX_AGENT_SPEED:
            self.agent.speed = MAX_AGENT_SPEED

        if self.agent.speed < -MAX_AGENT_SPEED:
            self.agent.speed = -MAX_AGENT_SPEED

        if self.agent.angular_vel > MAX_ANGULAR_VELOCITY:
            self.agent.angular_vel = MAX_ANGULAR_VELOCITY

        if self.agent.angular_vel < -MAX_ANGULAR_VELOCITY:
            self.agent.angular_vel = -MAX_ANGULAR_VELOCITY

    def update_rangefinder_sensors(self):
        """
        The function to update the agent range finder sensors.
        """
        for i, angle in enumerate(self.agent.range_finder_angles):
            rad = geometry.deg_to_rad(angle)
            # project a point from agent location outwards
            projection_point = geometry.Point(
                x = self.agent.location.x + math.cos(rad) * self.agent.range_finder_range,
                y = self.agent.location.y + math.sin(rad) * self.agent.range_finder_range
            )
            # rotate the projection point by the agent's heading angle to
            # align it with heading direction
            projection_point.rotate(self.agent.heading, self.agent.location)
            # create the line segment from the agent location to the projected point
            projection_line = geometry.Line(
                a = self.agent.location,
                b = projection_point
            )
            # set range to maximum detection range
            min_range = self.agent.range_finder_range

            # now test against maze walls to see if projection line hits any wall
            # and find the closest hit
            for wall in self.walls:
                found, intersection = wall.intersection(projection_line)
                if found:
                    found_range = intersection.distance(self.agent.location)
                    # we are interested in the closest hit
                    if found_range < min_range:
                        min_range = found_range

            # Update sensor value
            self.agent.range_finders[i] = min_range/self.agent.range_finder_range

    def update_radars(self):
        """
        The function to update the agent radar sensors.
        """
        target = geometry.Point(self.exit_point.x, self.exit_point.y)
        # rotate target with respect to the agent's heading to align it with heading direction
        target.rotate(self.agent.heading, self.agent.location)
        # translate with respect to the agent's location
        target.x -= self.agent.location.x
        target.y -= self.agent.location.y
        # the angle between maze exit point and the agent's heading direction
        angle = target.angle()
        # find the appropriate radar sensor to be fired
        for i, r_angles in enumerate(self.agent.radar_angles):
            self.agent.radar[i] = 0.0 # reset specific radar

            if (angle >= r_angles[0] and angle < r_angles[1]) or (angle + 360 >= r_angles[0] and angle + 360 < r_angles[1]):
                self.agent.radar[i] = 1.0 # fire the radar

    def update(self, control_signals):
        """
        The function to update solver agent position within maze. After agent position
        updated it will be checked to find out if maze exit was reached afetr that.
        Arguments:
            control_signals: The control signals received from the control ANN
        Returns:
            The True if maze exit was found after update or maze exit was already
            found in previous simulation cycles.
        """
        if self.exit_found:
            # Maze exit already found
            return True

        # Apply control signals
        self.apply_control_signals(control_signals)

        # get X and Y velocity components
        vx = math.cos(geometry.deg_to_rad(self.agent.heading)) * self.agent.speed
        vy = math.sin(geometry.deg_to_rad(self.agent.heading)) * self.agent.speed

        # Update current Agent's heading (we consider the simulation time step size equal to 1s
        # and the angular velocity as degrees per second)
        self.agent.heading += self.agent.angular_vel

        # Enforce angular velocity bounds by wrapping
        if self.agent.heading > 360:
            self.agent.heading -= 360
        elif self.agent.heading < 0:
            self.agent.heading += 360

        # find the next location of the agent
        new_loc = geometry.Point(
            x = self.agent.location.x + vx,
            y = self.agent.location.y + vy
        )

        if not self.test_wall_collision(new_loc):
            self.agent.location = new_loc

        # update agent's sensors
        self.update_rangefinder_sensors()
        self.update_radars()

        # check if agent reached exit point
        distance = self.agent_distance_to_exit()
        self.exit_found = (distance < self.exit_range)

        return self.exit_found

    def __str__(self):
        """
        Returns the nicely formatted string representation of this environment.
        """
        str = "MAZE\nAgent at: (%.1f, %.1f)" % (self.agent.location.x, self.agent.location.y)
        str += "\nExit  at: (%.1f, %.1f), exit range: %.1f" % (self.exit_point.x, self.exit_point.y, self.exit_range)
        str += "\nWalls [%d]" % len(self.walls)
        for w in self.walls:
            str += "\n\t%s" % w

        return str

    @staticmethod
    def read_environment(file_path):
        """
        The function to read maze environment configuration from provided
        file.
        Arguments:
            file_path: The path to the file to read maze configuration from.
        Returns:
            The initialized maze environment.
        """
        num_lines, index = -1, 0
        walls = []
        maze_agent, maze_exit = None, None
        with open(file_path, 'r') as file:
            for line in file.readlines():
                line = line.strip()
                if len(line) == 0:
                    # skip empty lines
                    continue

                if index == 0:
                    # read the number of line segments
                    num_lines = int(line)
                elif index == 1:
                    # read the agent's position
                    loc = geometry.read_point(line)
                elif index == 2:
                    # read the agent's initial heading
                    heading = float(line)
                elif index == 3:
                    # read the maze exit location
                    maze_exit = geometry.read_point(line)
                else:
                    # read the walls
                    wall = geometry.read_line(line)
                    walls.append(wall)

                # increment cursor
                index += 1

        assert len(walls) == num_lines

        print("Maze environment configured successfully from the file: %s" % file_path)
        # create and return the maze environment
        return MazeEnvironment(init_location=loc, init_heading=heading, walls=walls, exit_point=maze_exit)

    @staticmethod
    def make_environment(start_point, walls, exit_point, init_heading=0):
        return MazeEnvironment(
            init_location=geometry.read_point(' '.join(list(map(str, start_point)))),
            init_heading=init_heading,
            walls=[geometry.read_line(' '.join(list(map(str,line)))) for line in walls],
            exit_point=geometry.read_point(' '.join(list(map(str, exit_point))))
        )
