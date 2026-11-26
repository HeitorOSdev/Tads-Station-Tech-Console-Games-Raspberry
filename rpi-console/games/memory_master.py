"""
Jogo 1: Memory Master (Desafio da Memória - Genius 4 Cores).
Apresenta 4 setores coloridos na tela 1024x600 sincronizados com os 4 LEDs físicos:
- Cor 0 (Vermelho): LED1 (Pino 11 / BCM 17) / Nota Dó
- Cor 1 (Verde):    LED2 (Pino 13 / BCM 27) / Nota Mi
- Cor 2 (Azul):     LED3 (Pino 15 / BCM 22) / Nota Sol
- Cor 3 (Amarelo):  LED4 (Pino 16 / BCM 23) / Nota Dó Agudo

Recursos:
- Opção "COM LEDS" (padrão com LEDs físicos) e "SEM LEDS" (cores piscam visualmente na tela)
- Os LEDs físicos continuam acionados normalmente em ambos os modos
- Seletor de 2 Botões físicos no modo jogador: BT1 = Mover seletor, BT2 = Escolher
- Suporte simultâneo a toque direto nos quadrantes da tela touch
"""

import random
import time
import pygame
from core.game_interface import Jogo
from core.hardware import HardwareManager
from core.audio_manager import AudioManager
from ui.components import HeaderBar, TouchButton, COLOR_BG, COLOR_PANEL, COLOR_BORDER, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_YELLOW, COLOR_CYAN, COLOR_GREEN, COLOR_RED


