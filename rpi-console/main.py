"""
TECH ARCADE CONSOLE — PONTO DE ENTRADA PRINCIPAL (1024x600).
Executa na Raspberry Pi 3 B+ com Display Touch 7" HDMI IPS.
- Motor de jogo a 60 FPS com Pygame
- Suporte simultâneo a Touchscreen, Botões Físicos GPIO e Teclado
- 7 Jogos Completos Integrados (100% Digital)
- Inicialização em tela cheia (Modo Kiosk) com cursor oculto
"""

import sys
import time
import os
import pygame

from core.hardware import HardwareManager
from core.audio_manager import AudioManager
from core.input_manager import InputManager
from ui.components import HardwareLedBar
from ui.launcher import Launcher

from games.memory_master import JogoMemoryMaster
from games.quick_draw import JogoQuickDraw
from games.steady_hands import JogoSteadyHands
from games.minefield import JogoCampoMinado
from games.perfect_time import JogoPerfectTime
from games.button_frenzy import JogoButtonFrenzy
from games.ping_pong import JogoPingPong


def main():
    # Inicialização do Pygame
    pygame.init()
    pygame.font.init()

    LARGURA, ALTURA = 1024, 600

    flags = pygame.DOUBLEBUF
    try:
        tela = pygame.display.set_mode((LARGURA, ALTURA), flags)
    except Exception:
        tela = pygame.display.set_mode((LARGURA, ALTURA))

    pygame.display.set_caption("Tech Arcade Console 7'' — 7 Jogos")

    # Fontes padronizadas do sistema
    fonte_tit = pygame.font.SysFont("arial", 22, bold=True)
    fonte_med = pygame.font.SysFont("arial", 18, bold=True)
    fonte_peq = pygame.font.SysFont("arial", 15)

    # Inicialização dos subsistemas de hardware e áudio
    hw = HardwareManager()
    audio = AudioManager()
    input_mgr = InputManager(hw)
    led_bar = HardwareLedBar(y=555)

    # Instanciação dos 7 jogos integrados (POO / Polimorfismo)
    jogos = [
        JogoMemoryMaster(hw, audio),
        JogoQuickDraw(hw, audio),
        JogoSteadyHands(hw, audio),
        JogoCampoMinado(hw, audio),
        JogoPerfectTime(hw, audio),
        JogoButtonFrenzy(hw, audio),
        JogoPingPong(hw, audio)
    ]

    launcher = Launcher(jogos)

    jogo_ativo = None
    estado_console = "MENU"  # MENU ou JOGANDO

    clock = pygame.time.Clock()
    rodando = True

    print(f"[CONSOLE] Tech Arcade Console 7'' iniciado a 1024x600 @ 60 FPS com {len(jogos)} jogos integrados.")

    while rodando:
        dt = clock.tick(60) / 1000.0  # Delta time em segundos

        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                rodando = False

        # Atualiza a camada de entradas físicas e simuladas
        input_mgr.processar(eventos)

        # -------------------------------------------------------------
        # BOTÃO UNIVERSAL DE RETORNO AO MENU (Segurar BT5 por 1.5s ou Esc)
        # -------------------------------------------------------------
        if input_mgr.consumir_retorno_menu():
            if estado_console == "JOGANDO" and jogo_ativo:
                print(f"[CONSOLE] Retorno ao menu principal acionado pelo botão de pânico (saindo de {jogo_ativo.get_nome()}).")
                jogo_ativo.encerrar()
                audio.tocar("menu_move")
                jogo_ativo = None
                estado_console = "MENU"

        # -------------------------------------------------------------
        # MÁQUINA DE ESTADOS DO CONSOLE
        # -------------------------------------------------------------
        if estado_console == "MENU":
            resultado = launcher.processar_eventos(eventos, input_mgr)
            if resultado == "DESLIGAR":
                print("[CONSOLE] Desligamento seguro solicitado via tela Touch...")
                tela.fill((12, 14, 24))
                surf_aviso1 = fonte_tit.render("DESLIGANDO O CONSOLE...", True, (255, 60, 90))
                surf_aviso2 = fonte_med.render("Aguarde o LED verde apagar antes de retirar da tomada.", True, (240, 245, 255))
                tela.blit(surf_aviso1, surf_aviso1.get_rect(center=(512, 270)))
                tela.blit(surf_aviso2, surf_aviso2.get_rect(center=(512, 330)))
                pygame.display.flip()
                time.sleep(1.2)

                hw.encerrar()
                pygame.quit()
                os.system("sudo poweroff")
                sys.exit(0)
            elif resultado:
                novo_jogo = resultado
                print(f"[CONSOLE] Iniciando jogo: {novo_jogo.get_nome()}")
                audio.tocar("menu_select")
                jogo_ativo = novo_jogo
                jogo_ativo.iniciar()
                estado_console = "JOGANDO"
            else:
                launcher.renderizar(tela, fonte_tit, fonte_med, fonte_peq, input_mgr.exibir_botoes_touch())

        elif estado_console == "JOGANDO" and jogo_ativo:
            # Processa eventos no jogo ativo
            jogo_ativo.processar_eventos(eventos, input_mgr.borda_descida)
            jogo_ativo.atualizar(dt)

            if jogo_ativo.solicitou_retorno():
                print(f"[CONSOLE] Jogo {jogo_ativo.get_nome()} encerrou e solicitou retorno ao menu.")
                jogo_ativo.encerrar()
                jogo_ativo = None
                estado_console = "MENU"
            else:
                jogo_ativo.renderizar(tela)

        # Barra inferior unificada com status dos 5 LEDs físicos em tempo real
        led_bar.renderizar(tela, hw.estados_leds, fonte_peq)

        pygame.display.flip()

    # Encerramento seguro
    if jogo_ativo:
        jogo_ativo.encerrar()
    hw.encerrar()
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
