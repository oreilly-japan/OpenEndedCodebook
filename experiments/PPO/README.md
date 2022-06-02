# NEET


## Evogym
### execution
```
$python run_evogym.py
```
#### options:
| option          | abbrev  | default         | detail  |
| :---            | :---:   | :---:           | :---    |
| --name          | -n      | "{task}_{robot}"| experiment name |
| --task          | -t      | Walker-v0       | evogym environment id |
| --robot         | -r      | default         | robot structure name <br> built on "envs/evogym/robot_files/" <br> if "default", load default robot for the task |
| --num-processes | -p      | 4               | how many training CPU processes to use |
| --steps         | -s      | 128             | num steps to use in PPO |
| --num-mini-batch| -b      | 4               | number of batches for ppo |
| --epochs        | -e      | 8               | number of ppo epochs |
| --ppo-iters     | -i      | 100             | learning iterations of PPO |
| --lerning-rate  | -lr     | 3e-4            | learning rate |
| --gamma         |         | 0.99            | discount factor for rewards |
| --clip-range    | -c      | 0.3             | ppo clip parameter |
| --deterministic | -d      | *false*         | robot act deterministic |
| --no-view       |         | *false*         | not open simulation window of best robot |


### make figure
after run_evogym, make {gif, jpg} file for each of all controllers.
output to "./out/evogym_ppo/{expt name}/{gif, jpg}/"
```
$python make_figures.py {experiment name}
```
#### options:
| option              | abbrev  | default | detail  |
| :---                | :---:   | :---:   | :---    |
|                     |         |         | name of experiment for making figures |
| --specified         | -s      |         | input iter, make figure for the only specified controller |
| --save-type         | -st     | gif     | file type (choose from [gif, jpg])
| --resolution-ratio  | -r      | 0.2     | gif resolution ratio (0.2 -> (256,144)) |
| --interval          | -i      | timestep| in case of save type is jpg, type of interval for robot drawing <br>(choose from [timestep, distance, hybrid]) |
| --resolution-scale  | -rs     | 30.0    | jpg resolution scale <br> when output monochrome image, try this argument change. |
| --timestep-interval | -ti     | 80      | timestep interval for robot drawing <br>(if interval is hybrid, it should be about 40) |
| --distance-interval | -di     | 0.8     | distance interval for robot drawing |
| --display-timestep  |         | *false* | display timestep above robot |
| --num-cores         | -c      | 1       | number of parallel making processes |
| --not-overwrite     |         | *false* | skip process if already figure exists |
| --no-multi          |         | *false* | do without using multiprocessing. if error occur, try this option. |
