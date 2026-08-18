import os
import random
import pygame

LARGURA = 600
ALTURA = 150
FPS = 60
GRAVIDADE = 0.6
COR_FUNDO = (235, 235, 235)

# Usamos o caminho absoluto da pasta onde este arquivo está, em vez de um caminho
# relativo tipo 'sprites/nome.png'. Isso resolve o problema que você teve antes
# (FileNotFoundError) quando rodou o jogo de um diretório de trabalho diferente:
# agora funciona não importa de onde o Python for executado.
PASTA_JOGO = os.path.dirname(os.path.abspath(__file__))
PASTA_SPRITES = os.path.join(PASTA_JOGO, 'sprites')


def carregar_imagem(nome, sizex=-1, sizey=-1, colorkey=None):
    caminho = os.path.join(PASTA_SPRITES, nome)
    imagem = pygame.image.load(caminho)
    imagem = imagem.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = imagem.get_at((0, 0))
        imagem.set_colorkey(colorkey, pygame.RLEACCEL)
    if sizex != -1 or sizey != -1:
        imagem = pygame.transform.scale(imagem, (sizex, sizey))
    return imagem, imagem.get_rect()


def carregar_sprite_sheet(nome_arquivo, nx, ny, escalax=-1, escalay=-1, colorkey=None):
    caminho = os.path.join(PASTA_SPRITES, nome_arquivo)
    folha = pygame.image.load(caminho)
    folha = folha.convert()
    folha_rect = folha.get_rect()

    sprites = []
    tamanhox = folha_rect.width // nx
    tamanhoy = folha_rect.height // ny

    for i in range(ny):
        for j in range(nx):
            retangulo = pygame.Rect((j * tamanhox, i * tamanhoy, tamanhox, tamanhoy))
            imagem = pygame.Surface(retangulo.size)
            imagem = imagem.convert()
            imagem.blit(folha, (0, 0), retangulo)

            if colorkey is not None:
                if colorkey == -1:
                    colorkey = imagem.get_at((0, 0))
                imagem.set_colorkey(colorkey, pygame.RLEACCEL)

            if escalax != -1 or escalay != -1:
                imagem = pygame.transform.scale(imagem, (escalax, escalay))

            sprites.append(imagem)

    sprite_rect = sprites[0].get_rect()
    return sprites, sprite_rect


class Dino:
    def __init__(self, sizex=-1, sizey=-1):
        self.images, self.rect = carregar_sprite_sheet('dino.png', 5, 1, sizex, sizey, -1)
        self.images1, self.rect1 = carregar_sprite_sheet('dino_ducking.png', 2, 1, 59, sizey, -1)
        self.rect.bottom = int(0.98 * ALTURA)
        self.rect.left = LARGURA // 15
        self.image = self.images[0]
        self.index = 0
        self.counter = 0
        self.isJumping = False
        self.isDead = False
        self.isDucking = False
        self.movement = [0, 0]
        self.jumpSpeed = 11.5

        self.stand_pos_width = self.rect.width
        self.duck_pos_width = self.rect1.width

    def desenhar(self, tela):
        tela.blit(self.image, self.rect)

    def checar_limites(self):
        if self.rect.bottom > int(0.98 * ALTURA):
            self.rect.bottom = int(0.98 * ALTURA)
            self.isJumping = False

    def atualizar(self):
        if self.isJumping:
            self.movement[1] += GRAVIDADE
            self.index = 0
        elif self.isDucking:
            if self.counter % 5 == 0:
                self.index = (self.index + 1) % 2
        else:
            if self.counter % 5 == 0:
                self.index = (self.index + 1) % 2 + 2

        if self.isDead:
            self.index = 4

        if not self.isDucking:
            self.image = self.images[self.index]
            self.rect.width = self.stand_pos_width
        else:
            self.image = self.images1[self.index % 2]
            self.rect.width = self.duck_pos_width

        self.rect = self.rect.move(self.movement)
        self.checar_limites()

        self.counter += 1


class Cactus(pygame.sprite.Sprite):
    # O método abaixo precisa se chamar exatamente "update" (em inglês), não
    # "atualizar". Não é escolha nossa: pygame.sprite.Group.update() (chamado
    # dentro de Jogo.passo()) procura por esse nome específico em cada sprite
    # do grupo. É o mesmo tipo de "contrato de nome obrigatório" que vimos com
    # action_space/observation_space no env.py, só que agora é um contrato da
    # biblioteca pygame, não do gymnasium.
    def __init__(self, grupo, velocidade=5, sizex=-1, sizey=-1):
        pygame.sprite.Sprite.__init__(self, grupo)
        self.images, self.rect = carregar_sprite_sheet('cacti-small.png', 3, 1, sizex, sizey, -1)
        self.rect.bottom = int(0.98 * ALTURA)
        self.rect.left = LARGURA + self.rect.width
        self.image = self.images[random.randrange(0, 3)]
        self.movement = [-1 * velocidade, 0]

    def update(self):
        self.rect = self.rect.move(self.movement)
        if self.rect.right < 0:
            self.kill()


