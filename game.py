import os
import pygame
import sys
import random

pygame.init()


screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption('Jogo da Nave')

base_path = os.path.dirname(__file__)


nave_img = pygame.image.load(os.path.join(base_path, 'Nave.png'))
nave_img = pygame.transform.scale(nave_img, (50, 50))

tiro_img = pygame.image.load(os.path.join(base_path, 'Tiro.png'))
tiro_img = pygame.transform.scale(tiro_img, (10, 20))

inimigo_img = pygame.image.load(os.path.join(base_path, 'Inimigo.png'))
inimigo_img = pygame.transform.scale(inimigo_img, (50, 50))

font_path = os.path.join(base_path, '8bit16.ttf')
font = pygame.font.Font(font_path, 36)
small_font = pygame.font.Font(font_path, 24)  

nave_rect = nave_img.get_rect(midbottom=(WIDTH // 2, HEIGHT - 30))
nave_speed = 1.5

tiros = []
inimigos = []
spawn_cooldown = 1000  
ultimo_spawn = pygame.time.get_ticks()

# Configuração do joystick
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

cooldown_tiro = 300  
ultimo_tiro = pygame.time.get_ticks()

pontos = 0

jogo_ativo = False
menu_ativo = True
nome_ativo = True
letras = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '
nome_jogador = ['A', 'A', 'A', 'A', 'A', 'A',]
indice_letra = 0
indice_nome = 0

def desenhar_menu():
    screen.fill((0, 0, 0))
    menu_text = small_font.render('Pressione Start para iniciar', True, (255, 255, 255))
    screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT // 2 - menu_text.get_height() // 2))
    
    pontuacoes_text = carregar_pontuacoes()
    for i, pontuacao in enumerate(pontuacoes_text):
        pontuacao_render = small_font.render(pontuacao, True, (255, 255, 255))
        screen.blit(pontuacao_render, (10, 10 + i * 30))  # Alinhado à esquerda

    pygame.display.flip()

def desenhar_nome():
    screen.fill((0, 0, 0))
    nome_text = ''.join(nome_jogador)
    nome_render = font.render(f'Seu Nome: {nome_text}', True, (255, 255, 255))
    screen.blit(nome_render, (WIDTH // 2 - nome_render.get_width() // 2, HEIGHT // 2 - 50))

    for i, letra in enumerate(nome_jogador):
        color = (255, 0, 0) if i == indice_nome else (255, 255, 255)
        letra_render = font.render(letra, True, color)
        screen.blit(letra_render, (WIDTH // 2 - nome_render.get_width() // 2 + i * 40, HEIGHT // 2))

    confirm_text = small_font.render('Pressione Start para confirmar', True, (255, 255, 255))
    screen.blit(confirm_text, (WIDTH // 2 - confirm_text.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()

def carregar_pontuacoes():
    arquivo = os.path.join(base_path, 'pontuacoes.txt')
    pontuacoes = []
    if os.path.exists(arquivo):
        with open(arquivo, 'r') as f:
            pontuacoes = f.readlines()
    
    pontuacoes = [p.strip() for p in pontuacoes if p.strip()]
    return pontuacoes[:10]

def atirar():
    global ultimo_tiro
    agora = pygame.time.get_ticks()
    if agora - ultimo_tiro >= cooldown_tiro:
        tiro_rect = tiro_img.get_rect(midtop=nave_rect.midtop)
        tiros.append(tiro_rect)
        ultimo_tiro = agora  # Atualiza o último tiro
    return ultimo_tiro

def spawn_inimigo():
    inimigo_x = random.randint(0, WIDTH - inimigo_img.get_width())
    inimigo_y = 0
    inimigo_speed = random.uniform(0.5, 1.5)  
    inimigo_rect = pygame.Rect(inimigo_x, inimigo_y, inimigo_img.get_width(), inimigo_img.get_height())
    inimigos.append({"rect": inimigo_rect, "speed": inimigo_speed})

def reiniciar_jogo():
    global pontos, tiros, inimigos, nave_rect, jogo_ativo, menu_ativo, nome_ativo
    pontos = 0
    tiros = []
    inimigos = []
    nave_rect.midbottom = (WIDTH // 2, HEIGHT - 30)
    jogo_ativo = True
    menu_ativo = False
    nome_ativo = False
    nome_jogador[:] = ['A', 'A', 'A']  # Redefine o nome do jogador para o valor inicial

def reiniciar_fase_jogo():
    global pontos, tiros, inimigos, nave_rect, ultimo_spawn
    pontos = 0
    tiros = []
    inimigos = []
    nave_rect.midbottom = (WIDTH // 2, HEIGHT - 30)
    ultimo_spawn = pygame.time.get_ticks()  # Reinicie o cooldown para spawnar inimigos

def salvar_pontuacao(nome, pontuacao):
    arquivo = os.path.join(base_path, 'pontuacoes.txt')
    pontuacoes = []
    if os.path.exists(arquivo):
        with open(arquivo, 'r') as f:
            pontuacoes = f.readlines()
    
    pontuacoes = [p.strip() for p in pontuacoes if p.strip() and ': ' in p]
    pontuacoes.append(f"{nome}: {pontuacao}")
    pontuacoes.sort(key=lambda x: int(x.split(': ')[1]), reverse=True)
    
    with open(arquivo, 'w') as f:
        for ponto in pontuacoes[:10]:
            f.write(ponto + "\n")

def atualizar_joystick():
    global indice_letra, indice_nome, nome_jogador, jogo_ativo, menu_ativo, nome_ativo, ultimo_tiro

    if joystick.get_button(9):  # Start button
        if nome_ativo:
            nome_ativo = False
            menu_ativo = True
        elif menu_ativo:
            menu_ativo = False
            reiniciar_fase_jogo()
            jogo_ativo = True
        elif not jogo_ativo:
            reiniciar_jogo()
    elif joystick.get_button(0):  # South button
        if nome_ativo:
            if indice_nome < len(nome_jogador) - 1:
                indice_nome += 1
            else:
                salvar_pontuacao(''.join(nome_jogador), pontos)
                nome_ativo = False
                menu_ativo = True
        elif jogo_ativo:
            ultimo_tiro = atirar()
    elif joystick.get_button(8):  # Back button
        pygame.quit()
        sys.exit()

def atualizar_entrada_joystick():
    global indice_letra, nome_jogador, indice_nome

    if joystick.get_axis(1) < -0.5:  # Para cima
        indice_letra = (indice_letra - 1) % len(letras)
        nome_jogador[indice_nome] = letras[indice_letra]
    elif joystick.get_axis(1) > 0.5:  # Para baixo
        indice_letra = (indice_letra + 1) % len(letras)
        nome_jogador[indice_nome] = letras[indice_letra]

def main_loop():
    global nave_rect, tiros, inimigos, pontos, jogo_ativo, menu_ativo, nome_ativo, ultimo_spawn

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYAXISMOTION:
                atualizar_joystick()
                if nome_ativo:
                    atualizar_entrada_joystick()

        if nome_ativo:
            desenhar_nome()
        elif menu_ativo:
            desenhar_menu()
        elif jogo_ativo:
            nave_rect.x += joystick.get_axis(0) * nave_speed
            if nave_rect.left < 0:
                nave_rect.left = 0
            if nave_rect.right > WIDTH:
                nave_rect.right = WIDTH

            agora = pygame.time.get_ticks()

            if agora - ultimo_spawn >= spawn_cooldown:
                spawn_inimigo()
                ultimo_spawn = agora

            for inimigo in inimigos[:]:
                inimigo['rect'].y += inimigo['speed']  # Velocidade dos inimigos ajustada
                if inimigo['rect'].top > HEIGHT:
                    inimigos.remove(inimigo)

            for tiro in tiros[:]:
                tiro.y -= 2
                if tiro.bottom < 0:
                    tiros.remove(tiro)

            for tiro in tiros[:]:
                for inimigo in inimigos[:]:
                    if tiro.colliderect(inimigo['rect']):
                        tiros.remove(tiro)
                        inimigos.remove(inimigo)
                        pontos += 1

            for inimigo in inimigos:
                if inimigo['rect'].colliderect(nave_rect):
                    salvar_pontuacao(''.join(nome_jogador), pontos)
                    jogo_ativo = False
                    menu_ativo = True
                    nome_ativo = True
                    break

            screen.fill((0, 0, 0))
            screen.blit(nave_img, nave_rect.topleft)
            for tiro in tiros:
                screen.blit(tiro_img, tiro.topleft)
            for inimigo in inimigos:
                screen.blit(inimigo_img, inimigo['rect'].topleft)

            pontos_text = font.render(f'Pontos: {pontos}', True, (255, 255, 255))
            screen.blit(pontos_text, (10, 10))
            pygame.display.flip()
            

if __name__ == "__main__":
    main_loop()
