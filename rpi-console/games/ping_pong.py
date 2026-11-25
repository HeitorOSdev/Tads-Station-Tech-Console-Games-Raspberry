"""
Jogo 7 (Adicional): Ping Pong Clássico (Duelo 2 Jogadores).
Migrado e aprimorado a partir do repositório 'pong/pingpong/pong.py':
- Resolução nativa 1024x600 com estética Retro Neon Arcade
- Mapeamento idêntico de pinos físicos da Raspberry Pi:
  * Jogador 1 (Esquerda): BT1 (Pino 11 / GPIO 17 - Cima) e BT2 (Pino 13 / GPIO 27 - Baixo)
  * Jogador 2 (Direita):  BT3 (Pino 15 / GPIO 22 - Cima) e BT4 (Pino 16 / GPIO 23 - Baixo)
- Suporte simultâneo a botões táteis na tela Touch e controle por teclado
- Física real de colisão com aceleração progressiva da bola
- Disputa até 5 pontos com efeitos sonoros sintetizados
"""

import random
import time
import pygame
from core.game_interface import Jogo
from core.hardware import HardwareManager
from core.audio_manager import AudioManager
from ui.components import HeaderBar, TouchButton, COLOR_BG, COLOR_PANEL, COLOR_BORDER, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_CYAN


