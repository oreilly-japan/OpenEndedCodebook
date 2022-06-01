# Quality Diversity


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
| --batch-size    | -b      | 4               | genome number to evaluate in one generation |
| --generation    | -g      | 500             | iterations of NEAT |
| --ppo-iters     | -i      | 5               | learning iterations of PPO algo <br> on the more complex task, need more. |
| --deterministic | -d      | *false*         | evaluate robot on deterministic action |
| --num-cores     | -c      | 1               | number of parallel evaluation processes |
| --no-plot       |         | *false*         | not open window of progress figure |
| --no-view       |         | *false*         | not open simulation window of best robot |

### make gif
after run_evogym_cppn, make gif file for each of all robots written in population history file.
output to "./out/evogym_me_cppn/{expt name}/gif/"
```
$python make_gifs_cppn.py {experiment name}
```
#### options:
| option          | abbrev  | default | detail  |
| :---            | :---:   | :---:   | :---    |
|                 |         |         | name of experiment for making gifs |
| --resolution    | -r      | 0.2     | image resolution ratio (0.2 -> (256,144)) |
| --specified     | -s      |         | input id, make gif for the only specified robot |
| --deterministic | -d      | *false* | robot act deterministically |
| --num-cores     | -c      | 1       | number of parallel making processes |
| --not-overwrite |         | *false* | skip process if already gif exists |
| --no-multi      |         | *false* | do without using multiprocessing. if error occur, try this option. |
