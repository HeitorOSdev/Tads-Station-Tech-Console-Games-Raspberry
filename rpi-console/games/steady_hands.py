"""
Jogo 4: Steady Hands (Teste de Precisão / Mão Firme na Pista de Arame).
Monitora o contato da argola no arame (GPIO 16 com proteção contra estática ESD):
- Botão de Início (BT3 ou Touch)
- Botão de Conclusão (BT4 ou Touch)
- 3 Vidas gerenciadas em tempo real com indicação nos LEDs 1, 2 e 3
- Cronômetro de precisão em centésimos de segundo
- Alerta de contato em tempo real (LED 5 e efeito sonoro)
"""

import time
import pygame
from core.game_interface import Jogo
from core.hardware import HardwareManager
from core.audio_manager import AudioManager
from ui.components import HeaderBar, TouchButton, COLOR_BG, COLOR_PANEL, COLOR_BORDER, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_CYAN


class JogoSteadyHands(Jogo):
    def __init__(self, hw: HardwareManager, audio: AudioManager):
        self.hw = hw
        self.audio = audio
        self.header = HeaderBar("STEADY HANDS — MÃO FIRME NO ARAME")
        self.retorno_menu = False

        self.vidas = 3
        self.estado = "ESPERA"  # ESPERA, PERCURSO, RESULTADO
        self.tempo_inicio = 0.0
        self.tempo_final = 0.0
        self.recorde_tempo = None
        self.ultimo_erro = 0.0
        self.contato_anterior = False
        self.resultado_msg = ""
        self.timer_reinicio = 0.0
        self.modo_touch = True

        # Botões de toque para apoio (sem botões mock de simulação)
        self.btn_iniciar = TouchButton(200, 420, 280, 58, "INICIAR (BT3)", COLOR_GREEN)
        self.btn_concluir = TouchButton(544, 420, 280, 58, "CONCLUIR (BT4)", COLOR_CYAN)

    def get_id(self) -> str:
        return "steady_hands"

    def get_nome(self) -> str:
        return "Steady Hands"

    def get_descricao(self) -> str:
        return "Conduza a argola pelo arame sem encostar nele no menor tempo possível."

    def iniciar(self) -> None:
        self.retorno_menu = False
        self.vidas = 3
        self.estado = "ESPERA"
        self.contato_anterior = False
        self.resultado_msg = "POSICIONE A ARGOLA E INICIE"
        self._atualizar_leds_vidas()
        self.hw.set_led(3, False)
        self.hw.set_led(4, False)

    def _atualizar_leds_vidas(self):
        self.hw.set_led(0, self.vidas >= 1)
        self.hw.set_led(1, self.vidas >= 2)
        self.hw.set_led(2, self.vidas >= 3)

    def processar_eventos(self, eventos_pygame: list[pygame.event.Event], estado_botoes: dict[str, bool]) -> None:
        if "MODO_TOUCH" in estado_botoes:
            self.modo_touch = estado_botoes["MODO_TOUCH"]

        for evento in eventos_pygame:
            if self.header.processar_evento(evento):
                self.retorno_menu = True

            if evento.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                self.modo_touch = True

            if self.estado == "ESPERA" and self.btn_iniciar.processar_evento(evento):
                self._iniciar_partida()

            elif self.estado == "PERCURSO" and self.btn_concluir.processar_evento(evento):
                self._concluir_partida()

        # Botões físicos da GPIO (BT3 inicia, BT4 conclui)
        if estado_botoes.get("BT3"):
            self.modo_touch = False
            if self.estado == "ESPERA":
                self._iniciar_partida()

        elif estado_botoes.get("BT4"):
            self.modo_touch = False
            if self.estado == "PERCURSO":
                self._concluir_partida()

    def _iniciar_partida(self):
        self.vidas = 3
        self._atualizar_leds_vidas()
        self.hw.set_led(3, True)  # LED indicador de partida ativa
        self.tempo_inicio = time.time()
        self.estado = "PERCURSO"
        self.audio.tocar("acerto")
        self.resultado_msg = "PERCURSO EM ANDAMENTO!"

    def _registrar_erro_contato(self):
        agora = time.time()
        if agora - self.ultimo_erro >= 0.12:  # Debounce de 120ms
            self.ultimo_erro = agora
            self.vidas = max(0, self.vidas - 1)
            self._atualizar_leds_vidas()
            self.hw.set_led(4, True)  # LED 5 pisca em erro
            self.audio.tocar("choque")

            if self.vidas == 0:
                self.estado = "RESULTADO"
                self.hw.set_led(3, False)
                self.audio.tocar("erro")
                self.resultado_msg = "GAME OVER! AS VIDAS ACABARAM"
                self.timer_reinicio = agora + 4.5

    def _concluir_partida(self):
        agora = time.time()
        self.tempo_final = agora - self.tempo_inicio
        self.estado = "RESULTADO"
        self.hw.set_led(3, False)

        novo_recorde = False
        if self.recorde_tempo is None or self.tempo_final < self.recorde_tempo:
            self.recorde_tempo = self.tempo_final
            novo_recorde = True
            self.audio.tocar("vitoria")
        else:
            self.audio.tocar("acerto")

        self.resultado_msg = f"PERCURSO CONCLUÍDO! ({self.tempo_final:.2f} s)"
        if novo_recorde:
            self.resultado_msg += " *NOVO RECORDE*"
        self.timer_reinicio = agora + 5.0

    def atualizar(self, dt: float) -> None:
        agora = time.time()

        if self.estado == "PERCURSO":
            # Leitura do sensor de arame na GPIO 16 (LOW quando toca)
            contato_fisico = self.hw.contato_arame_ativo()
            self.hw.set_led(4, contato_fisico)

            if contato_fisico and not self.contato_anterior:
                self._registrar_erro_contato()

            self.contato_anterior = contato_fisico

        elif self.estado == "RESULTADO":
            if agora >= self.timer_reinicio:
                self.iniciar()

    def renderizar(self, superficie: pygame.Surface) -> None:
        superficie.fill(COLOR_BG)
        fonte_tit = pygame.font.SysFont("arial", 22, bold=True)
        fonte_med = pygame.font.SysFont("arial", 18, bold=True)
        fonte_peq = pygame.font.SysFont("arial", 15)
        fonte_gra = pygame.font.SysFont("arial", 62, bold=True)

        self.header.renderizar(superficie, fonte_tit, fonte_peq)

        # Painel Central do Cronômetro
        painel_tempo = pygame.Rect(180, 100, 664, 290)
        pygame.draw.rect(superficie, COLOR_PANEL, painel_tempo, border_radius=16)
        pygame.draw.rect(superficie, COLOR_BORDER, painel_tempo, width=2, border_radius=16)

        # Cronômetro Digital
        tempo_atual = (time.time() - self.tempo_inicio) if self.estado == "PERCURSO" else \
                      self.tempo_final if self.estado == "RESULTADO" else 0.0

        txt_tempo = f"{tempo_atual:.2f} s"
        surf_tempo = fonte_gra.render(txt_tempo, True, COLOR_YELLOW if self.estado == "PERCURSO" else COLOR_TEXT)
        superficie.blit(surf_tempo, surf_tempo.get_rect(center=(512, 175)))

        # Vidas Restantes
        surf_vidas = fonte_med.render(f"VIDAS: {'[O] ' * self.vidas}{'[-] ' * (3 - self.vidas)}", True, COLOR_GREEN if self.vidas > 1 else COLOR_RED)
        superficie.blit(surf_vidas, surf_vidas.get_rect(center=(512, 250)))

        # Mensagem de Status
        surf_msg = fonte_med.render(self.resultado_msg, True, COLOR_CYAN if self.estado == "PERCURSO" else COLOR_YELLOW)
        superficie.blit(surf_msg, surf_msg.get_rect(center=(512, 310)))

        # Recorde
        rec_txt = f"MELHOR TEMPO: {self.recorde_tempo:.2f} s" if self.recorde_tempo else "MELHOR TEMPO: --"
        surf_rec = fonte_peq.render(rec_txt, True, COLOR_TEXT_DIM)
        superficie.blit(surf_rec, surf_rec.get_rect(center=(512, 355)))

        # Controles (Oculta botões touch se estiver em modo físico)
        if self.modo_touch:
            self.btn_iniciar.renderizar(superficie, fonte_med)
            self.btn_concluir.renderizar(superficie, fonte_med)
        else:
            rect_hud = pygame.Rect(180, 430, 664, 44)
            pygame.draw.rect(superficie, (18, 22, 36), rect_hud, border_radius=10)
            pygame.draw.rect(superficie, COLOR_BORDER, rect_hud, width=1, border_radius=10)
            surf_hud = fonte_peq.render("[BT3] INICIAR     |     [ARAME / ARGOLA] PERCURSO     |     [BT4] CONCLUIR", True, COLOR_TEXT_DIM)
            superficie.blit(surf_hud, surf_hud.get_rect(center=rect_hud.center))

    def encerrar(self) -> None:
        self.hw.apagar_leds()
        self.audio.parar_todos()

    def solicitou_retorno(self) -> bool:
        return self.retorno_menu