class JogoPingPong(Jogo):
    PONTOS_VITORIA = 5
    VELOCIDADE_RAQUETE = 480.0  # pixels por segundo
    VELOCIDADE_BOLA_INICIAL = 420.0
    ACELERACAO_BOLA = 25.0

    def __init__(self, hw: HardwareManager, audio: AudioManager):
        self.hw = hw
        self.audio = audio
        self.header = HeaderBar("PING PONG — DUELO 2 JOGADORES")
        self.retorno_menu = False

        # Dimensões da quadra
        self.topo_campo = 70
        self.fundo_campo = 545
        self.altura_campo = self.fundo_campo - self.topo_campo

        # Raquetes
        self.largura_raquete = 16
        self.altura_raquete = 110
        self.p1_x = 35
        self.p1_y = (self.topo_campo + self.fundo_campo) // 2 - self.altura_raquete // 2
        self.p2_x = 1024 - 35 - self.largura_raquete
        self.p2_y = self.p1_y

        # Bola
        self.raio_bola = 9
        self.bola_x = 512.0
        self.bola_y = 300.0
        self.bola_vx = 0.0
        self.bola_vy = 0.0
        self.velocidade_atual = self.VELOCIDADE_BOLA_INICIAL

        # Placar e Estados
        self.placar_p1 = 0
        self.placar_p2 = 0
        self.estado = "PRONTO"  # PRONTO, JOGANDO, GOL, VITORIA
        self.vencedor = None
        self.timer_estado = 0.0

        # Botões de Toque na Tela para apoio aos jogadores
        self.btn_p1_up = TouchButton(10, 100, 70, 180, "▲", COLOR_CYAN)
        self.btn_p1_down = TouchButton(10, 320, 70, 180, "▼", COLOR_CYAN)
        self.btn_p2_up = TouchButton(944, 100, 70, 180, "▲", COLOR_RED)
        self.btn_p2_down = TouchButton(944, 320, 70, 180, "▼", COLOR_RED)

    def get_id(self) -> str:
        return "ping_pong"

    def get_nome(self) -> str:
        return "Ping Pong Arcade"

    def get_descricao(self) -> str:
        return "Clássico Pong para 2 jogadores. P1 usa BT1/BT2 e P2 usa BT3/BT4. Vence quem fizer 5 pontos!"

    def iniciar(self) -> None:
        self.retorno_menu = False
        self.placar_p1 = 0
        self.placar_p2 = 0
        self.vencedor = None
        self.p1_y = (self.topo_campo + self.fundo_campo) // 2 - self.altura_raquete // 2
        self.p2_y = self.p1_y
        self._resetar_bola(direcao_p1=random.choice([True, False]))
        self.estado = "PRONTO"
        self.timer_estado = time.time() + 1.2
        self.hw.apagar_leds()

    def _resetar_bola(self, direcao_p1: bool):
        self.bola_x = 512.0
        self.bola_y = float((self.topo_campo + self.fundo_campo) // 2)
        self.velocidade_atual = self.VELOCIDADE_BOLA_INICIAL

        sentido_x = -1.0 if direcao_p1 else 1.0
        angulo_y = random.uniform(-0.6, 0.6)
        self.bola_vx = sentido_x * self.velocidade_atual
        self.bola_vy = angulo_y * self.velocidade_atual

    def processar_eventos(self, eventos_pygame: list[pygame.event.Event], estado_botoes: dict[str, bool]) -> None:
        for evento in eventos_pygame:
            if self.header.processar_evento(evento):
                self.retorno_menu = True

            # Toques rápidos nas setas da tela
            self.btn_p1_up.processar_evento(evento)
            self.btn_p1_down.processar_evento(evento)
            self.btn_p2_up.processar_evento(evento)
            self.btn_p2_down.processar_evento(evento)

    def atualizar(self, dt: float) -> None:
        agora = time.time()

        if self.estado == "PRONTO":
            if agora >= self.timer_estado:
                self.estado = "JOGANDO"
                self.audio.tocar("largada")

        elif self.estado == "GOL":
            if agora >= self.timer_estado:
                if self.placar_p1 >= self.PONTOS_VITORIA or self.placar_p2 >= self.PONTOS_VITORIA:
                    self.estado = "VITORIA"
                    self.vencedor = 1 if self.placar_p1 >= self.PONTOS_VITORIA else 2
                    self.hw.set_led(0 if self.vencedor == 1 else 1, True)
                    self.audio.tocar("vitoria")
                    self.timer_estado = agora + 4.5
                else:
                    self._resetar_bola(direcao_p1=(self.placar_p2 > self.placar_p1))
                    self.estado = "JOGANDO"

        elif self.estado == "VITORIA":
            if agora >= self.timer_estado:
                self.iniciar()

        elif self.estado == "JOGANDO":
            # -------------------------------------------------------------
            # Movimentação das Raquetes (Física + Teclado + Touch)
            # -------------------------------------------------------------
            # P1: BT1 (Sobe) e BT2 (Desce)
            p1_sobe = self.hw.esta_pressionado("BT1") or self.btn_p1_up.pressionado or pygame.key.get_pressed()[pygame.K_w]
            p1_desce = self.hw.esta_pressionado("BT2") or self.btn_p1_down.pressionado or pygame.key.get_pressed()[pygame.K_s]

            if p1_sobe and self.p1_y > self.topo_campo:
                self.p1_y -= self.VELOCIDADE_RAQUETE * dt
            if p1_desce and self.p1_y + self.altura_raquete < self.fundo_campo:
                self.p1_y += self.VELOCIDADE_RAQUETE * dt

            # P2: BT3 (Sobe) e BT4 (Desce)
            p2_sobe = self.hw.esta_pressionado("BT3") or self.btn_p2_up.pressionado or pygame.key.get_pressed()[pygame.K_UP]
            p2_desce = self.hw.esta_pressionado("BT4") or self.btn_p2_down.pressionado or pygame.key.get_pressed()[pygame.K_DOWN]

            if p2_sobe and self.p2_y > self.topo_campo:
                self.p2_y -= self.VELOCIDADE_RAQUETE * dt
            if p2_desce and self.p2_y + self.altura_raquete < self.fundo_campo:
                self.p2_y += self.VELOCIDADE_RAQUETE * dt

            # Trava as raquetes nas bordas da quadra
            self.p1_y = max(self.topo_campo, min(self.fundo_campo - self.altura_raquete, self.p1_y))
            self.p2_y = max(self.topo_campo, min(self.fundo_campo - self.altura_raquete, self.p2_y))

            # -------------------------------------------------------------
            # Movimentação e Colisões da Bola
            # -------------------------------------------------------------
            self.bola_x += self.bola_vx * dt
            self.bola_y += self.bola_vy * dt

            # Colisão com o teto e o chão da quadra
            if self.bola_y - self.raio_bola <= self.topo_campo:
                self.bola_y = self.topo_campo + self.raio_bola
                self.bola_vy = abs(self.bola_vy)
                self.audio.tocar("menu_move")
            elif self.bola_y + self.raio_bola >= self.fundo_campo:
                self.bola_y = self.fundo_campo - self.raio_bola
                self.bola_vy = -abs(self.bola_vy)
                self.audio.tocar("menu_move")

            # Colisão com a Raquete 1 (Esquerda)
            rect_p1 = pygame.Rect(self.p1_x, int(self.p1_y), self.largura_raquete, self.altura_raquete)
            if rect_p1.collidepoint(int(self.bola_x - self.raio_bola), int(self.bola_y)) and self.bola_vx < 0:
                self.bola_x = self.p1_x + self.largura_raquete + self.raio_bola
                self.velocidade_atual += self.ACELERACAO_BOLA

                # Calcula o desvio angular baseado no ponto de impacto na raquete
                delta_y = (self.bola_y - (self.p1_y + self.altura_raquete / 2)) / (self.altura_raquete / 2)
                self.bola_vx = abs(self.velocidade_atual)
                self.bola_vy = delta_y * self.velocidade_atual * 0.85
                self.audio.tocar("acerto")
                self.hw.set_led(0, True)

            # Colisão com a Raquete 2 (Direita)
            rect_p2 = pygame.Rect(self.p2_x, int(self.p2_y), self.largura_raquete, self.altura_raquete)
            if rect_p2.collidepoint(int(self.bola_x + self.raio_bola), int(self.bola_y)) and self.bola_vx > 0:
                self.bola_x = self.p2_x - self.raio_bola
                self.velocidade_atual += self.ACELERACAO_BOLA

                delta_y = (self.bola_y - (self.p2_y + self.altura_raquete / 2)) / (self.altura_raquete / 2)
                self.bola_vx = -abs(self.velocidade_atual)
                self.bola_vy = delta_y * self.velocidade_atual * 0.85
                self.audio.tocar("acerto")
                self.hw.set_led(1, True)

            # -------------------------------------------------------------
            # Pontuação (Gol)
            # -------------------------------------------------------------
            if self.bola_x < 0:
                # Ponto para P2
                self.placar_p2 += 1
                self.audio.tocar("tiro")
                self.hw.set_led(1, True)
                self.estado = "GOL"
                self.timer_estado = agora + 1.2
            elif self.bola_x > 1024:
                # Ponto para P1
                self.placar_p1 += 1
                self.audio.tocar("tiro")
                self.hw.set_led(0, True)
                self.estado = "GOL"
                self.timer_estado = agora + 1.2

    def renderizar(self, superficie: pygame.Surface) -> None:
        superficie.fill(COLOR_BG)
        fonte_tit = pygame.font.SysFont("arial", 22, bold=True)
        fonte_med = pygame.font.SysFont("arial", 18, bold=True)
        fonte_peq = pygame.font.SysFont("arial", 15)
        fonte_placar = pygame.font.SysFont("arial", 56, bold=True)
        fonte_gra = pygame.font.SysFont("arial", 46, bold=True)

        self.header.renderizar(superficie, fonte_tit, fonte_peq)

        # Campo da Quadra (Bordas Superior e Inferior)
        pygame.draw.line(superficie, COLOR_BORDER, (0, self.topo_campo), (1024, self.topo_campo), 2)
        pygame.draw.line(superficie, COLOR_BORDER, (0, self.fundo_campo), (1024, self.fundo_campo), 2)

        # Linha Central Tracejada
        for y in range(self.topo_campo + 10, self.fundo_campo - 10, 24):
            pygame.draw.line(superficie, (35, 45, 75), (512, y), (512, y + 14), 3)

        # Placar Central
        surf_p1 = fonte_placar.render(str(self.placar_p1), True, COLOR_CYAN)
        surf_p2 = fonte_placar.render(str(self.placar_p2), True, COLOR_RED)
        superficie.blit(surf_p1, (430, 90))
        superficie.blit(surf_p2, (560, 90))

        # Raquetes
        rect_r1 = pygame.Rect(self.p1_x, int(self.p1_y), self.largura_raquete, self.altura_raquete)
        rect_r2 = pygame.Rect(self.p2_x, int(self.p2_y), self.largura_raquete, self.altura_raquete)
        pygame.draw.rect(superficie, COLOR_CYAN, rect_r1, border_radius=6)
        pygame.draw.rect(superficie, COLOR_RED, rect_r2, border_radius=6)

        # Bola
        pygame.draw.circle(superficie, COLOR_YELLOW, (int(self.bola_x), int(self.bola_y)), self.raio_bola)
        pygame.draw.circle(superficie, (255, 255, 255), (int(self.bola_x), int(self.bola_y)), self.raio_bola - 2)

        # Setas Táteis Laterais para suporte a Touchscreen
        self.btn_p1_up.renderizar(superficie, fonte_tit)
        self.btn_p1_down.renderizar(superficie, fonte_tit)
        self.btn_p2_up.renderizar(superficie, fonte_tit)
        self.btn_p2_down.renderizar(superficie, fonte_tit)

        # Rótulos dos Jogadores
        surf_lbl_p1 = fonte_peq.render("P1: BT1(▲) BT2(▼)", True, COLOR_CYAN)
        superficie.blit(surf_lbl_p1, (90, 520))

        surf_lbl_p2 = fonte_peq.render("P2: BT3(▲) BT4(▼)", True, COLOR_RED)
        superficie.blit(surf_lbl_p2, (780, 520))

        # Mensagens Centrais de Estado
        if self.estado == "PRONTO":
            surf_msg = fonte_gra.render("PREPAREM-SE!", True, COLOR_YELLOW)
            superficie.blit(surf_msg, surf_msg.get_rect(center=(512, 300)))
        elif self.estado == "GOL":
            surf_gol = fonte_gra.render("PONTO!", True, COLOR_YELLOW)
            superficie.blit(surf_gol, surf_gol.get_rect(center=(512, 300)))
        elif self.estado == "VITORIA":
            msg_vit = f"JOGADOR {self.vencedor} VENCEU O DUELO!"
            cor_vit = COLOR_CYAN if self.vencedor == 1 else COLOR_RED
            surf_vit = fonte_gra.render(msg_vit, True, cor_vit)
            superficie.blit(surf_vit, surf_vit.get_rect(center=(512, 300)))

    def encerrar(self) -> None:
        self.hw.apagar_leds()
        self.audio.parar_todos()

    def solicitou_retorno(self) -> bool:
        return self.retorno_menu