class Ptera(pygame.sprite.Sprite):
    # Mesmo motivo do Cactus: este método precisa se chamar "update".
    def __init__(self, grupo, velocidade=5, sizex=-1, sizey=-1):
        pygame.sprite.Sprite.__init__(self, grupo)
        self.images, self.rect = carregar_sprite_sheet('ptera.png', 2, 1, sizex, sizey, -1)
        self.alturas_possiveis = [ALTURA * 0.82, ALTURA * 0.75, ALTURA * 0.60]
        self.rect.centery = self.alturas_possiveis[random.randrange(0, 3)]
        self.rect.left = LARGURA + self.rect.width
        self.image = self.images[0]
        self.movement = [-1 * velocidade, 0]
        self.index = 0
        self.counter = 0

    def update(self):
        if self.counter % 10 == 0:
            self.index = (self.index + 1) % 2
        self.image = self.images[self.index]
        self.rect = self.rect.move(self.movement)
        self.counter += 1
        if self.rect.right < 0:
            self.kill()


class Chao:
    def __init__(self, velocidade=-5):
        self.image, self.rect = carregar_imagem('ground.png', -1, -1, -1)
        self.image1, self.rect1 = carregar_imagem('ground.png', -1, -1, -1)
        self.rect.bottom = ALTURA
        self.rect1.bottom = ALTURA
        self.rect1.left = self.rect.right
        self.velocidade = velocidade

    def desenhar(self, tela):
        tela.blit(self.image, self.rect)
        tela.blit(self.image1, self.rect1)

    def atualizar(self):
        self.rect.left += self.velocidade
        self.rect1.left += self.velocidade

        if self.rect.right < 0:
            self.rect.left = self.rect1.right
        if self.rect1.right < 0:
            self.rect1.left = self.rect.right


