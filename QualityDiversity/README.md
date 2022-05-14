# Quality Diversity

### execution
```
$python run.py
```
#### options:
- -n --name       : experiment name (default: task id)
- -t --task       : task id (default: Walker-v0)
- -b --batch-size : genome num to evaluate in one generation (default: 4)
- -g --generation : generations of neat (default: 100)
- --num-cores     : number of parallel processes (default: 1)
- --ppo-iters     : learning iterations of PPO algo (default: 5). on the other task, need more.
- --shape         : robot shape (usage: "--shape {height} {width}", default: (5,5))
- --deterministic : evaluate robot deterministically (default: probabilistic)
- --no-view       : not view simulation of best robot

### make gif
after searching robot structures, make gif file for each of all robots.
output to "./out/{expt name}/gif/"
```
$python make_gifs.py -n {target experiment name}
```
#### options:
- -n --name             : target experiment name
- -r --resolution-ratio : image resolution ratio (default: 0.2 -> (256,144))
- -s --specified        : make gif for only specified robot (usage: "-s {id}")
- --num-cores           : number of parallel processes (default: 1)
- --deterministic       : robot act deterministically (default: probabilistic)
- --not-overwrite       : skip process if already gif exists (default: overwrite)
- --no-multi            : do without using multiprocess. if error occur, try this option.
