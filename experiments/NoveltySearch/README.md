# Novelty Search


## Maze
### execution
```
$python run_maze.py
```
#### options:
- -n --name         : experiment name (default: "{task}")
- -t --task       : task id (default: hard)
- -p --pop-size   : population size of neat (default: 500)
- -g --generation : generations of neat (default: 500)
- --ns-threshold  : initial threshold for novelty archive (default: 6.0)
- --num-knn       : number of nearest neighbors to calculate novelty (default: 15)
- --mcns          : minimal reward criterion (default: 0.01)
- --timesteps     : maze solving simulator steps (default: 400)
- --num-cores     : number of parallel processes (default: 4)
- --no-plot       : not plot progress figure


## Maze Hyper-NEAT
### execution
```
$python run_maze_hyper.py
```
#### options:
- -n --name         : experiment name (default: "{task}")
- -t --task         : task id (default: medium)
- -p --pop-size     : population size of neat (default: 500)
- -g --generation   : generations of neat (default: 500)
- --ns-threshold  : initial threshold for novelty archive (default: 6.0)
- --num-knn       : number of nearest neighbors to calculate novelty (default: 15)
- --mcns          : minimal reward criterion (default: 0.01)
- --timesteps       : maze solving simulator steps (default: 400)
- --num-cores       : number of parallel processes (default: 4)
- --no-plot         : not plot progress figure


## Evogym
### execution
```
$python run_evogym.py
```
#### options:
- -n --name       : experiment name (default: "{task}_{robot}")
- -t --task       : task id (default: Walker-v0)
- -r --robot      : robot structure name (default: cat, built in "envs/evogym/robot_files/{name}.txt")
- -p --pop-size   : population size of neat (default: 200)
- -g --generation : generations of neat (default: 500)
- --ns-threshold  : initial threshold for novelty archive (default: 0.1)
- --num-knn       : number of nearest neighbors to calculate novelty (default: 5)
- --mcns          : minimal reward criterion (default: 0.0)
- --eval-num      : if probabilistic task, need a certain times (default: 1)
- --num-cores     : number of parallel processes (default: 4)
- --no-plot       : not plot progress figure

### make gif
after run_evogym, make gif file for each of all robots written in history files.
output to "./out/evogym_ns_neat/{expt name}/gif/"
```
$python make_gifs.py -n {experiment name}
```
#### options:
- -n --name             : experiment name
- -r --resolution-ratio : image resolution ratio (default: 0.2 -> (256,144))
- -s --specified        : make gif for only specified robot (usage: "-s {id}")
- --num-cores           : number of parallel processes (default: 1)
- --not-overwrite       : skip process if already gif exists (default: overwrite)
- --no-multi            : do without using multiprocess. if error occur, try this option.


## Evogym Hyper-NEAT
### execution
```
$python run_evogym_hyper.py
```
#### options:
- -n --name       : experiment name (default: "{task}_{robot}")
- -t --task       : task id (default: Walker-v0)
- -r --robot      : robot structure name (default: cat, built in "envs/evogym/robot_files/{name}.txt")
- -p --pop-size   : population size of neat (default: 200)
- -g --generation : generations of neat (default: 500)
- --ns-threshold  : initial threshold for novelty archive (default: 0.1)
- --num-knn       : number of nearest neighbors to calculate novelty (default: 5)
- --mcns          : minimal reward criterion (default: 0.0)
- --use-hidden    : make hidden nodes on NN substrate (default: False)
- --eval-num      : if probabilistic task, need a certain times (default: 1)
- --num-cores     : number of parallel processes (default: 4)
- --no-plot       : not plot progress figure

### make gif
after run_evogym_hyper, make gif file for each of all robots written in history files.
output to "./out/evogym_ns_hyper/{expt name}/gif/"
```
$python make_gifs_hyper.py -n {experiment name}
```
#### options:
- -n --name             : experiment name
- -r --resolution-ratio : image resolution ratio (default: 0.2 -> (256,144))
- -s --specified        : make gif for only specified robot (usage: "-s {id}")
- --num-cores           : number of parallel processes (default: 1)
- --not-overwrite       : skip process if already gif exists (default: overwrite)
- --no-multi            : do without using multiprocess. if error occur, try this option.
