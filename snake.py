import pygame
import random
import sys
import os
import json 

# --- 1. Inicialização ---
pygame.init()
pygame.mixer.init()

# --- 2. Definições de Tela e Cores ---
LARGURA_TELA = 600
ALTURA_TELA = 400
TAMANHO_BLOCO = 20

COR_FUNDO = (0, 0, 0)
COR_COMIDA_FALLBACK = (255, 0, 0)
COR_TEXTO = (255, 255, 255)
COR_BOTAO_INATIVO = (100, 100, 100)
COR_BOTAO_ATIVO = (150, 150, 150)
COR_INPUT_ATIVO = (200, 200, 200)
COR_INPUT_INATIVO = (100, 100, 100)

CORES_COBRA = [(0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 0, 255), (0, 0, 255)]

# Configuração da tela
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption('Jogo da Cobrinha (Snake) by Uninassau')

relogio = pygame.time.Clock()
VELOCIDADE_INICIAL = 8
ARQUIVO_HIGHSCORE = "highscores.json"
NOME_FONTE = "minha_fonte.ttf"

# --- 3. Carregar Fontes ---

try:
    # Fontes diminuídas (v3.2)
    fonte_pequena = pygame.font.Font(NOME_FONTE, 20)
    fonte = pygame.font.Font(NOME_FONTE, 30)
    fonte_titulo = pygame.font.Font(NOME_FONTE, 50)
except (FileNotFoundError, pygame.error):
    print(f"Aviso: Fonte '{NOME_FONTE}' não encontrada. Usando fonte padrão.")
    fonte_pequena = pygame.font.SysFont(None, 20)
    fonte = pygame.font.SysFont(None, 30)
    fonte_titulo = pygame.font.SysFont(None, 50)

# --- 4. Carregar Mídia ---

try:
    som_comer = pygame.mixer.Sound('som_comer.wav')
except FileNotFoundError:
    print("Aviso: 'som_comer.wav' não encontrado.")
    som_comer = None

imagem_cobra_segmento = None # Imagem da cobra não será usada

try:
    temp_img = pygame.image.load('fruta.png').convert_alpha()
    imagem_fruta = pygame.transform.scale(temp_img, (TAMANHO_BLOCO, TAMANHO_BLOCO))
except (FileNotFoundError, pygame.error):
    print("Aviso: 'fruta.png' não encontrada.")
    imagem_fruta = None

try:
    logo_uninassau = pygame.image.load('logo.png').convert_alpha()
    largura_original, altura_original = logo_uninassau.get_size()
    nova_largura = 150
    nova_altura = int(altura_original * (nova_largura / largura_original))
    logo_uninassau = pygame.transform.scale(logo_uninassau, (nova_largura, nova_altura))
except (FileNotFoundError, pygame.error):
    print("Aviso: 'logo.png' não encontrada.")
    logo_uninassau = None

try:
    icone_pause = pygame.image.load('pause.png').convert_alpha()
    icone_pause = pygame.transform.scale(icone_pause, (20, 20))
    icone_play = pygame.image.load('play.png').convert_alpha()
    icone_play = pygame.transform.scale(icone_play, (20, 20))
except (FileNotFoundError, pygame.error):
    print("Aviso: Ícones de pause/play não encontrados.")
    icone_pause, icone_play = None, None


# --- 5. Funções de Highscore (JSON) ---

def carregar_highscores():
    if not os.path.exists(ARQUIVO_HIGHSCORE):
        return []
    try:
        with open(ARQUIVO_HIGHSCORE, 'r') as f:
            scores = json.load(f)
            scores_ordenados = sorted(scores, key=lambda x: x['score'], reverse=True)
            return scores_ordenados
    except (json.JSONDecodeError, IOError):
        print("Aviso: Arquivo de highscore corrompido ou ilegível.")
        return []

def salvar_highscore(nome, pontos):
    novo_score = {'nome': nome, 'score': pontos}
    scores = carregar_highscores()
    scores.append(novo_score)
    scores_ordenados = sorted(scores, key=lambda x: x['score'], reverse=True)
    try:
        with open(ARQUIVO_HIGHSCORE, 'w') as f:
            json.dump(scores_ordenados[:10], f, indent=4)
    except IOError:
        print("Erro ao salvar highscore.")

