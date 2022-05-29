# NEET


## Maze
### execution
```
$python run_maze.py
```
#### options:
| option      | abbrev  | default   | detail  |
| :---        | :---:   | :---:     | :---    |
| --name      | -n      | "{task}"  | experiment name |
| --task      | -t      | medium    | maze name <br> built on "envs/maze/maze_files/" |
| --pop-size  | -p      | 500       | population size of NEAT |
| --generation| -g      | 500       | iterations of NEAT |
| --timestep  |         | 400       | limit of timestep for solving maze |
| --num-cores | -c      | 4         | number of parallel evaluation processes |
| --no-plot   |         | *false*   | not open window of progress figure |


## Maze Hyper-NEAT
### execution
```
$python run_maze_hyper.py
```
#### options:
| option      | abbrev  | default   | detail  |
| :---        | :---:   | :---:     | :---    |
| --name      | -n      | "{task}"  | experiment name |
| --task      | -t      | medium    | maze name <br> built on "envs/maze/maze_files/" |
| --pop-size  | -p      | 500       | population size of NEAT |
| --generation| -g      | 500       | iterations of NEAT |
| --use-hideen|         | *false*   | make hidden nodes on NN substrate |
| --timestep  |         | 400       | limit of timestep for solving maze |
| --num-cores | -c      | 4         | number of parallel evaluation processes |
| --no-plot   |         | *false*   | not open window of progress figure |



## Evogym
### execution
```
$python run_evogym.py
```
#### options:
| option      | abbrev  | default         | detail  |
| :---        | :---:   | :---:           | :---    |
| --name      | -n      | "{task}_{robot}"| experiment name |
| --task      | -t      | Walker-v0       | evogym environment id |
| --robot     | -r      | cat             | robot structure name <br> built on "envs/evogym/robot_files/" |
| --pop-size  | -p      | 200             | population size of NEAT |
| --generation| -g      | 500             | iterations of NEAT |
| --eval-num  |         | 1               | evaluation times. if probabilistic task, need more. |
| --num-cores | -c      | 4               | number of parallel evaluation processes |
| --no-view   |         | *false*         | not open simulation window of best robot |


### make gif
after run_evogym, make gif file for each of all robots written in reward history file.
output to "./out/evogym_neat/{expt name}/gif/"
```
$python make_gifs.py {experiment name}
```
#### options:
| option          | abbrev  | default | detail  |
| :---            | :---:   | :---:   | :---    |
|                 |         |         | name of experiment for making gifs |
| --resolution    | -r      | 0.2     | image resolution ratio (0.2 -> (256,144)) |
| --specified     | -s      |         | input id, make gif for the only specified robot |
| --num-cores     | -c      | 1       | number of parallel making processes |
| --not-overwrite |         | *false* | skip process if already gif exists |
| --no-multi      |         | *false* | do without using multiprocessing. if error occur, try this option. |


## Evogym Hyper-NEAT
### execution
```
$python run_evogym_hyper.py
```
#### options:
| option      | abbrev  | default         | detail  |
| :---        | :---:   | :---:           | :---    |
| --name      | -n      | "{task}_{robot}"| experiment name |
| --task      | -t      | Walker-v0       | evogym environment id |
| --robot     | -r      | cat             | robot structure name <br> built on "envs/evogym/robot_files/" |
| --pop-size  | -p      | 200             | population size of NEAT |
| --generation| -g      | 500             | iterations of NEAT |
| --use-hideen|         | *false*         | make hidden nodes on NN substrate |
| --eval-num  |         | 1               | evaluation times. if probabilistic task, need more. |
| --num-cores | -c      | 4               | number of parallel evaluation processes |
| --no-view   |         | *false*         | not open simulation window of best robot |


### make gif
after run_evogym_hyper, make gif file for each of all robots written in reward history file.
output to "./out/evogym_hyper/{expt name}/gif/"
```
$python make_gifs_hyper.py {experiment name}
```
#### options:
| option          | abbrev  | default | detail  |
| :---            | :---:   | :---:   | :---    |
|                 |         |         | name of experiment for making gifs |
| --resolution    | -r      | 0.2     | image resolution ratio (0.2 -> (256,144)) |
| --specified     | -s      |         | input id, make gif for the only specified robot |
| --num-cores     | -c      | 1       | number of parallel making processes |
| --not-overwrite |         | *false* | skip process if already gif exists |
| --no-multi      |         | *false* | do without using multiprocessing. if error occur, try this option. |


## Evogym Structure Evolution
### execution
```
$python run_evogym_cppn.py
```
#### options:
| option          | abbrev  | default         | detail  |
| :---            | :---:   | :---:           | :---    |
| --name          | -n      | "{task}_{robot}"| experiment name |
| --task          | -t      | Walker-v0       | evogym environment id |
| --shape         | -s      | (5,5)           | robot shape <br> usage: "-s {height} {width}" |
| --pop-size      | -p      | 4               | population size of NEAT |
| --generation    | -g      | 500             | iterations of NEAT |
| --ppo-iters     | -l      | 5               | learning iterations of PPO algo <br> on the more complex task, need more. |
| --deterministic |         | *false*         | evaluate robot on deterministic action |
| --num-cores     | -c      | 1               | number of parallel evaluation processes |
| --no-view       |         | *false*         | not open simulation window of best robot |

### make gif
after run_evogym_cppn, make gif file for each of all robots written in reward history file.
output to "./out/evogym_cppn/{expt name}/gif/"
```
$python make_gifs_cppn.py {experiment name}
```
#### options:
| option          | abbrev  | default | detail  |
| :---            | :---:   | :---:   | :---    |
|                 |         |         | name of experiment for making gifs |
| --resolution    | -r      | 0.2     | image resolution ratio (0.2 -> (256,144)) |
| --specified     | -s      |         | input id, make gif for the only specified robot |
| --deterministic |         | *false* | robot act deterministically |
| --num-cores     | -c      | 1       | number of parallel making processes |
| --not-overwrite |         | *false* | skip process if already gif exists |
| --no-multi      |         | *false* | do without using multiprocessing. if error occur, try this option. |
