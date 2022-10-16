import numpy as np

from me_neat import LinerBehavioralDescriptor

class BlockDensity(LinerBehavioralDescriptor):
    def evaluate(self, robot):
        x = np.mean(robot['body']>0)
        index = self.get_index(x)
        return index

class RigidDensity(LinerBehavioralDescriptor):
    def evaluate(self, robot):
        x = np.mean(robot['body']==1)
        index = self.get_index(x)
        return index

class SoftDensity(LinerBehavioralDescriptor):
    def evaluate(self, robot):
        x = np.mean(robot['body']==2)
        index = self.get_index(x)
        return index

class ActuatorDensity(LinerBehavioralDescriptor):
    def evaluate(self, robot):
        x = np.mean(np.logical_or(robot['body']==2, robot['body']==3))
        index = self.get_index(x)
        return index
