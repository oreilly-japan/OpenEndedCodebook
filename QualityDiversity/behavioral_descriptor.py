import numpy as np

class BehavioralDescriotir:
    def __init__(self, name, value_range, resolution):
        self.name = name
        self.value_range = value_range
        self.resolution = resolution
        self.bin_width = (value_range[1]-value_range[0])/resolution
        self.bins = [value_range[0]+i*self.bin_width for i in range(resolution+1)]

    def get_index(self, bd):
        index = int((bd-self.value_range[0])/self.bin_width)
        index = max(0,min(index,self.resolution-1))
        return index

    def evaluate(self, data):
        pass

class BlockDensity(BehavioralDescriotir):
    def evaluate(self, robot, connections):
        x = 1-np.mean(robot==0)
        index = self.get_index(x)
        return index

class RigidDensity(BehavioralDescriotir):
    def evaluate(self, robot, connections):
        x = np.mean(robot==1)
        index = self.get_index(x)
        return index

class SoftDensity(BehavioralDescriotir):
    def evaluate(self, robot, connections):
        x = np.mean(robot==2)
        index = self.get_index(x)
        return index

class ActuatorDensity(BehavioralDescriotir):
    def evaluate(self, robot, connections):
        x = np.mean(np.logical_or(robot==2, robot==3))
        index = self.get_index(x)
        return index
