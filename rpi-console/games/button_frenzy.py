"""
Jogo 7: Button Frenzy (Desafio de Velocidade / Tapping Frenético).
Portado e aprimorado para Raspberry Pi 3 B+ (1024x600) em conformidade com Clean Code, POO e SOLID:
- Contagem regressiva visual e sonora de 3 segundos
- Janela de 10.00 segundos para o jogador pressionar o Botão Físico BT1 ou tocar na tela o máximo de vezes
- Cálculo em tempo real de cliques totais e CPS (Cliques Por Segundo)
- Classificação por faixas de velocidade (Iniciante, Intermediário, Rápido, Muito Rápido, Especialista e Lendário)
- Sinalização nos LEDs físicos: LED Verde (D6) ativo durante a partida e LED Vermelho (D5) em fim de tempo
"""

import time
import pygame
from core.game_interface import Jogo
from core.hardware import HardwareManager
from core.audio_manager import AudioManager
from ui.components import HeaderBar, TouchButton, COLOR_BG, COLOR_PANEL, COLOR_BORDER, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_CYAN


class JogoButtonFrenzy(Jogo):
    DURACAO_PARTIDA = 10.00  # 10 segundos exatos

    CLASSIFICACOES = [
        (20, "INICIANTE", (140, 150, 180)),
        (40, "INTERMEDIÁRIO", (50, 180, 220)),
        (60, "RÁPIDO!", (40, 220, 120)),
        (80, "MUITO RÁPIDO!", (255, 200, 30)),
        (100, "ESPECIALISTA!", (255, 120, 40)),
        (9999, "LENDÁRIO!", (255, 50, 90))
    ]

    def __init__(self, hw: HardwareManager, audio: AudioManager):
        self.hw = hw
        self.audio = audio
        self.header = HeaderBar("BUTTON FRENZY — DESAFIO DE VELOCIDADE")
        self.retorno_menu = False

        self.estado = "AGUARDANDO"  # AGUARDANDO, CONTAGEM, FRENZY, RESULTADO
        self.cliques = 0
        self.cps = 0.0
        self.tempo_restante = 10.00
        self.t_inicio = 0.0
        self.recorde_cliques = 0
        self.classificacao = ""
        self.cor_classificacao = COLOR_TEXT
        self.timer_contagem = 0.0
        self.segundos_contagem = 3
        self.timer_resultado = 0.0

        # Botão gigante de clique na tela
        self.btn_frenzy = TouchButton(262, 140, 500, 250, "APERTE BT1 OU TOQUE AQUI\nPARA INICIAR", COLOR_CYAN)

    def get_id(self) -> str:
        return "button_frenzy"

    def get_nome(self) -> str:
        return "Button Frenzy"

    def get_descricao(self) -> str:
        return "Pressione o botão o maior número de vezes possível em 10 segundos! Teste seus cliques/segundo."

    def iniciar(self) -> None:
        self.retorno_menu = False
        self.estado = "AGUARDANDO"
        self.cliques = 0
        self.cps = 0.0
        self.tempo_restante = self.DURACAO_PARTIDA
        self.classificacao = ""
        self.btn_frenzy.texto = "APERTE BT1 OU TOQUE AQUI\nPARA INICIAR"
        self.btn_frenzy.cor_destaque = COLOR_CYAN
        self.hw.apagar_leds()

    def processar_eventos(self, eventos_pygame: list[pygame.event.Event], estado_botoes: dict[str, bool]) -> None:
        for evento in eventos_pygame:
            if self.header.processar_evento(evento):
                self.retorno_menu = True

            # Toques na tela
            if self.btn_frenzy.processar_evento(evento):
                self._tratar_clique()

        # Botão físico BT1 (Pino 11)
        if estado_botoes.get("BT1"):
            self._tratar_clique()

    def _tratar_clique(self):
        if self.estado == "AGUARDANDO":
            # Inicia a contagem regressiva de 3 segundos
            self.estado = "CONTAGEM"
            self.segundos_contagem = 3
            self.timer_contagem = time.time() + 1.0
            self.audio.tocar("menu_move")
            self.hw.set_led(0, True)

        elif self.estado == "FRENZY":
            # Registra clique válido
            self.cliques += 1
            self.audio.tocar("acerto")

    def atualizar(self, dt: float) -> None:
        agora = time.time()

        if self.estado == "CONTAGEM":
            if agora >= self.timer_contagem:
                self.segundos_contagem -= 1
                if self.segundos_contagem > 0:
                    self.timer_contagem = agora + 1.0
                    self.audio.tocar("menu_move")
                    self.hw.set_led(0, self.segundos_contagem % 2 == 1)
                else:
                    # Inicia a partida Frenzy de 10s
                    self.estado = "FRENZY"
                    self.cliques = 0
                    self.t_inicio = time.time()
                    self.hw.set_led(0, False)
                    self.hw.set_led(1, True)  # LED Verde ativo durante partida
                    self.audio.tocar("largada")
                    self.btn_frenzy.cor_destaque = COLOR_YELLOW

        elif self.estado == "FRENZY":
            decorrido = agora - self.t_inicio
            self.tempo_restante = max(0.0, self.DURACAO_PARTIDA - decorrido)
            if decorrido > 0:
                self.cps = self.cliques / decorrido

            self.btn_frenzy.texto = f"CLIQUES: {self.cliques}\n{self.tempo_restante:.2f} s"

            if decorrido >= self.DURACAO_PARTIDA:
                # Fim de partida
                self.estado = "RESULTADO"
                self.hw.set_led(1, False)
                self.hw.set_led(0, True)  # LED Vermelho sinaliza término
                self.cps = self.cliques / 10.0

                # Determina classificação
                for limite, nome, cor in self.CLASSIFICACOES:
                    if self.cliques <= limite:
                        self.classificacao = nome
                        self.cor_classificacao = cor
                        break

                if self.cliques > self.recorde_cliques:
                    self.recorde_cliques = self.cliques
                    self.audio.tocar("vitoria")
                else:
                    self.audio.tocar("acerto")

                self.btn_frenzy.texto = f"FIM DE TEMPO!\n{self.cliques} CLIQUES ({self.cps:.1f} CPS)"
                self.btn_frenzy.cor_destaque = self.cor_classificacao
                self.timer_resultado = agora + 5.0

        elif self.estado == "RESULTADO":
            if agora >= self.timer_resultado:
                self.iniciar()

    def renderizar(self, superficie: pygame.Surface) -> None:
        superficie.fill(COLOR_BG)
        fonte_tit = pygame.font.SysFont("arial", 22, bold=True)
        fonte_med = pygame.font.SysFont("arial", 18, bold=True)
        fonte_peq = pygame.font.SysFont("arial", 15)
        fonte_gra = pygame.font.SysFont("arial", 52, bold=True)

        self.header.renderizar(superficie, fonte_tit, fonte_peq)

        # Botão / Painel de Toque Central
        if self.estado == "CONTAGEM":
            surf_cnt = fonte_gra.render(str(self.segundos_contagem), True, COLOR_YELLOW)
            superficie.blit(surf_cnt, surf_cnt.get_rect(center=(512, 260)))
        else:
            self.btn_frenzy.renderizar(superficie, fonte_med)

        # Painel Inferior de Estatísticas
        painel_stats = pygame.Rect(162, 415, 700, 115)
        pygame.draw.rect(superficie, COLOR_PANEL, painel_stats, border_radius=14)
        pygame.draw.rect(superficie, COLOR_BORDER, painel_stats, width=2, border_radius=14)

        if self.estado == "RESULTADO":
            surf_class = fonte_med.render(f"CLASSIFICAÇÃO: {self.classificacao}  |  VELOCIDADE: {self.cps:.1f} CPS", True, self.cor_classificacao)
            superficie.blit(surf_class, surf_class.get_rect(center=(512, 450)))

            surf_rec = fonte_peq.render(f"RECORDE DA SESSÃO: {self.recorde_cliques} CLIQUES", True, COLOR_YELLOW)
            superficie.blit(surf_rec, surf_rec.get_rect(center=(512, 490)))
        elif self.estado == "FRENZY":
            surf_durante = fonte_med.render(f"TEMPO: {self.tempo_restante:.2f} s   |   VELOCIDADE ATUAL: {self.cps:.1f} CPS", True, COLOR_YELLOW)
            superficie.blit(surf_durante, surf_durante.get_rect(center=(512, 472)))
        else:
            surf_info = fonte_peq.render("Pressione o botão o mais rápido possível por 10 segundos. Mostre a agilidade dos seus dedos!", True, COLOR_TEXT_DIM)
            superficie.blit(surf_info, surf_info.get_rect(center=(512, 472)))

    def encerrar(self) -> None:
        self.hw.apagar_leds()
        self.audio.parar_todos()

    def solicitou_retorno(self) -> bool:
        return self.retorno_menu
