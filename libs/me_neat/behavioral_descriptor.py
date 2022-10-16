import numpy as np

class LinerBehavioralDescriptor:
    def __init__(self, name, value_range, resolution):
        self.name = name
        self.value_range = value_range
        self.resolution = resolution
        self.bin_width = (value_range[1]-value_range[0])/resolution
        self.bins = [value_range[0]+i*self.bin_width for i in range(resolution+1)]

    def get_index(self, bd):
        index = int((bd-self.value_range[0])/self.bin_width)
        index = max(0,min(index,self.resolution))
        return index

    def evaluate(self, *args):
        pass
