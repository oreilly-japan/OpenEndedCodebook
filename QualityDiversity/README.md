# Quality Diversity

### excution
```
$python run.py
```
#### options:
- -n --name       : experiment name (default: task id)
- -t --task       : task id (default: Walker-v0)
- -p --pop-size   : population size of neat (default: 4)
- -g --generation : generations of neat (default: 100)
- --num-cores     : num of multiprocesses (default: 1)
- --ppo-iters     : learning iterations of PPO algo (default: 5). on the other environment, need more.
- --height        : height of robot structure (default: 5)
- --width         : width of robot structure (default: 5)
- --no_plot       : not plot progress figure
- --no_view       : not view simulation of best robot
