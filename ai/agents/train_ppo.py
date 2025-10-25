import argparse
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from rover_env.gym_rover_env import RoverEnv

parser = argparse.ArgumentParser()
parser.add_argument('--timesteps', type=int, default=10000)
args = parser.parse_args()

def make_env():
    return RoverEnv(discrete=True, latency_ms=0)

env = DummyVecEnv([make_env])
model = PPO('CnnPolicy', env, verbose=1)
model.learn(total_timesteps=args.timesteps)
model.save('ppo_rover')
