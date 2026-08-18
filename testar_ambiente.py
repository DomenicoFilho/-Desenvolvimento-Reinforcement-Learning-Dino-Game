from env import DinoEnv #importa a classe (template) do jogo para treino

env = DinoEnv() #Cria o objeto e roda o __init__

for episodio in range(5): #roda 5 vezes para treinar o agente
    obs, info = env.reset() #reseta o jogo e guarda os dados na variável obs e info
    terminated = False
    recompensa_total = 0 #reseta a contagem de recompensa do episódio

    while not terminated:
        acao = env.action_space.sample() #gera uma ação aleatória dentre as do env
        obs, recompensa, terminated, truncated, info = env.step(acao) #executa a ação e guarda os dados
        recompensa_total += recompensa #adiciona a recompensa da ação na soma total do episódio

    print(f"Episódio {episodio + 1}: recompensa total = {recompensa_total}")
    
env.close() #fecha o jogo


       


