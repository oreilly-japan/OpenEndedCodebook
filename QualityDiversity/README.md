# Quality Diversity

### execution
```
$python run.py
```
#### options:
- -n --name       : experiment name (default: task id)
- -t --task       : task id (default: Walker-v0)
- -p --pop-size   : population size of neat (default: 4)
- -g --generation : generations of neat (default: 100)
- --num-cores     : number of parallel processes (default: 1)
- --ppo-iters     : learning iterations of PPO algo (default: 5). on the other environment, need more.
- --height        : height of robot structure (default: 5)
- --width         : width of robot structure (default: 5)
- --deterministic : evaluate robot deterministic (default: probabilistic)
- --no_plot       : not plot progress figure
- --no_view       : not view simulation of best robot

### make gif
after robot search, make gif file of each robot
```
$python make_gifs.py -n {target experiment name}
```
#### options:
- -n --name             : target experiment name
- -r --resolution-ratio : image resolution ratio (default: 0.2 -> (256,144))
- --num-cores           : number of parallel processes (default: 1)
- --deterministic       : robot act deterministic (default: probabilistic)
- --not-overwrite       : skip process if already gif exists (default: overwrite)
- --no-multi            : do without using multiprocess. if error occur, try this option.
