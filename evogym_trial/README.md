# evogym trial

Watch the process that robot learn task.

### excution
```
$python run.py --env env_id
```
#### options:
- -t --task       : task id (default: Walker-v0)
- --random        : sampling robot randomly
- --shape         : robot shape (usage: "--shape {height} {width}", default: (5,5))
- --deterministic : robot act deterministically in simulation