class Jogo:
    """
    Esta é a classe nova, criada especificamente para este projeto. Ela existe
    porque o main.py original só sabe jogar sozinho: lê teclado real, desenha
    na tela e trava em 60 FPS num único loop `while` que só termina quando o
    dino morre ou a janela fecha.

    Um agente de RL precisa de outra coisa: controlar o jogo UM FRAME DE CADA
    VEZ, de fora, sem depender de teclado real nem de esperar o tempo real
    passar. É exatamente isso que os métodos abaixo oferecem: reiniciar() e
    passo(acao) — o env.py (Etapa 2) vai chamar esses dois métodos dentro do
    reset() e do step() do Gymnasium.

    Reparem que esta classe não sabe nada sobre "observação", "recompensa" ou
    "Gymnasium" — ela só entende o jogo em si (posições, colisão, pontuação
    de velocidade). Quem traduz isso para a linguagem do RL é o env.py.
    """

    def __init__(self, renderizar=False):
        # 'renderizar' controla se vamos de fato desenhar a janela e limitar a
        # velocidade a 60 FPS. Durante o TREINO do agente (Etapa 4) queremos
        # simular milhares de frames por segundo, então usamos renderizar=False.
        # Na VISUALIZAÇÃO do agente já treinado, vamos criar Jogo(renderizar=True).
        self.renderizar = renderizar

        pygame.init()
        # pygame.display.set_mode precisa ser chamado mesmo quando não vamos
        # desenhar nada visível -- é uma exigência interna do pygame: carregar
        # e converter imagens (.convert(), usado em carregar_imagem) só funciona
        # depois que existe uma "superfície" de referência configurada.
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("T-Rex Rush - Ambiente RL")
        self.relogio = pygame.time.Clock()

        self.reiniciar()

    def reiniciar(self):
        """
        Equivale ao início da função gameplay() do main.py original: zera tudo
        para começar um novo episódio. O env.py vai chamar isso dentro do
        reset() dele.
        """
        self.velocidade_jogo = 4
        self.contador = 0
        self.morreu = False

        self.dino = Dino(44, 47)
        self.chao = Chao(-1 * self.velocidade_jogo)

        # Grupos de sprites (recurso do próprio pygame): coleções que sabem
        # atualizar e desenhar vários obstáculos de uma vez só. Recriamos os
        # grupos do zero a cada reiniciar() para não carregar cactos/pteras
        # que sobraram do episódio anterior.
        #
        # Diferença importante em relação ao main.py original: lá, o grupo de
        # cada classe era guardado como atributo DA PRÓPRIA CLASSE inteira
        # (Cactus.containers = cacti), compartilhado globalmente. Isso é
        # frágil para o nosso caso: como reiniciar() vai ser chamado milhares
        # de vezes durante o treino (um episódio atrás do outro), preferimos
        # passar o grupo como parâmetro na criação de cada Cactus/Ptera (veja
        # o passo() abaixo) -- assim cada episódio fica isolado, sem estado
        # compartilhado entre um reiniciar() e o próximo.
        self.cactos = pygame.sprite.Group()
        self.pteras = pygame.sprite.Group()
        self.ultimo_obstaculo = pygame.sprite.Group()

    def passo(self, acao):
        """
        Avança exatamente 1 frame do jogo -- o coração da ponte com o RL.

        acao: 0 = não faz nada, 1 = pula, 2 = abaixa (mesma convenção do
        action_space Discrete(3) que já existe no env.py).

        Retorna True se o dino morreu neste frame (colidiu), False se
        continua vivo. O env.py vai usar esse retorno para decidir o
        'terminated' do step().
        """
        if self.renderizar:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.fechar()

        # Aqui é onde a "ação" do agente substitui o teclado real do humano.
        # Original: só pulava se `playerDino.rect.bottom == chão` (posição
        # exata). Usamos `not self.dino.isJumping` -- equivalente na prática
        # (isJumping só fica False quando o dino já pousou, ver
        # Dino.checar_limites), mas mais direto de ler.
        if acao == 1 and not self.dino.isJumping:
            self.dino.isJumping = True
            self.dino.movement[1] = -1 * self.dino.jumpSpeed

        # Original: isDucking ligava/desligava em eventos separados de tecla
        # pressionada/solta (KEYDOWN/KEYUP), persistindo por vários frames.
        # Aqui simplificamos: cada chamada de passo() já recebe a ação daquele
        # frame específico, então definimos isDucking direto a partir da ação
        # atual -- sem precisar rastrear "tecla ainda segurada".
        self.dino.isDucking = (acao == 2)

        for cacto in self.cactos:
            cacto.movement[0] = -1 * self.velocidade_jogo
            if pygame.sprite.collide_mask(self.dino, cacto):
                self.morreu = True

        for ptera in self.pteras:
            ptera.movement[0] = -1 * self.velocidade_jogo
            if pygame.sprite.collide_mask(self.dino, ptera):
                self.morreu = True

        # Lógica de nascimento de obstáculos: mesmas probabilidades do jogo
        # original (1/50 para novo cacto, 1/200 para pterodáctilo depois do
        # frame 500), só que os grupos agora são passados explicitamente.
        if len(self.cactos) < 2:
            if len(self.cactos) == 0:
                self.ultimo_obstaculo.empty()
                self.ultimo_obstaculo.add(Cactus(self.cactos, self.velocidade_jogo, 40, 40))
            else:
                for obstaculo in self.ultimo_obstaculo:
                    if obstaculo.rect.right < LARGURA * 0.7 and random.randrange(0, 50) == 10:
                        self.ultimo_obstaculo.empty()
                        self.ultimo_obstaculo.add(Cactus(self.cactos, self.velocidade_jogo, 40, 40))

        if len(self.pteras) == 0 and random.randrange(0, 200) == 10 and self.contador > 500:
            for obstaculo in self.ultimo_obstaculo:
                if obstaculo.rect.right < LARGURA * 0.8:
                    self.ultimo_obstaculo.empty()
                    self.ultimo_obstaculo.add(Ptera(self.pteras, self.velocidade_jogo, 46, 40))

        self.dino.atualizar()
        self.cactos.update()
        self.pteras.update()
        self.chao.atualizar()

        if self.renderizar:
            self._desenhar()
            self.relogio.tick(FPS)

        if self.contador % 700 == 699:
            self.chao.velocidade -= 1
            self.velocidade_jogo += 1

        self.contador += 1

        return self.morreu

    def obter_estado(self):
        """
        Devolve as 5 features BRUTAS (ainda não é a "observação" do Gymnasium
        -- isso é papel do env.py), na MESMA ORDEM combinada para o
        observation_space:

        (distancia_obstaculo, altura_obstaculo, velocidade_jogo,
         posicao_vertical_dino, velocidade_vertical_dino)

        O env.py vai chamar isto dentro do reset() e do step() para montar o
        vetor numpy que o agente realmente recebe.
        """
        proximo = self._proximo_obstaculo()
        chao_y = int(0.98 * ALTURA)

        if proximo is None:
            # Só acontece bem no início do episódio, antes do primeiro
            # obstáculo nascer: tratamos como "ameaça o mais longe possível".
            distancia_obstaculo = float(LARGURA)
            altura_obstaculo = float(chao_y)
        else:
            distancia_obstaculo = float(proximo.rect.left - self.dino.rect.right)
            altura_obstaculo = float(proximo.rect.centery)

        posicao_vertical_dino = float(chao_y - self.dino.rect.bottom)
        velocidade_vertical_dino = float(self.dino.movement[1])

        return (
            distancia_obstaculo,
            altura_obstaculo,
            float(self.velocidade_jogo),
            posicao_vertical_dino,
            velocidade_vertical_dino,
        )

    def _proximo_obstaculo(self):
        candidatos = [
            obstaculo for obstaculo in list(self.cactos) + list(self.pteras)
            if obstaculo.rect.right > self.dino.rect.left
        ]
        if not candidatos:
            return None
        return min(candidatos, key=lambda obstaculo: obstaculo.rect.left)

    def _desenhar(self):
        self.tela.fill(COR_FUNDO)
        self.chao.desenhar(self.tela)
        self.cactos.draw(self.tela)
        self.pteras.draw(self.tela)
        self.dino.desenhar(self.tela)
        pygame.display.update()

    def fechar(self):
        pygame.quit()
