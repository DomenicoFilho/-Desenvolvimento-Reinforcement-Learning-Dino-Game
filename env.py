import gymnasium as gym
from gymnasium import spaces
import numpy as np
from jogo import Jogo


class DinoEnv(gym.Env): #cria uma classe (template) para usar nos objetos
    def __init__(self): #função que roda sempre que o objeto usar essa classe
        super().__init__() #chama e carrega a classe mãe corretamente
        # 0 = não faz nada, 1 = pula, 2 = abaixa
        self.action_space = spaces.Discrete(3) #crias 3 possibilidades de ação que o objeto pode fazer
        #posição 0 → distancia_obstaculo
        #posição 1 → altura_obstaculo
        #posição 2 → velocidade_jogo
        #posição 3 → posicao_vertical_dino
        #posição 4 → velocidade_vertical_dino
        limite_minimo = np.array([0,0,0,0,-15], dtype=np.float32) #valores mínimos de dados e o dtype coloca em decimal e 32 bits
        limite_maximo = np.array([700, 150, 100, 150, 15], dtype=np.float32) #valores máximos de dados e o dtype coloca em decimal e 32 bits
        self.observation_space = spaces.Box(low=limite_minimo, high=limite_maximo, dtype=np.float32) #cria uma classe para receber os dados limite do jogo
        self.jogo = Jogo(renderizar=False)

    def reset(self, seed=None, options=None): #função que reinicia o jogo
        super().reset(seed=seed) #arquitetura obrigatória da biblioteca
        self.jogo.reiniciar() #chama a função que reseta o jogo (criada dentro do jogo.py)
        observacao = np.array(self.jogo.obter_estado(), dtype=np.float32) #puxa os dados do jogo e transforma em array
        info = {} #arquitetura obrigatoria tbm
        return observacao, info #retorna os dados do jogo

    def step(self, acao): #função que define oq será executado no jogo
        terminated = self.jogo.passo(acao) #executa a ação no jogo e retorna se o dino continua vivo
        observacao = np.array(self.jogo.obter_estado(), dtype=np.float32) #puxa os dados atualizados do estado do jogo
        if terminated:
            recompensa = -100
        else:
            recompensa = 1
        truncated = False #trunated seria para limitar a quantidade de ações que a função pode executar em uma bateria
        info = {}
        return observacao, recompensa, terminated, truncated, info #retorna todos os dados que foram definidos acima

    def render(self):
        self.jogo.renderizar = True #para mostrar a imagem do jogo

    def close(self):
        self.jogo.fechar() #para fechar a imagem do jogo

        

        





