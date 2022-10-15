
import numpy as np
import torch
from torch import nn

from functools import partial

from stable_baselines3.common.utils import obs_as_tensor
from stable_baselines3.common.preprocessing import preprocess_obs
from stable_baselines3.common.distributions import make_proba_distribution
from stable_baselines3.common.torch_layers import MlpExtractor, FlattenExtractor

def init_weights(module, gain=1):
    if isinstance(module, (nn.Linear, nn.Conv2d)):
        nn.init.orthogonal_(module.weight, gain=gain)
        if module.bias is not None:
            module.bias.data.fill_(0.0)

class Policy(nn.Module):
    def __init__(self, observation_spcae, action_space, init_log_std=0.0, device='cpu'):
        super().__init__()

        self.observation_space = observation_spcae
        self.action_space = action_space
        self.device = device

        self.features_extractor = FlattenExtractor(observation_spcae)

        self.mlp_extractor = MlpExtractor(
            observation_spcae.shape[-1],
            net_arch=[dict(pi=[64, 64], vf=[64, 64])],
            activation_fn=nn.Tanh,
            device=device,
        )
        self.mlp_extractor.apply(partial(init_weights, gain=np.sqrt(2)))

        latent_dim_pi = self.mlp_extractor.latent_dim_pi

        self.action_dist = make_proba_distribution(action_space)
        self.action_net, self.log_std = self.action_dist.proba_distribution_net(
            latent_dim=latent_dim_pi, log_std_init=init_log_std
        )
        self.action_net.apply(partial(init_weights, gain=0.01))
        self.value_net = nn.Linear(self.mlp_extractor.latent_dim_vf, 1)
        self.value_net.apply(partial(init_weights, 1))

    def extract_features(self, obs):
        preprocessed_obs = preprocess_obs(obs, self.observation_space)
        return self.features_extractor(preprocessed_obs)

    def forward(self, obs, deterministic=False):
        obs = obs_as_tensor(obs, self.device)
        features = self.extract_features(obs)
        latent_pi, latent_vf = self.mlp_extractor(features)
        values = self.value_net(latent_vf)

        mean_actions = self.action_net(latent_pi)
        distribution = self.action_dist.proba_distribution(mean_actions, self.log_std)
        actions = distribution.get_actions(deterministic=deterministic)
        log_prob = distribution.log_prob(actions)
        actions = actions.reshape((-1,) + self.action_space.shape)
        return actions, values, log_prob

    def predict(self, obs, deterministic=False):
        obs = obs_as_tensor(obs, self.device)
        features = self.extract_features(obs)
        latent_pi = self.mlp_extractor.forward_actor(features)
        mean_actions = self.action_net(latent_pi)
        distribution = self.action_dist.proba_distribution(mean_actions, self.log_std)
        actions = distribution.get_actions(deterministic=deterministic)
        actions = actions.cpu().numpy().reshape((-1,) + self.action_space.shape)
        return actions

    def evaluate_actions(self, obs, actions):
        # obs = obs_as_tensor(obs, self.device)
        features = self.extract_features(obs)
        latent_pi, latent_vf = self.mlp_extractor(features)
        mean_actions = self.action_net(latent_pi)
        distribution = self.action_dist.proba_distribution(mean_actions, self.log_std)
        log_prob = distribution.log_prob(actions)
        values = self.value_net(latent_vf)
        return values, log_prob, distribution.entropy()

    def predict_values(self, obs):
        obs = obs_as_tensor(obs, self.device)
        features = self.extract_features(obs)
        latent_vf = self.mlp_extractor.forward_critic(features)
        return self.value_net(latent_vf)
