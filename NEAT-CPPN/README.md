# NEET CPPN


## Maze
### execution
```
$python run_maze.py
```
#### options:
- -n --name       : experiment name (default: task id)
- -t --task       : task id (default: Walker-v0)
- -p --pop-size   : population size of neat (default: 500)
- -g --generation : generations of neat (default: 500)
- --timesteps     : maze solving simulator steps (default: 400)
- --num-cores     : number of parallel processes (default: 4)
- --no-plot       : not plot progress figure


## Evogym
### execution
```
$python run_evogym.py
```
#### options:
- -n --name       : experiment name (default: task id)
- -t --task       : task id (default: hard)
- -p --pop-size   : population size of neat (default: 200)
- -g --generation : generations of neat (default: 500)
- --eval-num      : if probabilistic task, need a certain times (default: 1)
- --num-cores     : number of parallel processes (default: 4)
- --no-view       : not view simulation of best robot

### make gif
after run_evogym, make gif file for each of all robots written in reward history files.
output to "./evogym_out/{expt name}/gif/"
```
$python make_gifs.py -n {target experiment name}
```
#### options:
- -n --name             : target experiment name
- -r --resolution-ratio : image resolution ratio (default: 0.2 -> (256,144))
- -s --specific         : make gif for only specified robot (how to: "-s {id}")
- --num-cores           : number of parallel processes (default: 1)
- --not-overwrite       : skip process if already gif exists (default: overwrite)
- --no-multi            : do without using multiprocess. if error occur, try this option.


## Evogym Structure Evolution
### execution
```
$python run_evogym_cppn.py
```
#### options:
- -n --name       : experiment name (default: task id)
- -t --task       : task id (default: hard)
- -p --pop-size   : population size of neat (default: 4)
- -g --generation : generations of neat (default: 300)
- --num-cores     : number of parallel processes (default: 4)
- --ppo-iters     : learning iterations of PPO algo (default: 5). on the other task, need more.
- --shape         : robot shape (usage: "--shape {height} {width}", default: (5,5))
- --deterministic : evaluate robot deterministically (default: probabilistic)
- --no-view       : not view simulation of best robot

### make gif
after run_evogym, make gif file for each of all robots written in history files.
output to "./evogym_cppn_out/{expt name}/gif/"
```
$python make_gifs_cppn.py -n {target experiment name}
```
#### options:
- -n --name             : target experiment name
- -r --resolution-ratio : image resolution ratio (default: 0.2 -> (256,144))
- -s --specific         : make gif for only specified robot (how to: "-s {id}")
- --num-cores           : number of parallel processes (default: 1)
- --not-overwrite       : skip process if already gif exists (default: overwrite)
- --no-multi            : do without using multiprocess. if error occur, try this option.
