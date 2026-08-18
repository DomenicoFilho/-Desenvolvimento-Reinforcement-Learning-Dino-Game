from env import DinoEnv
from stable_baselines3 import PPO

env = DinoEnv() #cria o jogo e roda o init
modelo = PPO("MlpPolicy", env, verbose=1) #cria um objeto (PPO) que chama um agente de ML que funciona a base de números/vetores = MlpPolicy
#verbose = 1 para ele mostrar o resultado no terminal

modelo.learn(total_timesteps=10000000)
modelo.save("dino_agente")
