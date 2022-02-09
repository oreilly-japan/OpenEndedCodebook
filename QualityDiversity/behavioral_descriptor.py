class BehavioralDescriotir:
    def __init__(self, name, value_range, divide_num):
        self.name = name
        self.value_range = value_range
        self.divide_num = divide_num
        self.bin_width = (value_range[1]-value_range[0])/divide_num
        self.bins = [value_range[0]+i*self.bin_width for i in range(divide_num+1)]

    def get_index(self, bd):
        index = int((bd-self.value_range[0])/self.bin_width)
        index = max(0,min(index,self.divide_num-1))
        return index

    def evaluate(self, data):
        pass

class PositionX(BehavioralDescriotir):
    def evaluate(self, points, **args):
        x = points[-1].x
        index = self.get_index(x)
        return index

class PositionY(BehavioralDescriotir):
    def evaluate(self, points, **args):
        y = points[-1].y
        index = self.get_index(y)
        return index

class Velocity(BehavioralDescriotir):
    def __init__(self, time_steps, sample_rate, **args):
        self.sample_rate = sample_rate
        self.time = int(time_steps/sample_rate)
        super().__init__(**args)

    def evaluate(self, points, **args):
        points_sampled = points[::self.sample_rate]
        distance = 0
        for i in range(len(points_sampled)-1):
            point = points_sampled[i]
            next_point = points_sampled[i+1]
            distance += point.distance(next_point)
        velocity = distance/((len(points_sampled)-1)*self.time)
        index = self.get_index(velocity)
        return index

class Rotation(BehavioralDescriotir):
    def __init__(self, time_steps, sample_rate, **args):
        self.sample_rate = sample_rate
        self.time = int(time_steps/sample_rate)
        super().__init__(**args)

    def evaluate(self, headings, **args):
        headings_sampled = headings[::self.sample_rate]
        rotation = 0
        for i in range(len(headings_sampled)-1):
            heading = headings_sampled[i]
            next_heading = headings_sampled[i+1]
            diff = abs(next_heading-heading)
            rotation += min(diff,360-diff)
        rotation = rotation/((len(headings_sampled)-1)*self.time)
        index = self.get_index(rotation)
        return index
