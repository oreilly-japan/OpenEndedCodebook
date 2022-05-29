import pickle
import numpy as np

from PIL import Image
import imageio
from pygifsicle import gifsicle

from gym_utils import make_vec_envs

from stable_baselines3 import PPO


def pool_init_func(lock_):
    global lock
    lock = lock_


def save_controller_gif(env_id, structure, genome_key, genome_file, genome_config, decode_function, gif_file, resolution):

    with open(genome_file, 'rb') as f:
        genome = pickle.load(f)


    env = make_vec_envs(env_id, structure, 0, 1, allow_early_resets=False)
    env.get_attr("default_viewer", indices=None)[0].set_resolution(resolution)

    controller = decode_function(genome, genome_config)

    done = False
    obs = env.reset()
    img = env.render(mode='img')
    imgs = [img]
    while not done:
        action = np.array(controller.activate(obs[0]))*2 - 1
        obs, _, done, infos = env.step([action])
        img = env.render(mode='img')
        imgs.append(img)

    env.close()

    imageio.mimsave(gif_file, imgs, duration=(1/50.0))

    with lock:
        gifsicle(sources=gif_file,
                 destination=gif_file,
                 optimize=False,
                 colors=64,
                 options=["--optimize=3","--no-warnings"])

    print(f'genome {genome_key} ... done')
    return


def save_structure_gif(env_id, genome_key, ppo_file, structure_file, gif_file, resolution, deterministic=False):

    controller = PPO.load(ppo_file)

    structure_data = np.load(structure_file)
    structure = (structure_data['robot'], structure_data['connectivity'])

    env = make_vec_envs(env_id, structure, 1000, 1, allow_early_resets=False)
    env.get_attr("default_viewer", indices=None)[0].set_resolution(resolution)
    env.obs_rms = controller.env.obs_rms

    done = False
    obs = env.reset()
    img = env.render(mode='img')
    imgs = [img]
    while not done:
        action, _ = controller.predict(obs, deterministic=deterministic)
        obs, _, done, infos = env.step(action)
        img = env.render(mode='img')
        imgs.append(img)

    env.close()

    imageio.mimsave(gif_file, imgs, duration=(1/50.0))

    with lock:
        gifsicle(sources=gif_file,
                 destination=gif_file,
                 optimize=False,
                 colors=64,
                 options=["--optimize=3","--no-warnings"])

    print(f'robot {genome_key} ... done')
    return