# --- 6. Funções Auxiliares de Desenho ---

def desenhar_texto(texto, fonte_obj, cor, superficie, x, y, centralizado=False):
    textobj = fonte_obj.render(texto, 1, cor)
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
        pygame.draw.rect(tela, cor_ativa, rect, border_radius=5)
        if clique[0] == 1:
            clicado = True
    else:
        pygame.draw.rect(tela, cor_inativa, rect, border_radius=5)
        
    desenhar_texto(texto, fonte, COR_TEXTO, tela, x + (w/2), y + (h/2), centralizado=True)
    return rect, clicado

def desenhar_cobra(segmentos_cobra, cor_cobra, imagem_cobra):
    if imagem_cobra: # Fallback (embora imagem_cobra_segmento seja None)
        for segmento in segmentos_cobra:
            tela.blit(imagem_cobra, (segmento[0], segmento[1]))
    else:
        for segmento in segmentos_cobra:
            pygame.draw.rect(tela, cor_cobra, [segmento[0], segmento[1], TAMANHO_BLOCO, TAMANHO_BLOCO])


def gerar_pos_comida():
    comida_x = round(random.randrange(0, LARGURA_TELA - TAMANHO_BLOCO) / TAMANHO_BLOCO) * TAMANHO_BLOCO
    comida_y = round(random.randrange(0, ALTURA_TELA - TAMANHO_BLOCO) / TAMANHO_BLOCO) * TAMANHO_BLOCO
    return (comida_x, comida_y)

def exibir_pontuacao(pontos):
    desenhar_texto("Pontos: " + str(pontos), fonte, COR_TEXTO, tela, 10, 10)

# --- 7. Telas do Jogo (Menu, Jogo, Game Over) ---

##-- MODIFICADO --## para 8 caracteres
def pedir_nome_jogador():
    nome = ""
    input_box = pygame.Rect(LARGURA_TELA/2 - 150, ALTURA_TELA/2 - 25, 300, 50)
    ativo = False
    
    while True:
        tela.fill(COR_FUNDO)
        if logo_uninassau:
            logo_rect = logo_uninassau.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA * 0.25))
            tela.blit(logo_uninassau, logo_rect)

        # ##-- MODIFICADO --## Texto atualizado
        desenhar_texto("Digite seu nome (até 8 letras):", fonte, COR_TEXTO, tela, LARGURA_TELA/2, ALTURA_TELA/2 - 60, centralizado=True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                ativo = input_box.collidepoint(event.pos)
            if event.type == pygame.KEYDOWN:
                if ativo:
                    if event.key == pygame.K_RETURN:
                        # ##-- MODIFICADO --## Permite de 1 a 8 caracteres
                        if len(nome) > 0 and len(nome) <= 8:
                            return nome.upper()
                    elif event.key == pygame.K_BACKSPACE:
                        nome = nome[:-1]
                    # ##-- MODIFICADO --## Limite de 8 e aceita letras/números
                    elif event.unicode.isalnum() and len(nome) < 8:
                        nome += event.unicode
                        
        cor_borda = COR_INPUT_ATIVO if ativo else COR_INPUT_INATIVO
        pygame.draw.rect(tela, cor_borda, input_box, 2, border_radius=5)
        
        # ##-- MODIFICADO --## Usa fonte normal para o nome, para caber 8 letras
        desenhar_texto(nome.upper(), fonte_titulo, COR_TEXTO, tela, input_box.centerx, input_box.centery, centralizado=True)
        
        # ##-- MODIFICADO --## Mostra o prompt se o nome for válido
        if len(nome) > 0 and len(nome) <= 8:
            desenhar_texto("Pressione ENTER para começar", fonte_pequena, COR_TEXTO, tela, LARGURA_TELA/2, ALTURA_TELA - 50, centralizado=True)

        pygame.display.update()
        relogio.tick(15)


def mostrar_menu(highscores):
    while True:
        tela.fill(COR_FUNDO)
        if logo_uninassau:
            logo_rect = logo_uninassau.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA * 0.20))
            tela.blit(logo_uninassau, logo_rect)
        
        desenhar_texto("JOGO DA COBRINHA", fonte_titulo, COR_TEXTO, tela, LARGURA_TELA / 2, ALTURA_TELA * 0.40, centralizado=True)
        
        desenhar_texto("Melhores Pontuações:", fonte, COR_TEXTO, tela, LARGURA_TELA / 2, ALTURA_TELA * 0.55, centralizado=True)
        
        if not highscores:
            desenhar_texto("Ninguém jogou ainda!", fonte_pequena, COR_TEXTO, tela, LARGURA_TELA / 2, ALTURA_TELA * 0.65, centralizado=True)
        else:
            pos_y = ALTURA_TELA * 0.65
            for i, score_entry in enumerate(highscores[:3]):
                placar = f"{i+1}. {score_entry['nome']} - {score_entry['score']}"
                desenhar_texto(placar, fonte, COR_TEXTO, tela, LARGURA_TELA / 2, pos_y, centralizado=True)
                pos_y += 35

        _, botao_jogar_clicado = desenhar_botao("Jogar", (LARGURA_TELA/2 - 100), (ALTURA_TELA * 0.85), 200, 50, COR_BOTAO_INATIVO, COR_BOTAO_ATIVO)

        if botao_jogar_clicado:
            return 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        relogio.tick(15)

