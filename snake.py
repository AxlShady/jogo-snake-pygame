import pygame
import random
import sys
import os # Para lidar com o arquivo de highscore

# --- 1. Inicialização ---
pygame.init()
pygame.mixer.init() # Inicializa o módulo de som

# --- 2. Definições de Tela e Cores ---
LARGURA_TELA = 600
ALTURA_TELA = 400
TAMANHO_BLOCO = 20

# Cores (RGB)
COR_FUNDO = (0, 0, 0)
COR_COMIDA = (255, 0, 0)
COR_TEXTO = (255, 255, 255)
COR_BOTAO_INATIVO = (100, 100, 100) # Cor para botões
COR_BOTAO_ATIVO = (150, 150, 150)   # Cor quando o mouse está em cima

# Lista de cores para a cobra mudar
CORES_COBRA = [
    (0, 255, 0),   # Verde
    (0, 255, 255), # Ciano
    (255, 255, 0), # Amarelo
    (255, 0, 255), # Magenta
    (0, 0, 255),   # Azul
]

# Configuração da tela
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption('Jogo da Cobrinha (Snake)')

relogio = pygame.time.Clock()
VELOCIDADE_INICIAL = 8 # Começa mais devagar
ARQUIVO_HIGHSCORE = "highscore.txt"

# Fontes
fonte = pygame.font.SysFont(None, 35)
fonte_titulo = pygame.font.SysFont(None, 60)
fonte_pequena = pygame.font.SysFont(None, 25)

# --- 3. Carregar Mídia ---

# Tenta carregar o som, mas não trava se não achar
try:
    # IMPORTANTE: Mude 'som_comer.wav' se seu arquivo tiver outro nome (ex: 'som_comer.mp3')
    som_comer = pygame.mixer.Sound('som_comer.wav') 
except FileNotFoundError:
    print("Aviso: Arquivo de som não encontrado. O jogo rodará sem som.")
    som_comer = None

# --- 4. Funções de Highscore ---

def carregar_highscore():
    if os.path.exists(ARQUIVO_HIGHSCORE):
        try:
            with open(ARQUIVO_HIGHSCORE, 'r') as f:
                return int(f.read())
        except ValueError:
            return 0 # Arquivo corrompido
    return 0

def salvar_highscore(novo_score):
    with open(ARQUIVO_HIGHSCORE, 'w') as f:
        f.write(str(novo_score))

# --- 5. Funções Auxiliares de Desenho ---

def desenhar_texto(texto, fonte, cor, superficie, x, y, centralizado=False):
    textobj = fonte.render(texto, 1, cor)
    textrect = textobj.get_rect()
    if centralizado:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    superficie.blit(textobj, textrect)
    return textrect

def desenhar_botao(texto, x, y, w, h, cor_inativa, cor_ativa):
    mouse_pos = pygame.mouse.get_pos()
    clique = pygame.mouse.get_pressed()
    
    rect = pygame.Rect(x, y, w, h)
    
    clicado = False
    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(tela, cor_ativa, rect)
        if clique[0] == 1: # [0] é o botão esquerdo
            clicado = True
    else:
        pygame.draw.rect(tela, cor_inativa, rect)
        
    desenhar_texto(texto, fonte, COR_TEXTO, tela, x + (w/2), y + (h/2), centralizado=True)
    return rect, clicado

def desenhar_cobra(segmentos_cobra, cor_cobra):
    for segmento in segmentos_cobra:
        pygame.draw.rect(tela, cor_cobra, [segmento[0], segmento[1], TAMANHO_BLOCO, TAMANHO_BLOCO])

def gerar_posicao_comida():
    comida_x = round(random.randrange(0, LARGURA_TELA - TAMANHO_BLOCO) / TAMANHO_BLOCO) * TAMANHO_BLOCO
    comida_y = round(random.randrange(0, ALTURA_TELA - TAMANHO_BLOCO) / TAMANHO_BLOCO) * TAMANHO_BLOCO
    return (comida_x, comida_y)

