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
| --robot         | -r      | default         | robot structure name <br> built on "envs/evogym/robot_files/" <br> if "default", load default robot of task |
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


### make gif
after run_evogym, make gif file for each of all controllers.
output to "./out/evogym_ppo/{expt name}/gif/"
```
$python make_gifs.py {experiment name}
```
#### options:
| option          | abbrev  | default | detail  |
| :---            | :---:   | :---:   | :---    |
|                 |         |         | name of experiment for making gifs |
| --resolution    | -r      | 0.2     | image resolution ratio (0.2 -> (256,144)) |
| --specified     | -s      |         | input iter, make gif for the only specified controller |
| --num-cores     | -c      | 1       | number of parallel making processes |
| --not-overwrite |         | *false* | skip process if already gif exists |
| --no-multi      |         | *false* | do without using multiprocessing. if error occur, try this option. |
