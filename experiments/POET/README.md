# POET


## Evogym
### execution
```
$python run_evogym_poet.py
```
#### options:
| option                | abbrev  | default         | detail  |
| :---                  | :---:   | :---:           | :---    |
| --name                | -n      | default         | experiment name |
| --task                | -t      | Parkour-v0      | task name |
| --robot               | -r      | cat             | robot structure name <br> built in "envs/evogym/robot_files/"           |
| --iteration           | -i      | 3000            | iterations of poet |
| --niche-num           | -n-num  | 10              | limit for niche to hold |
| --reproduce-num       | -r-num  | 10              | number of reproduce at once |
| --admit-child-num     | -ac-num | 1               | limit for admission of child at once |
| --reproduce-interval  | -r-iv   | 30              | reproduce interval |
| --transfer-interval   | -t-iv   | 15              | transfer interval |
| --save-interval       | -s-iv   | 0               | save interval, 0 means no save |
| --reproduce-threshold | -r-th   | 5.0             | threshold of reward to reproduce new niche |
| --mc-lower            | -mc-l   | 0.1             | ratio to maximum reward. used for lower minimal criteria. |
| --mc-upper            | -mc-u   | 0.8             | ratio to maximum reward. used for upper minimal criteria. |
| --width               | -w      | 100             | width of evogym terrain |
| --first-platform      | -fp     | 10              | first platform width of evogym terrain |
| --steps-per-iteration | -si-ppo | 4               | number of steps per iteration of poet |
| --learning-rate       | -lr-ppo | 2.5e-4          | learning rate |
| --epoch               | -e-ppo  | 4               | number of ppo epochs per 1 step of ppo |
| --num-mini-batch      | -b-ppo  | 4               | number of batches for ppo |
| --clip-param          | -c-ppo  | 0.1             | ppo clip parameter |
| --steps               | -s-ppo  | 128             | num steps to use in PPO |
| --num-processes       | -p-ppo  | 4               | number of paralell environment processes for ppo |
| --num-cores           | -c      | 4               | number of parallel evaluation processes |


### make figure
after run_evogym_poet, make {gif, jpg} file for each of all niches.
output to "./out/evogym_poet/{expt name}/figure/{gif, jpg}/"
```
$python make_figures_poet.py {experiment name}
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

