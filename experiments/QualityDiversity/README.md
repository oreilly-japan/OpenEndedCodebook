# Quality Diversity

### execution
```
$python run_evogym_cppn.py
```
#### options:
- -n --name       : experiment name (default: task id)
- -t --task       : task id (default: Walker-v0)
- --shape         : robot shape (usage: "--shape {height} {width}", default: (5,5))
- -b --batch-size : genome num to evaluate in one generation (default: 4)
- -g --generation : generations of neat (default: 100)
- --ppo-iters     : learning iterations of PPO algo (default: 5). on the more complex task, need more.
- --deterministic : evaluate robot deterministically (default: probabilistic)
- --num-cores     : number of parallel processes (default: 1)
- --no-plot       : not plot progress figure
- --no-view       : not view simulation of best robot

### make gif
after run_evogym_cppn, make gif file for each of all robots written in population history file.
output to "./out/evogym_me_cppn/{expt name}/gif/"
```
$python make_gifs_cppn.py -n {experiment name}
```
#### options:
- -n --name             : experiment name
- -r --resolution-ratio : image resolution ratio (default: 0.2 -> (256,144))
- -s --specified        : make gif for only specified robot (usage: "-s {id}")
- --deterministic       : robot act deterministically (default: probabilistically)
- --num-cores           : number of parallel processes (default: 1)
- --not-overwrite       : skip process if already gif exists (default: overwrite)
- --no-multi            : do without using multiprocess. if error occur, try this option.
