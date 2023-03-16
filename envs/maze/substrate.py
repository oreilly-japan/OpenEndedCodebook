import numpy as np

class Substrate:
    def __init__(self):
        self.nodes = None
        self.dims = None
        self.cppn_dims = None

    def make_substrate(self):
        self.nodes = {}

        input_nodes = [
            {
                'name': 'sensor270',
                'dims': {'x': np.cos(270/180*np.pi), 'y': np.sin(270/180*np.pi), 'd': 1, 'sensor': 1},
                'vector': None
            }, {
                'name': 'sensor315',
                'dims': {'x': np.cos(315/180*np.pi), 'y': np.sin(315/180*np.pi), 'd': 1, 'sensor': 1},
                'vector': None
            }, {
                'name': 'sensor0',
                'dims': {'x': np.cos(  0/180*np.pi), 'y': np.sin(  0/180*np.pi), 'd': 1, 'sensor': 1},
                'vector': None
            }, {
                'name': 'sensor45',
                'dims': {'x': np.cos( 45/180*np.pi), 'y': np.sin( 45/180*np.pi), 'd': 1, 'sensor': 1},
                'vector': None
            }, {
                'name': 'sensor90',
                'dims': {'x': np.cos( 90/180*np.pi), 'y': np.sin( 90/180*np.pi), 'd': 1, 'sensor': 1},
                'vector': None
            }, {
                'name': 'sensor180',
                'dims': {'x': np.cos(180/180*np.pi), 'y': np.sin(180/180*np.pi), 'd': 1, 'sensor': 1},
                'vector': None
            }, {
                'name': 'rader0',
                'dims': {'x': np.cos(  0/180*np.pi), 'y': np.sin(  0/180*np.pi), 'd': 2, 'rader': 1},
                'vector': None
            }, {
                'name': 'rader90',
                'dims': {'x': np.cos( 90/180*np.pi), 'y': np.sin( 90/180*np.pi), 'd': 2, 'rader': 1},
                'vector': None
            }, {
                'name': 'rader180',
                'dims': {'x': np.cos(180/180*np.pi), 'y': np.sin(180/180*np.pi), 'd': 2, 'rader': 1},
                'vector': None
            }, {
                'name': 'rader270',
                'dims': {'x': np.cos(270/180*np.pi), 'y': np.sin(270/180*np.pi), 'd': 2, 'rader': 1},
            }
        ]
        self.nodes['input'] = input_nodes

        output_nodes = [
            {
                'name': 'actuator_rotation',
                'dims': {'rotate': 1},
                'vector': None
            }, {
                'name': 'actuator_speed',
                'dims': {'spped': 1},
                'vector': None
            }
        ]
        self.nodes['output'] = output_nodes

        self.dims = list(set().union(*(
            sum([[set(node['dims'].keys()) for node in nodes] for nodes in self.nodes.values()],[])
        )))
        self.dims = sorted(self.dims)
        self.cppn_dims = list(map(lambda z: z+'1', self.dims)) + list(map(lambda z: z+'2', self.dims))

    def add_hidden(self, name):
        hidden_nodes = [
            {
                'name': f'{name}60',
                'dims': {'x': np.cos( 60/180*np.pi)/2, 'y': np.sin( 60/180*np.pi)/2, 'd': 0.5},
                'vector': None
            }, {
                'name': f'{name}180',
                'dims': {'x': np.cos(180/180*np.pi)/2, 'y': np.sin(180/180*np.pi)/2, 'd': 0.5},
                'vector': None
            }, {
                'name': f'{name}300',
                'dims': {'x': np.cos(300/180*np.pi)/2, 'y': np.sin(300/180*np.pi)/2, 'd': 0.5},
                'vector': None
            }
        ]
        self.nodes[name] = hidden_nodes

        # self.dims = sorted(list(set(self.dims+['hidden'])))
        # self.cppn_dims = list(map(lambda z: z+'1', self.dims)) + list(map(lambda z: z+'2', self.dims))

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

        return connections

    def get_node_inputs(self, layers):
        nodes = {}
        blank = np.zeros(len(self.dims))
        for layer in layers:
            for node in self.nodes[layer]:
                nodes[node['name']] = np.hstack((node['vector'], blank))

        return nodes

    def get_nodes(self, layer):
        return [node['name'] for node in self.nodes[layer]]

    def get_dim_size(self):
        return len(self.cppn_dims)