class JogoMemoryMaster(Jogo):
    CORES_BASE = [
        (220, 40, 60),    # 0: Vermelho
        (40, 200, 100),   # 1: Verde
        (30, 130, 240),   # 2: Azul
        (240, 200, 30)    # 3: Amarelo
    ]
    CORES_BRILHO = [
        (255, 130, 150),
        (130, 255, 170),
        (130, 200, 255),
        (255, 245, 140)
    ]
    NOMES_CORES = ["VERMELHO", "VERDE", "AZUL", "AMARELO"]

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

        # Modo Sem LEDs (permite jogar olhando apenas para a tela)
        self.modo_sem_leds = False
        self.btn_modo = TouchButton(750, 70, 230, 38, "MODO: COM LEDS", (20, 50, 85))

        # Seletor com 2 botões físicos: BT1 move, BT2 escolhe
        self.seletor_cor = 0
        self.modo_touch = True

        # Zonas de toque nos 4 quadrantes coloridos
        self.quadrantes = [
            pygame.Rect(262, 120, 240, 175),  # Top-Left (0: Vermelho)
            pygame.Rect(522, 120, 240, 175),  # Top-Right (1: Verde)
            pygame.Rect(262, 315, 240, 175),  # Bottom-Left (2: Azul)
            pygame.Rect(522, 315, 240, 175)   # Bottom-Right (3: Amarelo)
        ]

    def get_id(self) -> str:
        return "memory_master"

    def get_nome(self) -> str:
        return "Memory Master"

    def get_descricao(self) -> str:
        return "Desafio Genius: memorize a sequência nos LEDs ou na tela e use o seletor de 2 botões ou toque!"

    def iniciar(self) -> None:
        self.retorno_menu = False
        self.sequencia = [random.randint(0, 3)]
        self.rodada = 1
        self.passo_seq = 0
        self.passo_jogador = 0
        self.seletor_cor = 0
        self.estado = "MOSTRANDO"
        self.timer_estado = time.time() + 0.8
        self.cor_ativa = -1
        self.led_ativo = False
        self.ultimo_toque = 0.0
        self.hw.apagar_leds()

    def processar_eventos(self, eventos_pygame: list[pygame.event.Event], estado_botoes: dict[str, bool]) -> None:
        if "MODO_TOUCH" in estado_botoes:
            self.modo_touch = estado_botoes["MODO_TOUCH"]

        agora = time.time()
        for evento in eventos_pygame:
            if self.header.processar_evento(evento):
                self.retorno_menu = True

            # Botão de alternância de modo (COM LEDS vs SEM LEDS)
            if self.btn_modo.processar_evento(evento):
                self.modo_sem_leds = not self.modo_sem_leds
                txt = "MODO: SEM LEDS (TELA)" if self.modo_sem_leds else "MODO: COM LEDS"
                cor = (90, 40, 100) if self.modo_sem_leds else (20, 50, 85)
                self.btn_modo.texto = txt
                self.btn_modo.cor_normal = cor
                self.audio.tocar("menu_move")

            # Toque direto nos 4 quadrantes coloridos
            if self.estado == "JOGADOR" and evento.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                self.modo_touch = True
                if agora - self.ultimo_toque >= 0.18:
                    pos = evento.pos if hasattr(evento, "pos") else (int(evento.x * 1024), int(evento.y * 600))
                    for i, rect in enumerate(self.quadrantes):
                        if rect.collidepoint(pos):
                            self.ultimo_toque = agora
                            self.seletor_cor = i
                            self._registrar_jogada(i)
                            break

        # Controles Físicos com 2 Botões no modo Jogador:
        # BT1: Move o seletor entre as 4 cores
        # BT2: Confirma / Escolhe a cor selecionada
        if self.estado == "JOGADOR":
            if estado_botoes.get("BT1"):
                self.modo_touch = False
                self.seletor_cor = (self.seletor_cor + 1) % 4
                self.audio.tocar("menu_move")

            if estado_botoes.get("BT2") or estado_botoes.get("BT4") or estado_botoes.get("BT5"):
                self.modo_touch = False
                self._registrar_jogada(self.seletor_cor)

    def _registrar_jogada(self, cor: int):
        self.cor_ativa = cor
        self.hw.set_led(cor, True)
        self.audio.tocar(f"genius_{cor}")
        self.timer_estado = time.time() + 0.30

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
                    # Os LEDs físicos SEMPRE acendem em ambos os modos
                    self.hw.set_led(cor, True)
                    self.audio.tocar(f"genius_{cor}")
                    self.led_ativo = True

                    # No modo "SEM LEDS", a cor também brilha na tela
                    if self.modo_sem_leds:
                        self.cor_ativa = cor
                    else:
                        self.cor_ativa = -1

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
            # Apaga o destaque visual do toque após o feedback
            if self.cor_ativa != -1 and agora >= self.timer_estado:
                self.hw.apagar_leds()
                self.cor_ativa = -1

            # Timeout de resposta
            if agora >= self.timer_estado and self.cor_ativa == -1:
                self.estado = "DERROTA"
                self.audio.tocar("erro")
                self.hw.acender_leds()
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

        # Botão Touch de Alternância de Modo (Com LEDs vs Sem LEDs)
        self.btn_modo.renderizar(superficie, fonte_peq)

        # Painel de Status Central
        if self.estado == "MOSTRANDO":
            if self.modo_sem_leds:
                txt_status = "👀 OBSERVE A SEQUÊNCIA NA TELA!"
            else:
                txt_status = "👀 OBSERVE A SEQUÊNCIA NOS 4 LEDS FÍSICOS!"
            cor_status = COLOR_YELLOW
        elif self.estado == "JOGADOR":
            if self.modo_touch:
                txt_status = "🎮 SUA VEZ: TOQUE NA COR OU USE [BT1/BT2]"
            else:
                txt_status = "🎮 SUA VEZ: [BT1] MOVER SELETOR | [BT2] ESCOLHER"
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
        superficie.blit(surf_status, surf_status.get_rect(center=(430, 88)))

        # 4 Quadrantes Coloridos
        for i, rect in enumerate(self.quadrantes):
            # Célula ativa piscando (por toque ou durante demonstração visual em modo sem leds)
            ativo = (self.cor_ativa == i)
            selecionado = (self.estado == "JOGADOR" and not self.modo_touch and self.seletor_cor == i)

            cor = self.CORES_BRILHO[i] if ativo else self.CORES_BASE[i]
            pygame.draw.rect(superficie, cor, rect, border_radius=14)

            # Moldura do seletor físico (glowing ouro) ou borda normal
            if selecionado:
                pygame.draw.rect(superficie, (255, 230, 40), rect, width=5, border_radius=14)
            elif ativo:
                pygame.draw.rect(superficie, (255, 255, 255), rect, width=4, border_radius=14)
            else:
                pygame.draw.rect(superficie, (25, 25, 35), rect, width=1, border_radius=14)

            # Texto do quadrante
            nome_cor = self.NOMES_CORES[i]
            surf_rotulo = fonte_med.render(nome_cor, True, (255, 255, 255) if (ativo or selecionado) else (20, 20, 20))
            superficie.blit(surf_rotulo, surf_rotulo.get_rect(center=(rect.centerx, rect.centery - 12)))

            # Indicador de seletor ativo na cor
            if selecionado:
                surf_btn = fonte_peq.render("[BT2] ESCOLHER", True, (255, 240, 60))
                superficie.blit(surf_btn, surf_btn.get_rect(center=(rect.centerx, rect.centery + 16)))

        # Rodapé e Dica
        surf_placar = fonte_med.render(f"RODADA: {self.rodada}   |   RECORDE: {self.recorde}", True, COLOR_TEXT)
        superficie.blit(surf_placar, surf_placar.get_rect(center=(512, 515)))

        if not self.modo_touch:
            msg_dica = "[BT1] Mover Seletor     |     [BT2] Confirmar Cor     |     Segure [BT2] p/ Menu"
        else:
            msg_dica = "Toque diretamente na cor desejada ou use [BT1] Mover e [BT2] Escolher"
        surf_dica = fonte_peq.render(msg_dica, True, COLOR_TEXT_DIM)
        superficie.blit(surf_dica, surf_dica.get_rect(center=(512, 545)))

    def encerrar(self) -> None:
        self.hw.apagar_leds()
        self.audio.parar_todos()

    def solicitou_retorno(self) -> bool:
        return self.retorno_menu
