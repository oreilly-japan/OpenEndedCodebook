import numpy as np

from me_neat import LinerBehavioralDescriotir

class BlockDensity(LinerBehavioralDescriotir):
    def evaluate(self, robot, connections):
        x = np.mean(robot>0)
        index = self.get_index(x)
        return index

class RigidDensity(LinerBehavioralDescriotir):
    def evaluate(self, robot, connections):
        x = np.mean(robot==1)
        index = self.get_index(x)
        return index

class SoftDensity(LinerBehavioralDescriotir):
    def evaluate(self, robot, connections):
        x = np.mean(robot==2)
        index = self.get_index(x)
        return index

class ActuatorDensity(LinerBehavioralDescriotir):
    def evaluate(self, robot, connections):
        x = np.mean(np.logical_or(robot==2, robot==3))
        index = self.get_index(x)
        return index
