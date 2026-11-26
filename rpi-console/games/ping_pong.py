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
    VELOCIDADE_RAQUETE = 370.0  # Movimento contínuo suave (pixels por segundo)
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

        # Direções de movimento contínuo (+1.0 = Desce, -1.0 = Sobe)
        self.p1_dir = 1.0
        self.p2_dir = -1.0

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
        self.modo_touch = True

        # Botões de Toque Translúcidos no meio da tela
        self.rect_touch_p1 = pygame.Rect(90, 190, 190, 230)
        self.rect_touch_p2 = pygame.Rect(744, 190, 190, 230)

    def get_id(self) -> str:
        return "ping_pong"

    def get_nome(self) -> str:
        return "Ping Pong Arcade"

    def get_descricao(self) -> str:
        return "Pong arcade contínuo: as raquetes movem-se sozinhas. Aperte o botão para inverter a direção!"

    def iniciar(self) -> None:
        self.retorno_menu = False
        self.placar_p1 = 0
        self.placar_p2 = 0
        self.vencedor = None
        self.p1_y = (self.topo_campo + self.fundo_campo) // 2 - self.altura_raquete // 2
        self.p2_y = self.p1_y
        self.p1_dir = 1.0
        self.p2_dir = -1.0
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

    def _inverter_p1(self):
        """Inverte a direção contínua da raquete do Jogador 1."""
        self.p1_dir = -self.p1_dir
        self.audio.tocar("menu_move")

    def _inverter_p2(self):
        """Inverte a direção contínua da raquete do Jogador 2."""
        self.p2_dir = -self.p2_dir
        self.audio.tocar("menu_move")

    def processar_eventos(self, eventos_pygame: list[pygame.event.Event], estado_botoes: dict[str, bool]) -> None:
        if "MODO_TOUCH" in estado_botoes:
            self.modo_touch = estado_botoes["MODO_TOUCH"]

        for evento in eventos_pygame:
            if self.header.processar_evento(evento):
                self.retorno_menu = True

            # Toque nos botões translúcidos centrais ou na metade do campo
            if self.estado == "JOGANDO" and evento.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                self.modo_touch = True
                pos = evento.pos if hasattr(evento, "pos") else (int(evento.x * 1024), int(evento.y * 600))
                if pos[0] < 512:
                    self._inverter_p1()
                else:
                    self._inverter_p2()

            # Teclado para testes (W/S para P1; Setas/Enter para P2)
            elif self.estado == "JOGANDO" and evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d):
                    self.modo_touch = False
                    self._inverter_p1()
                elif evento.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN, pygame.K_SPACE):
                    self.modo_touch = False
                    self._inverter_p2()

        # Botões físicos: cada clique inverte a direção da respectiva raquete
        if self.estado == "JOGANDO":
            # P1 usa BT1 (ou BT2)
            if estado_botoes.get("BT1") or estado_botoes.get("BT2"):
                self.modo_touch = False
                self._inverter_p1()

            # P2 usa BT4 (ou BT3)
            if estado_botoes.get("BT4") or estado_botoes.get("BT3"):
                self.modo_touch = False
                self._inverter_p2()

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
            # Movimentação Contínua das Raquetes (Invertem nas bordas)
            # -------------------------------------------------------------
            self.p1_y += self.p1_dir * self.VELOCIDADE_RAQUETE * dt
            self.p2_y += self.p2_dir * self.VELOCIDADE_RAQUETE * dt

            # Rebate automático nas bordas superior e inferior
            if self.p1_y <= self.topo_campo:
                self.p1_y = self.topo_campo
                self.p1_dir = 1.0
            elif self.p1_y + self.altura_raquete >= self.fundo_campo:
                self.p1_y = self.fundo_campo - self.altura_raquete
                self.p1_dir = -1.0

            if self.p2_y <= self.topo_campo:
                self.p2_y = self.topo_campo
                self.p2_dir = 1.0
            elif self.p2_y + self.altura_raquete >= self.fundo_campo:
                self.p2_y = self.fundo_campo - self.altura_raquete
                self.p2_dir = -1.0

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

        # Botões Touch Translúcidos no meio da tela (Visíveis no modo touch)
        if self.modo_touch:
            surf_alpha = pygame.Surface((1024, 600), pygame.SRCALPHA)
            # Botão translúcido P1 (meio esquerdo)
            pygame.draw.rect(surf_alpha, (0, 230, 255, 30), self.rect_touch_p1, border_radius=18)
            pygame.draw.rect(surf_alpha, (0, 230, 255, 120), self.rect_touch_p1, width=2, border_radius=18)
            # Botão translúcido P2 (meio direito)
            pygame.draw.rect(surf_alpha, (255, 60, 90, 30), self.rect_touch_p2, border_radius=18)
            pygame.draw.rect(surf_alpha, (255, 60, 90, 120), self.rect_touch_p2, width=2, border_radius=18)
            superficie.blit(surf_alpha, (0, 0))

            surf_t1 = fonte_med.render("INVERTER", True, COLOR_CYAN)
            surf_sub1 = fonte_peq.render("TOQUE AQUI", True, (160, 230, 255))
            superficie.blit(surf_t1, surf_t1.get_rect(center=(self.rect_touch_p1.centerx, self.rect_touch_p1.centery - 12)))
            superficie.blit(surf_sub1, surf_sub1.get_rect(center=(self.rect_touch_p1.centerx, self.rect_touch_p1.centery + 15)))

            surf_t2 = fonte_med.render("INVERTER", True, COLOR_RED)
            surf_sub2 = fonte_peq.render("TOQUE AQUI", True, (255, 180, 190))
            superficie.blit(surf_t2, surf_t2.get_rect(center=(self.rect_touch_p2.centerx, self.rect_touch_p2.centery - 12)))
            superficie.blit(surf_sub2, surf_sub2.get_rect(center=(self.rect_touch_p2.centerx, self.rect_touch_p2.centery + 15)))

        # Rótulos dos Jogadores
        txt_p1 = "P1: Toque ou BT1 (Inverter)" if self.modo_touch else "P1: [BT1] Inverter Direção"
        surf_lbl_p1 = fonte_peq.render(txt_p1, True, COLOR_CYAN)
        superficie.blit(surf_lbl_p1, (90, 520))

        txt_p2 = "P2: Toque ou BT4 (Inverter)" if self.modo_touch else "P2: [BT4] Inverter Direção"
        surf_lbl_p2 = fonte_peq.render(txt_p2, True, COLOR_RED)
        superficie.blit(surf_lbl_p2, (740, 520))

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
