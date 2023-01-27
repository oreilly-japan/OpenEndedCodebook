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
| --robot     | -r      | cat             | robot structure name <br> built on "envs/evogym/robot_files/" <br> if "default", load default robot for the task |
| --pop-size  | -p      | 200             | population size of NEAT |
| --generation| -g      | 500             | iterations of NEAT |
| --eval-num  |         | 1               | evaluation times. if probabilistic task, need more. |
| --num-cores | -c      | 4               | number of parallel evaluation processes |
| --no-view   |         | *false*         | not open simulation window of best robot |


### make figure
after run_evogym, make {gif, jpg} file for each of all genomes written in reward history file.
output to "./out/evogym_neat/{expt name}/figure/{gif, jpg}/"
```
$python make_figures.py {experiment name}
```
#### options:
| option              | abbrev  | default | detail  |
| :---                | :---:   | :---:   | :---    |
|                     |         |         | name of experiment for making figures |
| --specified         | -s      |         | input id, make figure for the only specified genome |
| --save-type         | -st     | gif     | file type (choose from [gif, jpg])
| --track-robot       | -rt     | *false* | in case of save type is gif, track robot with camera |
| --interval          | -i      | timestep| in case of save type is jpg, type of interval for robot drawing <br>(choose from [timestep, distance]) |
| --resolution-scale  | -rs     | 32.0    | jpg resolution scale <br> when output monochrome image, try this argument change. |
| --start-timestep    |         | 0       | start timestep of render |
| --timestep-interval | -ti     | 80      | timestep interval for robot drawing <br>(if interval is hybrid, it should be about 40) |
| --blur              | -b      | 0       |in case of jpg, timesteps for rendering motion blur, 0 means no blur |
| --blur-temperature  | -bt     | 0.6     | blur temperature, up to 1.0 |
| --distance-interval | -di     | 0.8     | distance interval for robot drawing |
| --display-timestep  |         | *false* | display timestep above robot |
| --draw-trajectory   |         | *false* | draw robot trajectory as line |
| --num-cores         | -c      | 1       | number of parallel making processes |
| --not-overwrite     |         | *false* | skip process if already figure exists |
| --no-multi          |         | *false* | do without using multiprocessing. if error occur, try this option. |


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
| --robot     | -r      | cat             | robot structure name <br> built on "envs/evogym/robot_files/" <br> if "default", load default robot for the task |
| --pop-size  | -p      | 200             | population size of NEAT |
| --generation| -g      | 500             | iterations of NEAT |
| --use-hideen|         | *false*         | make hidden nodes on NN substrate |
| --eval-num  |         | 1               | evaluation times. if probabilistic task, need more. |
| --num-cores | -c      | 4               | number of parallel evaluation processes |
| --no-view   |         | *false*         | not open simulation window of best robot |


### make figure
after run_evogym_hyper, make {gif, jpg} file for each of all genomes written in reward history file.
output to "./out/evogym_hyper/{expt name}/figure/{gif, jpg}/"
```
$python make_figure_hyper.py {experiment name}
```
#### options:
| option              | abbrev  | default | detail  |
| :---                | :---:   | :---:   | :---    |
|                     |         |         | name of experiment for making figures |
| --specified         | -s      |         | input id, make figure for the only specified genome |
| --save-type         | -st     | gif     | file type (choose from [gif, jpg])
| --track-robot       | -rt     | *false* | in case of save type is gif, track robot with camera |
| --interval          | -i      | timestep| in case of save type is jpg, type of interval for robot drawing <br>(choose from [timestep, distance]) |
| --resolution-scale  | -rs     | 32.0    | jpg resolution scale <br> when output monochrome image, try this argument change. |
| --start-timestep    |         | 0       | start timestep of render |
| --timestep-interval | -ti     | 80      | timestep interval for robot drawing <br>(if interval is hybrid, it should be about 40) |
| --blur              | -b      | 0       |in case of jpg, timesteps for rendering motion blur, 0 means no blur |
| --blur-temperature  | -bt     | 0.6     | blur temperature, up to 1.0 |
| --distance-interval | -di     | 0.8     | distance interval for robot drawing |
| --display-timestep  |         | *false* | display timestep above robot |
| --draw-trajectory   |         | *false* | draw robot trajectory as line |
| --num-cores         | -c      | 1       | number of parallel making processes |
| --not-overwrite     |         | *false* | skip process if already figure exists |
| --no-multi          |         | *false* | do without using multiprocessing. if error occur, try this option. |


## Evogym Structure Evolution
### execution
```
$python run_evogym_cppn.py
```
#### options:
| option                | abbrev  | default         | detail  |
| :---                  | :---:   | :---:           | :---    |
| --name                | -n      | "{task}_{robot}"| experiment name |
| --task                | -t      | Walker-v0       | evogym environment id |
| --shape               | -s      | (5,5)           | robot shape <br> usage: "-s {height} {width}" |
| --pop-size            | -p      | 4               | population size of NEAT |
| --generation          | -g      | 500             | iterations of NEAT |
| --ppo-iters           | -i      | 100             | learning iterations of PPO algo <br> on the more complex task, need more. |
| --evaluation-interval | -ei     | 20              | frequency to evaluatie policy |
| --deterministic       | -d      | *false*         | evaluate robot on deterministic action |
| --num-cores           | -c      | 1               | number of parallel evaluation processes |
| --no-view             |         | *false*         | not open simulation window of best robot |

### make figure
after run_evogym_cppn, make {gif, jpg} file for each of all robots written in reward history file.
output to "./out/evogym_cppn/{expt name}/figure/{gif, jpg}/"
```
$python make_figures_cppn.py {experiment name}
```
#### options:
| option              | abbrev  | default | detail  |
| :---                | :---:   | :---:   | :---    |
|                     |         |         | name of experiment for making figures |
| --specified         | -s      |         | input id, make figure for the only specified robot |
| --save-type         | -st     | gif     | file type (choose from [gif, jpg])
| --track-robot       | -rt     | *false* | in case of save type is gif, track robot with camera |
| --interval          | -i      | timestep| in case of save type is jpg, type of interval for robot drawing <br>(choose from [timestep, distance]) |
| --resolution-scale  | -rs     | 32.0    | jpg resolution scale <br> when output monochrome image, try this argument change. |
| --start-timestep    |         | 0       | start timestep of render |
| --timestep-interval | -ti     | 80      | timestep interval for robot drawing <br>(if interval is hybrid, it should be about 40) |
| --blur              | -b      | 0       |in case of jpg, timesteps for rendering motion blur, 0 means no blur |
| --blur-temperature  | -bt     | 0.6     | blur temperature, up to 1.0 |
| --distance-interval | -di     | 0.8     | distance interval for robot drawing |
| --display-timestep  |         | *false* | display timestep above robot |
| --draw-trajectory   |         | *false* | draw robot trajectory as line |
| --deterministic     | -d      | *false* | robot act deterministically |
| --num-cores         | -c      | 1       | number of parallel making processes |
| --not-overwrite     |         | *false* | skip process if already figure exists |
| --no-multi          |         | *false* | do without using multiprocessing. if error occur, try this option. |