def mostrar_tela_game_over(pontos, nome_jogador):
    scores = carregar_highscores()
    
    if pontos > 0:
        salvar_highscore(nome_jogador, pontos)
    
    highscores_atualizados = carregar_highscores()
    
    while True:
        tela.fill(COR_FUNDO)
        desenhar_texto("GAME OVER", fonte_titulo, COR_COMIDA_FALLBACK, tela, LARGURA_TELA / 2, ALTURA_TELA / 4, centralizado=True)
        desenhar_texto(f"Sua Pontuação ({nome_jogador}): {pontos}", fonte, COR_TEXTO, tela, LARGURA_TELA / 2, ALTURA_TELA / 2 - 20, centralizado=True)
        
        placar_top1 = highscores_atualizados[0] if highscores_atualizados else {'nome': '---', 'score': 0}
        desenhar_texto(f"Maior Pontuação: {placar_top1['nome']} - {placar_top1['score']}", fonte, COR_TEXTO, tela, LARGURA_TELA / 2, ALTURA_TELA / 2 + 20, centralizado=True)

        _, botao_jogar_clicado = desenhar_botao("Tentar Novamente", (LARGURA_TELA/2 - 125), (ALTURA_TELA * 0.7), 250, 50, COR_BOTAO_INATIVO, COR_BOTAO_ATIVO)
        _, botao_menu_clicado = desenhar_botao("Menu", (LARGURA_TELA/2 - 125), (ALTURA_TELA * 0.7) + 60, 250, 50, COR_BOTAO_INATIVO, COR_BOTAO_ATIVO)

        if botao_jogar_clicado:
            return "jogar"
        if botao_menu_clicado:
            return "menu"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
        relogio.tick(15)

