
from evogym import is_connected, has_actuator, hashable

class EvogymStructureConstraint:
    def __init__(self, decode_function):
        self.decode_function = decode_function
        self.hashes = {}

    def eval_constraint(self, genome, config, generation):
        robot = self.decode_function(genome, config)
        body = robot['body']
        validity = is_connected(body) and has_actuator(body)
        if validity:
            robot_hash = hashable(body)
            if robot_hash in self.hashes:
                validity = False
            else:
                self.hashes[robot_hash] = True

        return validity
