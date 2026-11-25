"""
Jogo 5: Campo Minado (Minefield com 5 Posições e 2 Minas Ocultas).
Apresenta 5 cápsulas interativas na tela 1024x600 sincronizadas com BT1..BT5 e LEDs 1..5:
- O microcontrolador sorteia 2 minas e 3 caminhos seguros
- Acertos acendem o LED correspondente e tocam chime de sucesso
- Minas explodem visualmente e acionam som de explosão e piscar de todos os LEDs
"""

import random
import time
import pygame
from core.game_interface import Jogo
from core.hardware import HardwareManager
from core.audio_manager import AudioManager
from ui.components import HeaderBar, COLOR_BG, COLOR_PANEL, COLOR_BORDER, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_CYAN


class JogoCampoMinado(Jogo):
    def __init__(self, hw: HardwareManager, audio: AudioManager):
        self.hw = hw
        self.audio = audio
        self.header = HeaderBar("CAMPO MINADO — DESAFIO TÁTIL")
        self.retorno_menu = False

        self.minas = [False] * 5
        self.descobertos = [False] * 5
        self.acertos = 0
        self.estado = "JOGANDO"  # JOGANDO, VITORIA, DERROTA
        self.timer_reinicio = 0.0

        # 5 cartas na tela (distribuídas horizontalmente)
        self.rects_cartas = [
            pygame.Rect(50 + (i * 188), 160, 160, 260) for i in range(5)
        ]

    def get_id(self) -> str:
        return "minefield"

    def get_nome(self) -> str:
        return "Campo Minado"

    def get_descricao(self) -> str:
        return "Descubra os 3 caminhos seguros nos 5 botões sem detonar as 2 minas ocultas."

    def iniciar(self) -> None:
        self.retorno_menu = False
        self.minas = [False] * 5
        self.descobertos = [False] * 5
        self.acertos = 0
        self.estado = "JOGANDO"
        self.hw.apagar_leds()

        # Sorteia exatamente 2 minas
        posicoes_minas = random.sample(range(5), 2)
        for p in posicoes_minas:
            self.minas[p] = True

    def processar_eventos(self, eventos_pygame: list[pygame.event.Event], estado_botoes: dict[str, bool]) -> None:
        for evento in eventos_pygame:
            if self.header.processar_evento(evento):
                self.retorno_menu = True

            # Toque nas cartas
            if self.estado == "JOGANDO" and evento.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                pos = evento.pos if hasattr(evento, "pos") else (int(evento.x * 1024), int(evento.y * 600))
                for i, rect in enumerate(self.rects_cartas):
                    if rect.collidepoint(pos):
                        self._revelar_posicao(i)
                        break

        # Botões físicos
        if self.estado == "JOGANDO":
            for i in range(5):
                nome_btn = f"BT{i+1}"
                if estado_botoes.get(nome_btn):
                    self._revelar_posicao(i)
                    break

    def _revelar_posicao(self, indice: int):
        if self.descobertos[indice]:
            return

        self.descobertos[indice] = True
        agora = time.time()

        if self.minas[indice]:
            # Explodiu!
            self.estado = "DERROTA"
            self.audio.tocar("explosao")
            self.hw.acender_leds()
            self.timer_reinicio = agora + 4.0
        else:
            # Seguro!
            self.acertos += 1
            self.hw.set_led(indice, True)
            self.audio.tocar("acerto")

            if self.acertos >= 3:
                # Vitória total
                self.estado = "VITORIA"
                self.audio.tocar("vitoria")
                self.timer_reinicio = agora + 4.5

    def atualizar(self, dt: float) -> None:
        agora = time.time()
        if self.estado in ("VITORIA", "DERROTA") and agora >= self.timer_reinicio:
            self.iniciar()

    def renderizar(self, superficie: pygame.Surface) -> None:
        superficie.fill(COLOR_BG)
        fonte_tit = pygame.font.SysFont("arial", 22, bold=True)
        fonte_med = pygame.font.SysFont("arial", 18, bold=True)
        fonte_peq = pygame.font.SysFont("arial", 15)
        fonte_gra = pygame.font.SysFont("arial", 38, bold=True)

        self.header.renderizar(superficie, fonte_tit, fonte_peq)

        # Status
        txt_status = f"CAMINHOS SEGUROS: {self.acertos} / 3   |   2 MINAS OCULTAS" if self.estado == "JOGANDO" else \
                     "BOOOOM! VOCÊ DETONOU UMA MINA!" if self.estado == "DERROTA" else "PARABÉNS! CAMPO DESARMADO COM SUCESSO!"
        cor_status = COLOR_YELLOW if self.estado == "JOGANDO" else COLOR_RED if self.estado == "DERROTA" else COLOR_GREEN

        surf_status = fonte_med.render(txt_status, True, cor_status)
        superficie.blit(surf_status, surf_status.get_rect(center=(512, 110)))

        # 5 Cartas Interativas
        for i, rect in enumerate(self.rects_cartas):
            revelado = self.descobertos[i]

            if not revelado:
                cor_fundo = COLOR_PANEL
                cor_borda = COLOR_BORDER
                txt_centro = f"#{i+1}"
                txt_sub = f"BT{i+1}"
                cor_txt = COLOR_CYAN
            else:
                if self.minas[i]:
                    cor_fundo = (90, 20, 25)
                    cor_borda = COLOR_RED
                    txt_centro = "MINA!"
                    txt_sub = "DETONADA"
                    cor_txt = COLOR_RED
                else:
                    cor_fundo = (20, 75, 45)
                    cor_borda = COLOR_GREEN
                    txt_centro = "SEGURO"
                    txt_sub = "+1 ACERTO"
                    cor_txt = COLOR_GREEN

            pygame.draw.rect(superficie, cor_fundo, rect, border_radius=14)
            pygame.draw.rect(superficie, cor_borda, rect, width=2, border_radius=14)

            surf_c = fonte_gra.render(txt_centro, True, cor_txt)
            superficie.blit(surf_c, surf_c.get_rect(center=(rect.centerx, rect.centery - 20)))

            surf_s = fonte_peq.render(txt_sub, True, COLOR_TEXT_DIM)
            superficie.blit(surf_s, surf_s.get_rect(center=(rect.centerx, rect.centery + 35)))

        # Dica na base
        surf_dica = fonte_peq.render("Toque em uma carta ou pressione o botão físico correspondente (BT1 a BT5)", True, COLOR_TEXT_DIM)
        superficie.blit(surf_dica, surf_dica.get_rect(center=(512, 480)))

    def encerrar(self) -> None:
        self.hw.apagar_leds()
        self.audio.parar_todos()

    def solicitou_retorno(self) -> bool:
        return self.retorno_menu
