import numpy as np
import torch

EnvObservations = {
    'Walker-v0'         : ['robot_velocity', 'robot_relative_position'],
    'BridgeWalker-v0'   : ['robot_velocity', 'robot_orientation', 'robot_relative_position'],
    'CaveCrawler-v0'    : ['robot_velocity', 'robot_relative_position', 'floor', 'ceil'],
    'Jumper-v0'         : ['robot_velocity', 'robot_relative_position', 'floor'],
    'Flipper-v0'        : ['robot_orientation', 'robot_relative_position'],
    'Balancer-v0'       : ['robot_orientation', 'robot_relative_position'],
    'Balancer-v1'       : ['robot_orientation', 'robot_relative_position'],
    'UpStepper-v0'      : ['robot_velocity', 'robot_orientation', 'robot_relative_position', 'floor'],
    'DownStepper-v0'    : ['robot_velocity', 'robot_orientation', 'robot_relative_position', 'floor'],
    'ObstacleTraverser-v0'  : ['robot_velocity', 'robot_orientation', 'robot_relative_position', 'floor'],
    'ObstacleTraverser-v1'  : ['robot_velocity', 'robot_orientation', 'robot_relative_position', 'floor'],
    'Hurdler-v0'        : ['robot_velocity', 'robot_orientation', 'robot_relative_position', 'floor'],
    'GapJumper-v0'      : ['robot_velocity', 'robot_orientation', 'robot_relative_position', 'floor'],
    'PlatformJumper-v0' : ['robot_velocity', 'robot_orientation', 'robot_relative_position', 'floor'],
    'Traverser-v0'      : ['robot_velocity', 'robot_orientation', 'robot_relative_position', 'floor'],
    'Lifter-v0'         : ['robot_velocity', 'object_distance', 'object_velocity', 'object_orientation', 'robot_relative_position'],
    'Carrier-v0'        : ['robot_velocity', 'object_distance', 'object_velocity', 'robot_relative_position'],
    'Carrier-v1'        : ['robot_velocity', 'object_distance', 'object_velocity', 'robot_relative_position'],
    'Pusher-v0'         : ['robot_velocity', 'object_distance', 'object_velocity', 'robot_relative_position'],
    'Pusher-v1'         : ['robot_velocity', 'object_distance', 'object_velocity', 'robot_relative_position'],
    'BeamToppler-v0'    : ['object_distance', 'robot_velocity', 'object_velocity', 'object_orientation', 'robot_relative_position'],
    'BeamSlider-v0'     : ['object_distance', 'robot_velocity', 'object_velocity', 'object_orientation', 'robot_relative_position'],
    'Thrower-v0'        : ['robot_velocity', 'object_distance', 'object_velocity', 'robot_relative_position'],
    'Catcher-v0'        : ['object_distance', 'robot_velocity', 'object_velocity', 'object_orientation', 'robot_relative_position'],
    'AreaMaximizer-v0'  : ['robot_relative_position'],
    'AreaMinimizer-v0'  : ['robot_relative_position'],
    'WingspanMazimizer-v0'  : ['robot_relative_position'],
    'HeightMaximizer-v0'    : ['robot_relative_position'],
    'Climber-v0'        : ['robot_velocity', 'robot_relative_position'],
    'Climber-v1'        : ['robot_velocity', 'robot_relative_position'],
    'Climber-v2'        : ['robot_velocity', 'robot_orientation', 'robot_relative_position', 'ceil'],
    'BidirectionalWalker-v0': ['robot_velocity', 'robot_relative_position', 'goal_num', 'goal_position_x', 'goal_distance_x'],
}

EnvSightDepths = {
    'CaveCrawler-v0'    : 5,
    'Jumper-v0'         : 2,
    'UpStepper-v0'      : 5,
    'DownStepper-v0'    : 5,
    'ObstacleTraverser-v0'  : 5,
    'ObstacleTraverser-v1'  : 5,
    'Hurdler-v0'         : 5,
    'GapJumper-v0'      : 5,
    'PlatformJumper-v0' : 5,
    'Traverser-v0'      : 5,
    'Climber-v2'        : 3,
}

