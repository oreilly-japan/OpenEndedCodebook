
from neat_cppn import BaseHyperDecoder

class MazeHyperDecoder(BaseHyperDecoder):
    def __init__(self, substrate, use_hidden=False):

        connections = [('input', 'output')]
        downstream_nodes = ['output']

        substrate.make_substrate()
        if use_hidden:
            substrate.add_hidden('hidden')
            connections.extend([('input', 'hidden'), ('hidden', 'output')])
            downstream_nodes.append('hidden')

        substrate.make_vectors()

        self.set_attr(substrate, connections, downstream_nodes)