def exibir_pontuacao(pontos):
    desenhar_texto("Pontos: " + str(pontos), fonte, COR_TEXTO, tela, 10, 10)

# --- 6. Telas do Jogo (Menu, Jogo, Game Over) ---

def mostrar_menu(highscore):
    while True:
        tela.fill(COR_FUNDO)
        desenhar_texto("JOGO DA COBRINHA", fonte_titulo, COR_TEXTO, tela, LARGURA_TELA / 2, ALTURA_TELA / 4, centralizado=True)
        desenhar_texto(f"Maior Pontuação: {highscore}", fonte, COR_TEXTO, tela, LARGURA_TELA / 2, ALTURA_TELA / 2, centralizado=True)

        _, botao_jogar_clicado = desenhar_botao("Jogar", (LARGURA_TELA/2 - 100), (ALTURA_TELA * 0.7), 200, 50, COR_BOTAO_INATIVO, COR_BOTAO_ATIVO)

        if botao_jogar_clicado:
            return # Sai do loop do menu e começa o jogo

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        relogio.tick(15)

def mostrar_tela_game_over(pontos, highscore):
    if pontos > highscore:
        highscore = pontos
        salvar_highscore(highscore)
        
    while True:
        tela.fill(COR_FUNDO)
        desenhar_texto("GAME OVER", fonte_titulo, COR_COMIDA, tela, LARGURA_TELA / 2, ALTURA_TELA / 4, centralizado=True)
        desenhar_texto(f"Sua Pontuação: {pontos}", fonte, COR_TEXTO, tela, LARGURA_TELA / 2, ALTURA_TELA / 2 - 20, centralizado=True)
        desenhar_texto(f"Maior Pontuação: {highscore}", fonte, COR_TEXTO, tela, LARGURA_TELA / 2, ALTURA_TELA / 2 + 20, centralizado=True)

        _, botao_jogar_clicado = desenhar_botao("Tentar Novamente", (LARGURA_TELA/2 - 125), (ALTURA_TELA * 0.7), 250, 50, COR_BOTAO_INATIVO, COR_BOTAO_ATIVO)
        _, botao_menu_clicado = desenhar_botao("Menu", (LARGURA_TELA/2 - 125), (ALTURA_TELA * 0.7) + 60, 250, 50, COR_BOTAO_INATIVO, COR_BOTAO_ATIVO)

        if botao_jogar_clicado:
            return "jogar" # Quer jogar de novo
        if botao_menu_clicado:
            return "menu" # Quer voltar ao menu

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        relogio.tick(15)


