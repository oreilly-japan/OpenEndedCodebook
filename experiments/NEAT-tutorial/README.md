# NEET tutorial


## Circuit
### execution
```
$python run_circuit.py
```
#### options:
| option      | abbrev  | default   | detail  |
| :---        | :---:   | :---:     | :---    |
| --name      | -n      | "{task}"  | experiment name |
| --task      | -t      | xor       | circuit name <br> built on "envs/circuit/circuit_files/" |
| --pop-size  | -p      | 150       | population size of NEAT |
| --generation| -g      | 300       | iterations of NEAT |
| --num-cores | -c      | 4         | number of parallel evaluation processes |

### make gif
after run_circuit, make gif file for each of all robots written in reward history file.
output to "./out/circuit_neat/{expt name}/network/"
```
$python make_figures.py {experiment name}
```
#### options:
| option          | abbrev  | default | detail  |
| :---            | :---:   | :---:   | :---    |
|                 |         |         | name of experiment for making figures |
| --specified     | -s      |         | input id, make figure for the only specified circuit |
| --num-cores     | -c      | 1       | number of parallel making processes |
| --not-overwrite |         | *false* | skip process if already gif exists |
| --no-multi      |         | *false* | do without using multiprocessing. if error occur, try this option. |
