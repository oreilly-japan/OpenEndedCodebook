# Minimal Criterion Coevolution

## Maze
### boostrap
To execute before main mcc process. It prepare initial population.
```
$python boostrap_maze.py
```
#### options:
- -n --name           : boostrap name (default: default)
- --agent-num         : number of agent to prepare (default: 20)
- --maze-num          : number of maze to prepare (default: 10)
- --wall-gene-num     : initial number of wall gene (default: 2)
- --path-gene-num     : initial number of path gene (default: 2)
- --num-cores         : number of parallel process (default: 4)

### mcc
```
$python run_maze.py
```
#### options:
- -n --name         : experiment name (default: default)
- -b --boostrap     : to use boostrap namze (default: default)
- -g --generation   : number of iteration (default: 2000)
- --agent-criteria  : minimal number to solve maze for each agent to survive (default: 1)
- --maze-criteria   : minimal number of agent to solve for each maze to survive (default: 1)
- --agent-pop       : maximum size of agent population (default: 250)
- --maze-pop        : maximum size of maze population (default: 50)
- --agent-limit     : resource limit of agent (default: 0, it means no limit)
- --maze-limit      : resource limit of maze (default: 5)
- --agent-batch     : batch size of agent (default: 40)
- --maze-batch      : batch size of maze (default: 10)
- --num-cores       : number of parallel process (default: 4)
