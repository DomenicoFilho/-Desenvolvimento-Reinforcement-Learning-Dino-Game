from env import DinoEnv
from stable_baselines3 import PPO

env = DinoEnv()
modelo = PPO.load("dino_agente")

env.render()
obs, info = env.reset()
terminated = False

while not terminated:
    acao, _ = modelo.predict(obs)
    obs, recompensa, terminated, truncated, info = env.step(acao)

env.close()
