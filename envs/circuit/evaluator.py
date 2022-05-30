import numpy as np


def load_circuit(data_file):
    index = 0
    input_size = None
    output_size = None
    input_data = []
    output_data = []

    with open(data_file, 'r') as file:
        for line in file.readlines():
            line = line.strip()
            if len(line) == 0:
                continue

            elif index == 0:
                input_size = int(line)
            elif index == 1:
                output_size = int(line)
            else:
                data = list(map(float, line.split(' ')))
                assert len(data)==input_size+output_size

                input_data.append(data[:input_size])
                output_data.append(data[input_size:])

            index += 1

    input_data = np.vstack(input_data)
    output_data = np.vstack(output_data)

    return input_data, output_data


class CircuitEvaluator():
    def __init__(self, input_data, output_data):

        self.input_data = input_data
        self.output_data = output_data

    def evaluate_circuit(self, key, circuit, generation):

        output_pred = []
        for inp in self.input_data:
            pred = circuit.activate(inp)
            output_pred.append(pred)

        output_pred = np.vstack(output_pred)
        error = np.mean(np.square(self.output_data - output_pred))

        results = {
            'fitness': 1.0 - error
        }
        return results