def mostrar_tela_pause():
    pausado = True
    while pausado:
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        tela.blit(overlay, (0, 0))
        
        desenhar_texto("PAUSADO", fonte_titulo, COR_TEXTO, tela, LARGURA_TELA/2, ALTURA_TELA/2 - 50, centralizado=True)
        desenhar_texto("Pressione P para continuar", fonte, COR_TEXTO, tela, LARGURA_TELA/2, ALTURA_TELA/2 + 20, centralizado=True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pausado = False
        
        pygame.display.update()
        relogio.tick(15)


def rodar_jogo():
    x1, y1 = LARGURA_TELA / 2, ALTURA_TELA / 2
    x1_muda, y1_muda = 0, 0
    segmentos_cobra = []
    comprimento_cobra = 1
    pontos = 0
    velocidade_atual = VELOCIDADE_INICIAL
    cor_cobra_atual = CORES_COBRA[0]
    
    som_ligado = True
    
    rect_icone_som = pygame.Rect(LARGURA_TELA - 90, 10, 80, 30)
    rect_icone_pause = pygame.Rect(LARGURA_TELA - 120, 10, 25, 30)

    comida_x, comida_y = gerar_pos_comida()
    comida_rect = pygame.Rect(comida_x, comida_y, TAMANHO_BLOCO, TAMANHO_BLOCO)
    
    ui_rects = [rect_icone_som, rect_icone_pause] 
    
    while comida_rect.collidelist(ui_rects) != -1:
        comida_x, comida_y = gerar_pos_comida()
        comida_rect.update(comida_x, comida_y, TAMANHO_BLOCO, TAMANHO_BLOCO)

    game_over = False
    while not game_over:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rect_icone_som.collidepoint(event.pos):
                    som_ligado = not som_ligado
                elif rect_icone_pause.collidepoint(event.pos):
                    mostrar_tela_pause()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    mostrar_tela_pause()
                elif event.key == pygame.K_LEFT and x1_muda == 0:
                    x1_muda, y1_muda = -TAMANHO_BLOCO, 0
                elif event.key == pygame.K_RIGHT and x1_muda == 0:
                    x1_muda, y1_muda = TAMANHO_BLOCO, 0
                elif event.key == pygame.K_UP and y1_muda == 0:
                    x1_muda, y1_muda = 0, -TAMANHO_BLOCO
                elif event.key == pygame.K_DOWN and y1_muda == 0:
                    x1_muda, y1_muda = 0, TAMANHO_BLOCO

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
            comida_x, comida_y = gerar_pos_comida()
            comida_rect.update(comida_x, comida_y, TAMANHO_BLOCO, TAMANHO_BLOCO)
            while comida_rect.collidelist(ui_rects) != -1:
                comida_x, comida_y = gerar_pos_comida()
                comida_rect.update(comida_x, comida_y, TAMANHO_BLOCO, TAMANHO_BLOCO)

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
        
        if imagem_fruta:
            tela.blit(imagem_fruta, (comida_x, comida_y))
        else:
            pygame.draw.rect(tela, COR_COMIDA_FALLBACK, [comida_x, comida_y, TAMANHO_BLOCO, TAMANHO_BLOCO])
        
        desenhar_cobra(segmentos_cobra, cor_cobra_atual, imagem_cobra_segmento) 
        exibir_pontuacao(pontos)
        
        texto_som = "Som: ON" if som_ligado else "Som: OFF"
        cor_som = (0, 200, 0) if som_ligado else (200, 0, 0)
        pygame.draw.rect(tela, cor_som, rect_icone_som, border_radius=5)
        desenhar_texto(texto_som, fonte_pequena, COR_TEXTO, tela, rect_icone_som.centerx, rect_icone_som.centery, centralizado=True)
        
        pygame.draw.rect(tela, COR_BOTAO_INATIVO, rect_icone_pause, border_radius=5)
        if icone_pause:
            tela.blit(icone_pause, rect_icone_pause.topleft + pygame.Vector2(2, 5))

        else:
            desenhar_texto("P", fonte_pequena, COR_TEXTO, tela, rect_icone_pause.centerx, rect_icone_pause.centery, centralizado=True)

        pygame.display.update()

        relogio.tick(velocidade_atual)

    return pontos 

# --- 8. Loop Principal (Controlador do Jogo) ---

def main():
    estado_jogo = "menu"
    nome_jogador = "JOG"

    while True:
        highscores = carregar_highscores()
        
        if estado_jogo == "menu":
            mostrar_menu(highscores)
            estado_jogo = "pedir_nome"
        
        elif estado_jogo == "pedir_nome":
            nome_jogador = pedir_nome_jogador()
            estado_jogo = "jogando"
        
        elif estado_jogo == "jogando":
            pontos_finais = rodar_jogo() 
            estado_jogo = "game_over"
            
        elif estado_jogo == "game_over":
            escolha = mostrar_tela_game_over(pontos_finais, nome_jogador)
            if escolha == "jogar":
                estado_jogo = "jogando" # Joga de novo com o mesmo nome
            elif escolha == "menu":
                estado_jogo = "menu"

# --- Inicia o Jogo ---
main()