ObservationDimensions = {
    'robot_velocity'            : ['robot', 'velocity', 'x', 'y'],
    'robot_orientation'         : ['robot', 'orientation'],
    'robot_relative_position'   : ['robot', 'relative', 'x', 'y', 'pos_x', 'pos_y', 'ul', 'ur', 'll', 'lr'],
    'floor'                     : ['vertical', 'y', 'pos_x'],
    'ceil'                      : ['vertical', 'y', 'pos_x'],
    'object_distance'           : ['object', 'relative', 'x', 'y'],
    'object_velocity'           : ['object', 'velocity', 'x', 'y'],
    'object_orientation'        : ['object', 'orientation'],
    'goal_num'                  : ['goal', 'num'],
    'goal_position_x'           : ['goal', 'x'],
    'goal_distance_x'           : ['goal', 'relative', 'x'],
}

class Substrate:
    def __init__(self, env_id, robot):
        self.env_id = env_id
        self.robot = robot[::-1].T
        self.size = robot.shape

        self.observations = EnvObservations[env_id]

        self.nodes = None

        vertices = []
        actuators = []
        robot_pad = np.pad(self.robot, 1).astype(int)
        for y in range(self.size[0]-1,-1,-1):
            for x in range(self.size[1]):
                if self.robot[x,y]==0:
                    continue

                if self.robot[x,y]==3:
                    actuators.append((x,y,1,0))
                elif self.robot[x,y]==4:
                    actuators.append((x,y,0,1))

                around = np.where(robot_pad[x:x+3,y:y+3]>0, 1, 0)
                if around[1,2]==0 and around[0,1]==0:
                    around[0,2] = 0
                if around[1,2]==0 and around[2,1]==0:
                    around[2,2] = 0
                if around[0,1]==0 and around[1,0]==0:
                    around[0,0] = 0
                if around[2,1]==0 and around[1,0]==0:
                    around[2,0] = 0

                ul = (x,y+1) + tuple(list(around[0:2,1:3].flatten()))
                ur = (x+1,y+1) + tuple(list(around[1:3,1:3].flatten()))
                bl = (x,y) + tuple(list(around[0:2,0:2].flatten()))
                br = (x+1,y) + tuple(list(around[1:3,0:2].flatten()))
                if ul not in vertices:
                    vertices.append(ul)
                if ur not in vertices:
                    vertices.append(ur)
                if bl not in vertices:
                    vertices.append(bl)
                if br not in vertices:
                    vertices.append(br)

        self.vertices = vertices
        self.actuators = actuators

        self.sight_depth = EnvSightDepths.get(env_id, None)

        self.nodes = None
        self.dims = None
        self.cppn_dims = None

    def make_substrate(self):
        self.nodes = {}

        input_nodes = []
        for obs in self.observations:

            if obs=='robot_velocity':
                input_nodes.append(
                    {
                        'name': 'robot_velocity_x',
                        'dims': {'robot': 1, 'velocity': 1, 'x': 1},
                        'vector': None
                    })
                input_nodes.append(
                    {
                        'name': 'robot_velocity_y',
                        'dims': {'robot': 1, 'velocity': 1, 'y': 1},
                        'vector': None
                    })

            elif obs=='robot_orientation':
                input_nodes.append(
                    {
                        'name': 'robot_orientation',
                        'dims': {'robot': 1, 'orientation': 1},
                        'vector': None
                    })

            elif obs=='robot_relative_position':
                for i,vertice in enumerate(self.vertices):
                    input_nodes.append(
                        {
                            'name': f'robot_position_vertice{i+1}_x',
                            'dims': {
                                'robot': 1, 'relative': 1, 'x': 1, 'pos_x': vertice[0], 'pos_y': vertice[1],
                                'ul': vertice[2], 'ur': vertice[3], 'll': vertice[4], 'lr': vertice[5]},
                            'vector': None
                        })
                    input_nodes.append(
                        {
                            'name': f'robot_position_vertice{i+1}_y',
                            'dims': {
                                'robot': 1, 'relative': 1, 'y': 1, 'pos_x': vertice[0], 'pos_y': vertice[1],
                                'ul': vertice[2], 'ur': vertice[3], 'll': vertice[4], 'lr': vertice[5]},
                            'vector': None
                        })

            elif obs=='floor':
                for x in range(-self.sight_depth, self.sight_depth+1):
                    input_nodes.append(
                        {
                            'name': f'floor_{x: =+}',
                            'dims': {'sight': 1, 'y': 1, 'pos_x': x, 'pos_y': -1},
                            'vector': None
                        })

            elif obs=='ceil':
                for x in range(-self.sight_depth, self.sight_depth+1):
                    input_nodes.append(
                        {
                            'name': f'ceil_{x: =+}',
                            'dims': {'sight': 1, 'y': 1, 'pos_x': x, 'pos_y': 1},
                            'vector': None
                        })

            elif obs=='object_distance':
                input_nodes.append(
                    {
                        'name': 'obejct_distance',
                        'dims': {'object': 1, 'relative': 1, 'x': 1},
                        'vector': None
                    })
                input_nodes.append(
                    {
                        'name': 'obejct_distance',
                        'dims': {'object': 1, 'relative': 1, 'y': 1},
                        'vector': None
                    })

            elif obs=='object_velocity':
                input_nodes.append(
                    {
                        'name': 'obejct_velocity',
                        'dims': {'object': 1, 'velocity': 1, 'x': 1},
                        'vector': None
                    })
                input_nodes.append(
                    {
                        'name': 'obejct_velocity',
                        'dims': {'object': 1, 'velocity': 1, 'y': 1},
                        'vector': None
                    })

            elif obs=='object_orientation':
                input_nodes.append(
                    {
                        'name': 'object_orientation',
                        'dims': {'object': 1, 'orientation': 1},
                        'vector': None
                    })

            elif obs=='goal_num':
                input_nodes.append(
                    {
                        'name': 'goal_num',
                        'dims': {'goal': 1, 'num': 1},
                        'vector': None
                    })

            elif obs=='goal_position_x':
                input_nodes.append(
                    {
                        'name': 'goal_position_x',
                        'dims': {'goal': 1, 'x': 1},
                        'vector': None
                    })

            elif obs=='goal_distance_x':
                input_nodes.append(
                    {
                        'name': 'goal_distance_x',
                        'dims': {'goal': 1, 'relative': 1, 'x': 1},
                        'vector': None
                    })
        self.nodes['input'] = input_nodes

        output_nodes = []
        for i,actuator in enumerate(self.actuators):
            output_nodes.append(
                {
                    'name': f'actuator{i+1}',
                    'dims': {'robot': 1, 'pos_x': actuator[0]+0.5, 'pos_y': actuator[1]+0.5, 'horizontal': actuator[2], 'vertical': actuator[3]},
                    'vector': None
                })
        self.nodes['output'] = output_nodes

        self.dims = list(set().union(*(
            sum([[set(node['dims'].keys()) for node in nodes] for nodes in self.nodes.values()],[])
        )))
        self.dims = sorted(self.dims)
        self.cppn_dims = list(map(lambda z: z+'1', self.dims)) + list(map(lambda z: z+'2', self.dims))


    def add_hidden(self, name, hidden_num):
        hidden_nodes = []
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                hidden_nodes.append(
                    {
                        'name': f'{name}{hidden_num}_{x}_{y}',
                        'dims': {'pos_x': x+0.5, 'pos_y': y+0.5, 'hidden': hidden_num},
                        'vector': None
                    })
        self.nodes[name] = hidden_nodes

        self.dims = sorted(list(set(self.dims+['hidden'])))
        self.cppn_dims = list(map(lambda z: z+'1', self.dims)) + list(map(lambda z: z+'2', self.dims))

    def make_vectors(self):
        for layer in self.nodes.keys():
            for node in self.nodes[layer]:
                node['vector'] = np.array([node['dims'].get(dim, 0) for dim in self.dims])

    def get_connection_inputs(self, layer_pairs):
        connections = {}
        for layer_in, layer_out in layer_pairs:
            for node_in in self.nodes[layer_in]:
                for node_out in self.nodes[layer_out]:
                    connections[(node_in['name'], node_out['name'])] = np.hstack((node_in['vector'], node_out['vector']))

        edge_labels= list(connections.keys())
        cppn_inputs = torch.from_numpy(np.vstack(list(connections.values())))
        cppn_inputs = {dim: cppn_inputs[:,i] for i,dim in enumerate(self.cppn_dims)}
        return edge_labels, cppn_inputs

    def get_node_inputs(self, layers):
        nodes = {}
        blank = np.zeros(len(self.dims))
        for layer in layers:
            for node in self.nodes[layer]:
                nodes[node['name']] = np.hstack((node['vector'], blank))

        node_labels = list(nodes.keys())
        cppn_inputs = torch.from_numpy(np.vstack(list(nodes.values())))
        cppn_inputs = {dim: cppn_inputs[:,i] for i,dim in enumerate(self.cppn_dims)}
        return node_labels, cppn_inputs

    def get_nodes(self, layer):
        return [node['name'] for node in self.nodes[layer]]

    def get_dim_size(self):
        return len(self.cppn_dims)
