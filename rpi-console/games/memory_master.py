"""
Jogo 1: Memory Master (Desafio da Memória - Genius 4 Cores).
Apresenta 4 setores coloridos táteis na tela 1024x600 sincronizados com os 4 botões e LEDs físicos:
- Cor 0 (Vermelho): BT1 / LED1 / Nota Dó (262 Hz)
- Cor 1 (Verde): BT2 / LED2 / Nota Mi (330 Hz)
- Cor 2 (Azul): BT3 / LED3 / Nota Sol (392 Hz)
- Cor 3 (Amarelo): BT4 / LED4 / Nota Dó Agudo (523 Hz)
"""

import random
import time
import pygame
from core.game_interface import Jogo
from core.hardware import HardwareManager
from core.audio_manager import AudioManager
from ui.components import HeaderBar, COLOR_BG, COLOR_PANEL, COLOR_BORDER, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_YELLOW, COLOR_CYAN


class JogoMemoryMaster(Jogo):
    CORES_BASE = [
        (220, 40, 60),    # 0: Vermelho
        (40, 200, 100),   # 1: Verde
        (30, 130, 240),   # 2: Azul
        (240, 200, 30)    # 3: Amarelo
    ]
    CORES_BRILHO = [
        (255, 120, 140),
        (120, 255, 160),
        (120, 190, 255),
        (255, 240, 120)
    ]
    NOMES_CORES = ["VERMELHO (BT1)", "VERDE (BT2)", "AZUL (BT3)", "AMARELO (BT4)"]

    def __init__(self, hw: HardwareManager, audio: AudioManager):
        self.hw = hw
        self.audio = audio
        self.header = HeaderBar("MEMORY MASTER — DESAFIO GENIUS")
        self.retorno_menu = False

        self.sequencia = []
        self.rodada = 0
        self.passo_seq = 0
        self.passo_jogador = 0
        self.recorde = 0

        self.estado = "INICIO"  # INICIO, MOSTRANDO, JOGADOR, ACERTO, DERROTA, VITORIA
        self.timer_estado = 0.0
        self.cor_ativa = -1
        self.led_ativo = False
        self.ultimo_toque = 0.0

        # Zonas de toque nos 4 quadrantes
        self.quadrantes = [
            pygame.Rect(262, 110, 240, 180),  # Top-Left (Vermelho - BT1 / LED1)
            pygame.Rect(522, 110, 240, 180),  # Top-Right (Verde - BT2 / LED2)
            pygame.Rect(262, 310, 240, 180),  # Bottom-Left (Azul - BT3 / LED3)
            pygame.Rect(522, 310, 240, 180)   # Bottom-Right (Amarelo - BT4 / LED4)
        ]

    def get_id(self) -> str:
        return "memory_master"

    def get_nome(self) -> str:
        return "Memory Master"

    def get_descricao(self) -> str:
        return "Observe a sequência nos 4 LEDs físicos e repita pelos botões ou pelo touch."

    def iniciar(self) -> None:
        self.retorno_menu = False
        self.sequencia = [random.randint(0, 3)]
        self.rodada = 1
        self.passo_seq = 0
        self.passo_jogador = 0
        self.estado = "MOSTRANDO"
        self.timer_estado = time.time() + 0.8
        self.cor_ativa = -1
        self.led_ativo = False
        self.ultimo_toque = 0.0
        self.hw.apagar_leds()

    def processar_eventos(self, eventos_pygame: list[pygame.event.Event], estado_botoes: dict[str, bool]) -> None:
        agora = time.time()
        for evento in eventos_pygame:
            if self.header.processar_evento(evento):
                self.retorno_menu = True

            # Clique ou toque nos quadrantes coloridos (com debounce de 200ms contra eventos duplicados)
            if self.estado == "JOGADOR" and evento.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                if agora - self.ultimo_toque >= 0.20:
                    pos = evento.pos if hasattr(evento, "pos") else (int(evento.x * 1024), int(evento.y * 600))
                    for i, rect in enumerate(self.quadrantes):
                        if rect.collidepoint(pos):
                            self.ultimo_toque = agora
                            self._registrar_jogada(i)
                            break

        # Processamento de botões físicos da GPIO (BT1=0, BT2=1, BT3=2, BT4=3)
        if self.estado == "JOGADOR":
            if estado_botoes.get("BT1"): self._registrar_jogada(0)
            elif estado_botoes.get("BT2"): self._registrar_jogada(1)
            elif estado_botoes.get("BT3"): self._registrar_jogada(2)
            elif estado_botoes.get("BT4"): self._registrar_jogada(3)

    def _registrar_jogada(self, cor: int):
        self.cor_ativa = cor
        self.hw.set_led(cor, True)
        self.audio.tocar(f"genius_{cor}")
        self.timer_estado = time.time() + 0.25

        if cor == self.sequencia[self.passo_jogador]:
            self.passo_jogador += 1
            if self.passo_jogador >= self.rodada:
                if self.rodada >= 32:
                    self.estado = "VITORIA"
                    self.audio.tocar("vitoria")
                    self.timer_estado = time.time() + 3.0
                else:
                    self.rodada += 1
                    if self.rodada - 1 > self.recorde:
                        self.recorde = self.rodada - 1
                    self.sequencia.append(random.randint(0, 3))
                    self.estado = "ACERTO"
                    self.timer_estado = time.time() + 0.6
        else:
            self.estado = "DERROTA"
            self.audio.tocar("erro")
            self.hw.acender_leds()
            self.timer_estado = time.time() + 2.5

    def atualizar(self, dt: float) -> None:
        agora = time.time()

        if self.estado == "MOSTRANDO":
            intervalo = max(0.2, 0.6 - (self.rodada * 0.02))
            pausa = max(0.08, 0.25 - (self.rodada * 0.01))

            if not self.led_ativo:
                if agora >= self.timer_estado:
                    cor = self.sequencia[self.passo_seq]
                    # Pisca EXCLUSIVAMENTE o LED físico correspondente (A tela permanece sem acender)
                    self.cor_ativa = -1
                    self.hw.set_led(cor, True)
                    self.audio.tocar(f"genius_{cor}")
                    self.led_ativo = True
                    self.timer_estado = agora + intervalo
            else:
                if agora >= self.timer_estado:
                    self.hw.apagar_leds()
                    self.cor_ativa = -1
                    self.led_ativo = False
                    self.timer_estado = agora + pausa
                    self.passo_seq += 1

                    if self.passo_seq >= self.rodada:
                        self.estado = "JOGADOR"
                        self.passo_jogador = 0
                        self.timer_estado = agora + 6.0  # 6 segundos para responder

        elif self.estado == "JOGADOR":
            # Apaga o destaque visual do toque após pequeno delay de feedback
            if self.cor_ativa != -1 and agora >= self.timer_estado:
                self.hw.apagar_leds()
                self.cor_ativa = -1

            # Timeout de resposta
            if agora >= self.timer_estado and self.cor_ativa == -1:
                self.estado = "DERROTA"
                self.audio.tocar("erro")
                self.timer_estado = agora + 2.5

        elif self.estado == "ACERTO":
            if agora >= self.timer_estado:
                self.passo_seq = 0
                self.led_ativo = False
                self.cor_ativa = -1
                self.estado = "MOSTRANDO"
                self.timer_estado = agora + 0.4

        elif self.estado in ("DERROTA", "VITORIA"):
            if agora >= self.timer_estado:
                self.iniciar()

    def renderizar(self, superficie: pygame.Surface) -> None:
        superficie.fill(COLOR_BG)
        fonte_tit = pygame.font.SysFont("arial", 22, bold=True)
        fonte_med = pygame.font.SysFont("arial", 18, bold=True)
        fonte_peq = pygame.font.SysFont("arial", 15)

        self.header.renderizar(superficie, fonte_tit, fonte_peq)

        # Painel de Status Dinâmico (A tela orienta e diz se acertou ou errou)
        if self.estado == "MOSTRANDO":
            txt_status = "👀 OBSERVE A SEQUÊNCIA NOS 4 LEDS FÍSICOS!"
            cor_status = COLOR_YELLOW
        elif self.estado == "JOGADOR":
            txt_status = "🎮 SUA VEZ: REPITA A SEQUÊNCIA (BT1..BT4 OU TOQUE)"
            cor_status = COLOR_CYAN
        elif self.estado == "ACERTO":
            txt_status = "✓ ACERTOU! PREPARE-SE PARA A PRÓXIMA..."
            cor_status = (40, 240, 130)
        elif self.estado == "DERROTA":
            txt_status = "✗ SEQUÊNCIA INCORRETA! FIM DE JOGO"
            cor_status = (255, 60, 90)
        else:
            txt_status = "★ PARABÉNS! VOCÊ VENCEU O DESAFIO GENIUS!"
            cor_status = (255, 215, 0)

        surf_status = fonte_med.render(txt_status, True, cor_status)
        superficie.blit(surf_status, surf_status.get_rect(center=(512, 85)))

        # 4 Quadrantes Coloridos (Interface de Controle Tátil)
        for i, rect in enumerate(self.quadrantes):
            # A cor só brilha em tela se for durante a jogada ativa do jogador
            ativo = (self.estado == "JOGADOR" and self.cor_ativa == i)
            cor = self.CORES_BRILHO[i] if ativo else self.CORES_BASE[i]

            pygame.draw.rect(superficie, cor, rect, border_radius=14)
            borda = (255, 255, 255) if ativo else (30, 30, 40)
            pygame.draw.rect(superficie, borda, rect, width=3 if ativo else 1, border_radius=14)

            surf_rotulo = fonte_med.render(self.NOMES_CORES[i], True, (255, 255, 255) if ativo else (20, 20, 20))
            superficie.blit(surf_rotulo, surf_rotulo.get_rect(center=rect.center))

        # Placar Inferior
        surf_placar = fonte_med.render(f"RODADA ATUAL: {self.rodada}   |   RECORDE: {self.recorde}", True, COLOR_TEXT)
        superficie.blit(surf_placar, surf_placar.get_rect(center=(512, 520)))

    def encerrar(self) -> None:
        self.hw.apagar_leds()
        self.audio.parar_todos()

    def solicitou_retorno(self) -> bool:
        return self.retorno_menu
