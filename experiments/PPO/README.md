# PPO


## Evogym
### execution
```
$python run_evogym.py
```
#### options:
| option                | abbrev  | default         | detail  |
| :---                  | :---:   | :---:           | :---    |
| --name                | -n      | "{task}_{robot}"| experiment name |
| --task                | -t      | Walker-v0       | evogym environment id |
| --robot               | -r      | default         | robot structure name <br> built on "envs/evogym/robot_files/" <br> if "default", load default robot for the task |
| --num-processes       | -p      | 4               | how many training CPU processes to use |
| --steps               | -s      | 256             | num steps to use in PPO |
| --num-mini-batch      | -b      | 8               | number of batches for ppo |
| --epochs              | -e      | 8               | number of ppo epochs |
| --train-iters         | -i      | 2500            | learning iterations of PPO |
| --evaluation-interval | -ei     | 25              | frequency to evaluate policy |
| --lerning-rate        | -lr     | 3e-4            | learning rate |
| --gamma               |         | 0.99            | discount factor for rewards |
| --clip-range          | -c      | 0.3             | ppo clip parameter |
| --init-log-std        | -std    | 0.1             | initial log std of action distribution |
| --deterministic       | -d      | *false*         | robot act deterministic |
| --no-view             |         | *false*         | not open simulation window of best robot |


### make figure
after run_evogym, make {gif, jpg} file for each of all controllers.
output to "./out/evogym_ppo/{expt name}/figure/{gif, jpg}/"
```
$python make_figures.py {experiment name}
```
#### options:
| option              | abbrev  | default | detail  |
| :---                | :---:   | :---:   | :---    |
|                     |         |         | name of experiment for making figures |
| --specified         | -s      |         | input iter, make figure for the only specified controller |
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
