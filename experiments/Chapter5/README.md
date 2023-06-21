# Minimal Criterion Coevolution


## Maze
### bootstrap
To execute before main mcc process. It prepare initial population.
```
$ python bootstrap_maze_mcc.py
```
#### options:
| option            | abbrev  | default   | detail  |
| :---              | :---:   | :---:     | :---    |
| --name            | -n      | default   | boostrap name |
| --agent-num       |         | 20        | number of agent to prepare |
| --maze-num        |         | 10        | number of maze to prepare |
| --wall-gene-num   |         | 2         | initial number of wall gene |
| --path-gene-num   |         | 2         | initial number of path gene |
| --exit-range      |         | 5.0       | range of judgment that reached the goal |
| --radius          |         | 5.0       | radius of agent |
| --range-finder    |         | 100.0     | range of agent's range finder |
| --max-speed       |         | 5.0       | agent max speed |
| --max-angular-vel |         | 8.0       | agent max angular velocity |
| --speed-scale     |         | 2.0       | nn output scaler for speed |
| --angular-scale   |         | 3.0       | nn output scaler for angular velocity |
| --num-cores       | -c      | 4         | number of parallel evaluation processes |

### mcc
```
$ python run_maze_mcc.py
```
#### options:
| option            | abbrev  | default       | detail  |
| :---              | :---:   | :---:         | :---    |
| --name            | -n      | "{bootstrap}" | experiment name |
| --bootstrap       | -b      | default       | name of bootstrap to use as initial state |
| --generation      | -g      | 1000          | iterations |
| --agent-criterion |         | 1             | minimal number to solve maze for each agent to survive |
| --maze-criterion  |         | 1             | minimal number of agent to solve for each maze to survive |
| --agent-pop       |         | 160           | maximum size of agent population |
| --maze-pop        |         | 40            | maximum size of maze population |
| --agent-limit     |         | 0             | resource limit of agent <br> 0 means no limit |
| --maze-limit      |         | 4             | resource limit of maze |
| --agent-bacth     |         | 40            | agent number to evaluate in one iteration |
| --maze-batch      |         | 10            | maze number to evaluate in one iteration |
| --num-cores       | -c      | 4             | number of parallel evaluation processes |
| --print-maze      |         | *false*       | print detail of survived maze genome every iteration |

### make figure
```
$ python draw_maze_mcc.py {experiment name}
```
#### options:
| option            | abbrev  | default | detail  |
| :---              | :---:   | :---:   | :---    |
|                   |         |         | name of experiment for making figures |
| --start-generation| -sg     | 0       | draw all of mazes produced since this generation |
| --end-generation  | -eg     | 2^16    | draw all of mazes produced up to this generation |
| --colorbar        | -cb     | *false* | plot colorbar of timestep |
| --num-cores       | -c      | 1       | number of parallel making processes |
| --not-overwrite   |         | *false* | skip process if already gif exists |
| --no-multi        |         | *false* | do without using multiprocessing. if error occur, try this option. |
