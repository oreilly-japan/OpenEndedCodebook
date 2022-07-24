# Novelty Search


## Maze
### execution
```
$python run_maze.py
```
#### options:
| option        | abbrev  | default   | detail  |
| :---          | :---:   | :---:     | :---    |
| --name        | -n      | "{task}"  | experiment name |
| --task        | -t      | medium    | maze name <br> built on "envs/maze/maze_files/" |
| --pop-size    | -p      | 500       | population size of NEAT |
| --generation  | -g      | 500       | iterations of NEAT |
| --ns-threshold|         | 6.0       | initial threshold to add to novelty archive |
| --num-knn     |         | 15        | number of nearest neighbors to calculate novelty |
| --mcns        |         | 0.01      | minimal reward criterion. if not satisfy, die. |
| --timestep    |         | 400       | limit of timestep for solving maze |
| --num-cores   | -c      | 4         | number of parallel evaluation processes |
| --no-plot     |         | *false*   | not open window of progress figure |


## Maze Hyper-NEAT
### execution
```
$python run_maze_hyper.py
```
#### options:
| option        | abbrev  | default   | detail  |
| :---          | :---:   | :---:     | :---    |
| --name        | -n      | "{task}"  | experiment name |
| --task        | -t      | medium    | maze name <br> built on "envs/maze/maze_files/" |
| --pop-size    | -p      | 500       | population size of NEAT |
| --generation  | -g      | 500       | iterations of NEAT |
| --ns-threshold|         | 6.0       | initial threshold to add to novelty archive |
| --num-knn     |         | 15        | number of nearest neighbors to calculate novelty |
| --mcns        |         | 0.01      | minimal reward criterion. if not satisfy, die. |
| --use-hideen  |         | *false*   | make hidden nodes on NN substrate |
| --timestep    |         | 400       | limit of timestep for solving maze |
| --num-cores   | -c      | 4         | number of parallel evaluation processes |
| --no-plot     |         | *false*   | not open window of progress figure |


## Evogym
### execution
```
$python run_evogym.py
```
#### options:
| option        | abbrev  | default         | detail  |
| :---          | :---:   | :---:           | :---    |
| --name        | -n      | "{task}_{robot}"| experiment name |
| --task        | -t      | Walker-v0       | evogym environment id |
| --robot       | -r      | cat             | robot structure name <br> built on "envs/evogym/robot_files/" <br> if "default", load default robot for the task |
| --pop-size    | -p      | 200             | population size of NEAT |
| --generation  | -g      | 500             | iterations of NEAT |
| --ns-threshold|         | 0.1             | initial threshold to add to novelty archive |
| --num-knn     |         | 5               | number of nearest neighbors to calculate novelty |
| --mcns        |         | 0.0             | minimal reward criterion. if not satisfy, die. |
| --eval-num    |         | 1               | evaluation times. if probabilistic task, need more. |
| --num-cores   | -c      | 4               | number of parallel evaluation processes |
| --no-view     |         | *false*         | not open simulation window of best robot |

### make figure
after run_evogym, make {gif, jpg} file for each of all genomes written in history files.
output to "./out/evogym_ns_neat/{expt name}/figure/{gif, jpg}/"
```
$python make_figures.py {experiment name}
```
#### options:
| option              | abbrev  | default | detail  |
| :---                | :---:   | :---:   | :---    |
|                     |         |         | name of experiment for making figures |
| --specified         | -s      |         | input id, make figure for the only specified genome |
| --save-type         | -st     | gif     | file type (choose from [gif, jpg])
| --resolution-ratio  | -r      | 0.2     | gif resolution ratio (0.2 -> (256,144)) |
| --interval          | -i      | timestep| in case of save type is jpg, type of interval for robot drawing <br>(choose from [timestep, distance, hybrid]) |
| --resolution-scale  | -rs     | 32.0    | jpg resolution scale <br> when output monochrome image, try this argument change. |
| --timestep-interval | -ti     | 80      | timestep interval for robot drawing <br>(if interval is hybrid, it should be about 40) |
| --distance-interval | -di     | 0.8     | distance interval for robot drawing |
| --display-timestep  |         | *false* | display timestep above robot |
| --num-cores         | -c      | 1       | number of parallel making processes |
| --not-overwrite     |         | *false* | skip process if already figure exists |
| --no-multi          |         | *false* | do without using multiprocessing. if error occur, try this option. |


## Evogym Hyper-NEAT
### execution
```
$python run_evogym_hyper.py
```
#### options:
| option        | abbrev  | default         | detail  |
| :---          | :---:   | :---:           | :---    |
| --name        | -n      | "{task}_{robot}"| experiment name |
| --task        | -t      | Walker-v0       | evogym environment id |
| --robot       | -r      | cat             | robot structure name <br> built on "envs/evogym/robot_files/" <br> if "default", load default robot for the task |
| --pop-size    | -p      | 200             | population size of NEAT |
| --generation  | -g      | 500             | iterations of NEAT |
| --ns-threshold|         | 0.1             | initial threshold to add to novelty archive |
| --num-knn     |         | 5               | number of nearest neighbors to calculate novelty |
| --mcns        |         | 0.0             | minimal reward criterion. if not satisfy, die. |
| --use-hideen  |         | *false*         | make hidden nodes on NN substrate |
| --eval-num    |         | 1               | evaluation times. if probabilistic task, need more. |
| --num-cores   | -c      | 4               | number of parallel evaluation processes |
| --no-view     |         | *false*         | not open simulation window of best robot |

### make figure
after run_evogym_hyper, make {gif, jpg} file for each of all genomes written in history files.
output to "./out/evogym_ns_hyper/{expt name}/figure/{gif, jpg}/"
```
$python make_figures_hyper.py {experiment name}
```
#### options:
| option              | abbrev  | default | detail  |
| :---                | :---:   | :---:   | :---    |
|                     |         |         | name of experiment for making figures |
| --specified         | -s      |         | input id, make figure for the only specified genome |
| --save-type         | -st     | gif     | file type (choose from [gif, jpg])
| --resolution-ratio  | -r      | 0.2     | gif resolution ratio (0.2 -> (256,144)) |
| --interval          | -i      | timestep| in case of save type is jpg, type of interval for robot drawing <br>(choose from [timestep, distance, hybrid]) |
| --resolution-scale  | -rs     | 32.0    | jpg resolution scale <br> when output monochrome image, try this argument change. |
| --timestep-interval | -ti     | 80      | timestep interval for robot drawing <br>(if interval is hybrid, it should be about 40) |
| --distance-interval | -di     | 0.8     | distance interval for robot drawing |
| --display-timestep  |         | *false* | display timestep above robot |
| --num-cores         | -c      | 1       | number of parallel making processes |
| --not-overwrite     |         | *false* | skip process if already figure exists |
| --no-multi          |         | *false* | do without using multiprocessing. if error occur, try this option. |