def rodar_jogo():
    x1 = LARGURA_TELA / 2
    y1 = ALTURA_TELA / 2
    x1_muda = 0
    y1_muda = 0

    segmentos_cobra = []
    comprimento_cobra = 1
    pontos = 0
    
    velocidade_atual = VELOCIDADE_INICIAL
    cor_cobra_atual = CORES_COBRA[0]
    
    som_ligado = True
    rect_icone_som = pygame.Rect(LARGURA_TELA - 60, 10, 50, 30) # Posição do "botão" de som

    comida_x, comida_y = gerar_posicao_comida()
    
    # --- INÍCIO DA CORREÇÃO ---
    # Cria um retângulo (hitbox) para a comida
    comida_rect = pygame.Rect(comida_x, comida_y, TAMANHO_BLOCO, TAMANHO_BLOCO)
    
    # Enquanto a comida colidir com o botão de som...
    while comida_rect.colliderect(rect_icone_som):
        # Gera uma nova posição para a comida
        comida_x, comida_y = gerar_posicao_comida()
        # Atualiza o hitbox da comida para a nova posição
        comida_rect.update(comida_x, comida_y, TAMANHO_BLOCO, TAMANHO_BLOCO)
    # --- FIM DA CORREÇÃO ---

    game_over = False
    while not game_over:
        
        # --- Manipulação de Eventos (Teclado e Mouse) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rect_icone_som.collidepoint(event.pos):
                    som_ligado = not som_ligado
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_muda == 0:
                    x1_muda = -TAMANHO_BLOCO
                    y1_muda = 0
                elif event.key == pygame.K_RIGHT and x1_muda == 0:
                    x1_muda = TAMANHO_BLOCO
                    y1_muda = 0
                elif event.key == pygame.K_UP and y1_muda == 0:
                    y1_muda = -TAMANHO_BLOCO
                    x1_muda = 0
                elif event.key == pygame.K_DOWN and y1_muda == 0:
                    y1_muda = TAMANHO_BLOCO
                    x1_muda = 0

        # --- Lógica do Jogo ---
        x1 += x1_muda
        y1 += y1_muda

        if x1 >= LARGURA_TELA or x1 < 0 or y1 >= ALTURA_TELA or y1 < 0:
            game_over = True
            
        cabeca_cobra = (x1, y1)
        segmentos_cobra.append(cabeca_cobra)
        if len(segmentos_cobra) > comprimento_cobra:
            del segmentos_cobra[0]

        for segmento in segmentos_cobra[:-1]:
            if segmento == cabeca_cobra:
                game_over = True

        if x1 == comida_x and y1 == comida_y:
            comida_x, comida_y = gerar_posicao_comida()
            
            # --- INÍCIO DA CORREÇÃO (2ª parte) ---
            # Precisamos verificar a colisão da *nova* comida também
            comida_rect.update(comida_x, comida_y, TAMANHO_BLOCO, TAMANHO_BLOCO)
            while comida_rect.colliderect(rect_icone_som):
                comida_x, comida_y = gerar_posicao_comida()
                comida_rect.update(comida_x, comida_y, TAMANHO_BLOCO, TAMANHO_BLOCO)
            # --- FIM DA CORREÇÃO (2ª parte) ---

            comprimento_cobra += 1
            pontos += 1
            
            if som_ligado and som_comer:
                som_comer.play()
                
            if pontos % 5 == 0:
                velocidade_atual += 1 
                indice_cor = (pontos // 5) % len(CORES_COBRA) 
                cor_cobra_atual = CORES_COBRA[indice_cor]

        # --- Renderização ---
        tela.fill(COR_FUNDO)
        pygame.draw.rect(tela, COR_COMIDA, [comida_x, comida_y, TAMANHO_BLOCO, TAMANHO_BLOCO])
        desenhar_cobra(segmentos_cobra, cor_cobra_atual)
        exibir_pontuacao(pontos)
        
        texto_som = "Som: ON" if som_ligado else "Som: OFF"
        cor_som = (0, 200, 0) if som_ligado else (200, 0, 0)
        pygame.draw.rect(tela, cor_som, rect_icone_som)
        desenhar_texto(texto_som, fonte_pequena, COR_TEXTO, tela, rect_icone_som.centerx, rect_icone_som.centery, centralizado=True)

        pygame.display.update()

        relogio.tick(velocidade_atual)

    # Quando o loop (while not game_over) termina, retorna os pontos
    return pontos 

# --- 7. Loop Principal (Controlador do Jogo) ---

def main():
    highscore_atual = carregar_highscore()
    estado_jogo = "menu" # Estados podem ser "menu", "jogando", "game_over"

    while True:
        if estado_jogo == "menu":
            mostrar_menu(highscore_atual)
            estado_jogo = "jogando" # Saiu do menu, começa a jogar
        
        elif estado_jogo == "jogando":
            pontos_finais = rodar_jogo()
            if pontos_finais > highscore_atual:
                highscore_atual = pontos_finais
                salvar_highscore(highscore_atual)
            estado_jogo = "game_over"
            
        elif estado_jogo == "game_over":
            escolha = mostrar_tela_game_over(pontos_finais, highscore_atual)
            if escolha == "jogar":
                estado_jogo = "jogando"
            elif escolha == "menu":
                estado_jogo = "menu"

# --- Inicia o Jogo ---
main() 