# Quality Diversity

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
- --ns-threshold  : initial threshold for novelty archive (default: 6.0)
- --num-knn       : number of nearest neighbors to calculate novelty (default: 15)
- --mcns          : minimal reward criterion (default: 0.01)
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
- --ns-threshold  : initial threshold for novelty archive (default: 0.1)
- --num-knn       : number of nearest neighbors to calculate novelty (default: 10)
- --mcns          : minimal reward criterion (default: 0.0)
- --eval-num      : if probabilistic task, need a certain number (default: 1)
- --num-cores     : number of parallel processes (default: 4)
- --no-plot       : not plot progress figure
- --no-view       : not view simulation of best robot

### make gif
after run_evogym, make gif file for each of all robots written in history files.
output to "./evogym_ut/{expt name}/gif/"
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
