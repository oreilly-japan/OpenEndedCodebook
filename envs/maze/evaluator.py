

class MazeControllerEvaluator():
    def __init__(self, maze, timesteps):
        self.maze = maze
        self.timesteps = timesteps

    def evaluate_agent(self, key, controller, generation):
        self.maze.reset()

        done = False
        for i in range(self.timesteps):
            obs = self.maze.get_observation()
            action = controller.activate(obs)
            done = self.maze.update(action)
            if done:
                break

        if done:
            reward = 1.0
        else:
            distance = self.maze.get_distance_to_exit()
            reward = (self.maze.initial_distance - distance) / self.maze.initial_distance

        last_loc = self.maze.get_agent_location()
        results = {
            'fitness': reward,
            'data': last_loc
        }
        return results


class MazeControllerEvaluatorNS():
    def __init__(self, maze, timesteps):
        self.maze = maze
        self.timesteps = timesteps

    def evaluate_agent(self, key, controller, generation):
        self.maze.reset()

        done = False
        for i in range(self.timesteps):
            obs = self.maze.get_observation()
            action = controller.activate(obs)
            done = self.maze.update(action)
            if done:
                break

        if done:
            reward = 1.0
        else:
            distance = self.maze.get_distance_to_exit()
            reward = (self.maze.initial_distance - distance) / self.maze.initial_distance

        last_loc = self.maze.get_agent_location()
        results = {
            'reward': reward,
            'data': last_loc
        }
        return results
