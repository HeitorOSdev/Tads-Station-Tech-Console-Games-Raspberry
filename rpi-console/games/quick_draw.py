"""
Jogo 2: Quick Draw (Duelo de Reflexo para 2 Jogadores).
Aproveita a tela 1024x600 dividida em dois lados (Jogador 1 vs Jogador 2):
- Jogador 1 (Esquerda): BT1 ou Toque na metade esquerda da tela (LED1 indicador)
- Jogador 2 (Direita): BT2 ou Toque na metade direita da tela (LED2 indicador)
- Alerta central (LED3 e sinal sonoro de partida)
- Detecção instantânea de Queima de Largada e medição em milissegundos
"""

import random
import time
import pygame
from core.game_interface import Jogo
from core.hardware import HardwareManager
from core.audio_manager import AudioManager
from ui.components import HeaderBar, COLOR_BG, COLOR_PANEL, COLOR_BORDER, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_CYAN


class JogoQuickDraw(Jogo):
    def __init__(self, hw: HardwareManager, audio: AudioManager):
        self.hw = hw
        self.audio = audio
        self.header = HeaderBar("QUICK DRAW — DUELO DE REFLEXO 2P")
        self.retorno_menu = False

        self.p1_pronto = False
        self.p2_pronto = False
        self.p1_tempo_ms = None
        self.p2_tempo_ms = None
        self.vencedor = None
        self.motivo_fim = ""

        self.estado = "ARMANDO"  # ARMANDO, CONTAGEM, FOGO, RESULTADO
        self.hora_largada = 0.0
        self.timer_resultado = 0.0

        # Metades da tela para toque
        self.rect_p1 = pygame.Rect(40, 90, 450, 420)
        self.rect_p2 = pygame.Rect(534, 90, 450, 420)

    def get_id(self) -> str:
        return "quick_draw"

    def get_nome(self) -> str:
        return "Quick Draw"

    def get_descricao(self) -> str:
        return "Duelo de reflexos para 2 jogadores. Quem atirar mais rápido após o sinal vence!"

    def iniciar(self) -> None:
        self.retorno_menu = False
        self.p1_pronto = False
        self.p2_pronto = False
        self.p1_tempo_ms = None
        self.p2_tempo_ms = None
        self.vencedor = None
        self.motivo_fim = ""
        self.estado = "ARMANDO"
        self.hw.apagar_leds()

    def processar_eventos(self, eventos_pygame: list[pygame.event.Event], estado_botoes: dict[str, bool]) -> None:
        for evento in eventos_pygame:
            if self.header.processar_evento(evento):
                self.retorno_menu = True

            # Toques na tela
            if evento.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                pos = evento.pos if hasattr(evento, "pos") else (int(evento.x * 1024), int(evento.y * 600))
                if self.rect_p1.collidepoint(pos):
                    self._acao_jogador(1)
                elif self.rect_p2.collidepoint(pos):
                    self._acao_jogador(2)

        # Botões físicos
        if estado_botoes.get("BT1"):
            self._acao_jogador(1)
        if estado_botoes.get("BT2"):
            self._acao_jogador(2)

    def _acao_jogador(self, player: int):
        agora = time.time()

        if self.estado == "ARMANDO":
            if player == 1:
                self.p1_pronto = True
                self.hw.set_led(0, True)
            elif player == 2:
                self.p2_pronto = True
                self.hw.set_led(1, True)

            if self.p1_pronto and self.p2_pronto:
                self.hw.apagar_leds()
                self.estado = "CONTAGEM"
                self.hora_largada = agora + random.uniform(2.0, 5.0)

        elif self.estado == "CONTAGEM":
            # Queima de largada!
            self.estado = "RESULTADO"
            self.audio.tocar("erro")
            if player == 1:
                self.vencedor = 2
                self.motivo_fim = "P1 QUEIMOU A LARGADA!"
                self.hw.set_led(1, True)
            else:
                self.vencedor = 1
                self.motivo_fim = "P2 QUEIMOU A LARGADA!"
                self.hw.set_led(0, True)
            self.timer_resultado = agora + 4.5

        elif self.estado == "FOGO":
            # Tiro válido após o sinal
            tempo_reacao = int((agora - self.hora_largada) * 1000)
            self.audio.tocar("tiro")

            if player == 1 and self.p1_tempo_ms is None:
                self.p1_tempo_ms = tempo_reacao
            elif player == 2 and self.p2_tempo_ms is None:
                self.p2_tempo_ms = tempo_reacao

            if self.vencedor is None:
                self.vencedor = player
                self.hw.set_led(0 if player == 1 else 1, True)
                self.motivo_fim = f"JOGADOR {player} VENCEU!"

            if self.p1_tempo_ms is not None and self.p2_tempo_ms is not None:
                self.estado = "RESULTADO"
                self.timer_resultado = agora + 4.5

    def atualizar(self, dt: float) -> None:
        agora = time.time()

        if self.estado == "CONTAGEM":
            if agora >= self.hora_largada:
                self.estado = "FOGO"
                self.hw.set_led(2, True)  # LED central de partida
                self.audio.tocar("largada")

        elif self.estado == "FOGO":
            if agora - self.hora_largada > 4.0:  # Timeout de 4s
                self.estado = "RESULTADO"
                self.timer_resultado = agora + 4.5
                if self.vencedor is None:
                    self.motivo_fim = "TEMPO ESGOTADO! NINGUÉM DISPAROU"

        elif self.estado == "RESULTADO":
            if agora >= self.timer_resultado:
                self.iniciar()

    def renderizar(self, superficie: pygame.Surface) -> None:
        superficie.fill(COLOR_BG)
        fonte_tit = pygame.font.SysFont("arial", 22, bold=True)
        fonte_med = pygame.font.SysFont("arial", 18, bold=True)
        fonte_peq = pygame.font.SysFont("arial", 15)
        fonte_gra = pygame.font.SysFont("arial", 48, bold=True)

        self.header.renderizar(superficie, fonte_tit, fonte_peq)

        # Lado P1
        cor_p1 = (45, 20, 28) if not self.p1_pronto else (80, 25, 35)
        if self.vencedor == 1: cor_p1 = (30, 90, 45)
        pygame.draw.rect(superficie, cor_p1, self.rect_p1, border_radius=16)
        pygame.draw.rect(superficie, COLOR_RED, self.rect_p1, width=2, border_radius=16)

        surf_p1 = fonte_med.render("JOGADOR 1 (BT1)", True, COLOR_RED)
        superficie.blit(surf_p1, surf_p1.get_rect(center=(self.rect_p1.centerx, 130)))

        txt_p1 = "ARMADO!" if self.p1_pronto else "TOQUE OU APERTE BT1"
        if self.p1_tempo_ms is not None: txt_p1 = f"{self.p1_tempo_ms} ms"
        surf_status_p1 = fonte_med.render(txt_p1, True, COLOR_TEXT)
        superficie.blit(surf_status_p1, surf_status_p1.get_rect(center=(self.rect_p1.centerx, 300)))

        # Lado P2
        cor_p2 = (20, 35, 45) if not self.p2_pronto else (25, 60, 80)
        if self.vencedor == 2: cor_p2 = (30, 90, 45)
        pygame.draw.rect(superficie, cor_p2, self.rect_p2, border_radius=16)
        pygame.draw.rect(superficie, COLOR_CYAN, self.rect_p2, width=2, border_radius=16)

        surf_p2 = fonte_med.render("JOGADOR 2 (BT2)", True, COLOR_CYAN)
        superficie.blit(surf_p2, surf_p2.get_rect(center=(self.rect_p2.centerx, 130)))

        txt_p2 = "ARMADO!" if self.p2_pronto else "TOQUE OU APERTE BT2"
        if self.p2_tempo_ms is not None: txt_p2 = f"{self.p2_tempo_ms} ms"
        surf_status_p2 = fonte_med.render(txt_p2, True, COLOR_TEXT)
        superficie.blit(surf_status_p2, surf_status_p2.get_rect(center=(self.rect_p2.centerx, 300)))

        # Centro: Alerta de Partida
        if self.estado == "CONTAGEM":
            surf_centro = fonte_med.render("PREPAREM-SE...", True, COLOR_YELLOW)
            superficie.blit(surf_centro, surf_centro.get_rect(center=(512, 260)))
        elif self.estado == "FOGO":
            surf_fogo = fonte_gra.render("FOGO!", True, COLOR_YELLOW)
            superficie.blit(surf_fogo, surf_fogo.get_rect(center=(512, 260)))
        elif self.estado == "RESULTADO":
            surf_res = fonte_med.render(self.motivo_fim, True, COLOR_YELLOW)
            superficie.blit(surf_res, surf_res.get_rect(center=(512, 260)))

    def encerrar(self) -> None:
        self.hw.apagar_leds()
        self.audio.parar_todos()

    def solicitou_retorno(self) -> bool:
        return self.retorno_menu
