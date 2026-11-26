"""
Jogo 6: Perfect Time (Desafio de Percepção Temporal).
Portado e aprimorado para Raspberry Pi 3 B+ (1024x600) em conformidade com Clean Code, POO e SOLID:
- O jogador deve estimar mentalmente 5.000 segundos sem relógio visível
- Acionamento via Botão Físico BT1 (Pino 11 / GPIO 17) ou Toque na Tela Touch
- Temporização de alta precisão em microssegundos com time.perf_counter()
- Indicação nos LEDs físicos: LED 1 (Vermelho / D5) e LED 2 (Verde / D6)
- Cálculo real de pontuação: 1000 - min(erro_ms, 1000) e classificação conforme regras originais
"""

import time
import pygame
from core.game_interface import Jogo
from core.hardware import HardwareManager
from core.audio_manager import AudioManager
from ui.components import HeaderBar, TouchButton, COLOR_BG, COLOR_PANEL, COLOR_BORDER, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_CYAN


class JogoPerfectTime(Jogo):
    TEMPO_ALVO = 5.000  # 5 segundos exatos
    TEMPO_LIMITE = 30.0  # Limite máximo de espera

    CLASSIFICACOES = [
        (100, "PERFEITO!", COLOR_GREEN),
        (250, "EXCELENTE!", COLOR_CYAN),
        (500, "BOM!", COLOR_YELLOW),
        (1000, "REGULAR!", COLOR_YELLOW),
        (999999, "RUIM!", COLOR_RED)
    ]

    def __init__(self, hw: HardwareManager, audio: AudioManager):
        self.hw = hw
        self.audio = audio
        self.header = HeaderBar("PERFECT TIME — DESAFIO DE 5 SEGUNDOS")
        self.retorno_menu = False

        self.estado = "AGUARDANDO"  # AGUARDANDO, ESTIMANDO, RESULTADO
        self.t_inicio = 0.0
        self.tempo_registrado = 0.0
        self.erro_ms = 0
        self.direcao_erro = ""
        self.pontos = 0
        self.classificacao = ""
        self.cor_classificacao = COLOR_TEXT
        self.recorde_erro_ms = None
        self.timer_resultado = 0.0
        self.modo_touch = True

        # Botão touch central grande para acionamento
        self.btn_gatilho = TouchButton(312, 145, 400, 255, "INICIAR", COLOR_CYAN)

    def get_id(self) -> str:
        return "perfect_time"

    def get_nome(self) -> str:
        return "Perfect Time"

    def get_descricao(self) -> str:
        return "Estime mentalmente 5 segundos exatos. Quanto mais perto de 5.000s, maior a pontuação!"

    def iniciar(self) -> None:
        self.retorno_menu = False
        self.estado = "AGUARDANDO"
        self.tempo_registrado = 0.0
        self.erro_ms = 0
        self.direcao_erro = ""
        self.pontos = 0
        self.classificacao = ""
        self.cor_classificacao = COLOR_TEXT
        self.btn_gatilho.cor_destaque = COLOR_CYAN
        self.hw.apagar_leds()

    def processar_eventos(self, eventos_pygame: list[pygame.event.Event], estado_botoes: dict[str, bool]) -> None:
        if "MODO_TOUCH" in estado_botoes:
            self.modo_touch = estado_botoes["MODO_TOUCH"]

        for evento in eventos_pygame:
            if self.header.processar_evento(evento):
                self.retorno_menu = True

            # Disparo instantâneo no toque (DOWN) - latência zero idêntica ao botão físico BT1
            if evento.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                self.modo_touch = True
                pos = evento.pos if hasattr(evento, "pos") else (int(evento.x * 1024), int(evento.y * 600))
                if self.btn_gatilho.rect.collidepoint(pos):
                    self._acionar()

        # Botão físico BT1 ou BT2
        if estado_botoes.get("BT1") or estado_botoes.get("BT2"):
            self.modo_touch = False
            self._acionar()

    def _acionar(self):
        agora = time.perf_counter()

        if self.estado == "RESULTADO":
            self.iniciar()
            return

        if self.estado == "AGUARDANDO":
            # Inicia contagem cega
            self.t_inicio = agora
            self.estado = "ESTIMANDO"
            self.hw.set_led(1, True)  # LED Verde ligado durante contagem
            self.hw.set_led(0, False)
            self.audio.tocar("acerto")
            self.btn_gatilho.cor_destaque = COLOR_YELLOW

        elif self.estado == "ESTIMANDO":
            # Interrompe e calcula o tempo
            duracao = agora - self.t_inicio
            self.tempo_registrado = duracao
            self.hw.apagar_leds()

            diff = duracao - self.TEMPO_ALVO
            self.erro_ms = int(abs(diff) * 1000)
            if abs(diff) < 0.001:
                self.direcao_erro = "EXATO!"
            elif diff < 0:
                self.direcao_erro = "ADIANTADO"
            else:
                self.direcao_erro = "ATRASADO"

            self.pontos = max(0, 1000 - min(self.erro_ms, 1000))

            # Classificação
            for limite, nome, cor in self.CLASSIFICACOES:
                if self.erro_ms <= limite:
                    self.classificacao = nome
                    self.cor_classificacao = cor
                    break

            # Sinalização de LEDs conforme as regras originais
            if self.erro_ms <= 250:
                self.hw.set_led(1, True)  # LED Verde em resultados excelentes
            else:
                self.hw.set_led(0, True)  # LED Vermelho em erros maiores

            # Verificação de recorde (menor erro em ms)
            novo_recorde = False
            if self.recorde_erro_ms is None or self.erro_ms < self.recorde_erro_ms:
                self.recorde_erro_ms = self.erro_ms
                novo_recorde = True
                self.audio.tocar("vitoria")
            else:
                self.audio.tocar("acerto")

            self.estado = "RESULTADO"
            self.timer_resultado = time.time() + 4.5

    def atualizar(self, dt: float) -> None:
        agora = time.time()

        if self.estado == "ESTIMANDO":
            # Verifica timeout de abandono (30s)
            if (time.perf_counter() - self.t_inicio) >= self.TEMPO_LIMITE:
                self.estado = "RESULTADO"
                self.classificacao = "TEMPO LIMITE EXCEDIDO!"
                self.cor_classificacao = COLOR_RED
                self.tempo_registrado = self.TEMPO_LIMITE
                self.erro_ms = 25000
                self.direcao_erro = "LIMITE EXCEDIDO"
                self.pontos = 0
                self.hw.set_led(0, True)
                self.audio.tocar("erro")
                self.timer_resultado = agora + 4.0

        elif self.estado == "RESULTADO":
            if agora >= self.timer_resultado:
                self.iniciar()

    def renderizar(self, superficie: pygame.Surface) -> None:
        superficie.fill(COLOR_BG)
        fonte_tit = pygame.font.SysFont("arial", 22, bold=True)
        fonte_med = pygame.font.SysFont("arial", 18, bold=True)
        fonte_peq = pygame.font.SysFont("arial", 15)
        fonte_gra = pygame.font.SysFont("arial", 46, bold=True)

        self.header.renderizar(superficie, fonte_tit, fonte_peq)

        inst_entrada = "TOQUE NA TELA" if self.modo_touch else "PRESSIONE [BT1/BT2]"

        # Botão / Painel de Acionamento Central
        if self.estado == "AGUARDANDO":
            self.btn_gatilho.texto = f"DESAFIO DE TEMPO\n\n[ INICIAR ]\n\n{inst_entrada} P/ COMEÇAR"
            self.btn_gatilho.cor_destaque = COLOR_CYAN
            self.btn_gatilho.renderizar(superficie, fonte_med)
        elif self.estado == "ESTIMANDO":
            self.btn_gatilho.texto = f"CONTAGEM ATIVA!\n\n[ PARAR ]\n\n{inst_entrada} P/ PARAR"
            self.btn_gatilho.cor_destaque = COLOR_YELLOW
            self.btn_gatilho.renderizar(superficie, fonte_med)
        elif self.estado == "RESULTADO":
            # Renderizamos o card de resultado com destaque do tempo registrado
            cor_fundo = (25, 32, 52) if not self.btn_gatilho.pressionado else (45, 58, 85)
            pygame.draw.rect(superficie, (5, 6, 12), self.btn_gatilho.rect.move(0, 3), border_radius=12)
            pygame.draw.rect(superficie, cor_fundo, self.btn_gatilho.rect, border_radius=12)
            pygame.draw.rect(superficie, self.cor_classificacao, self.btn_gatilho.rect, width=3, border_radius=12)

            # Rótulo superior
            surf_rot = fonte_peq.render("SEU TEMPO REGISTRADO:", True, COLOR_TEXT_DIM)
            superficie.blit(surf_rot, surf_rot.get_rect(center=(self.btn_gatilho.rect.centerx, self.btn_gatilho.rect.top + 34)))

            # Tempo registrado em destaque (ex.: "4.872 s" ou "5.000 s")
            txt_tempo = f"{self.tempo_registrado:.3f} s"
            surf_tempo = fonte_gra.render(txt_tempo, True, self.cor_classificacao)
            superficie.blit(surf_tempo, surf_tempo.get_rect(center=(self.btn_gatilho.rect.centerx, self.btn_gatilho.rect.top + 84)))

            # Diferença em ms e direção (adiantado / atrasado)
            sinal = "-" if (self.tempo_registrado < self.TEMPO_ALVO and self.erro_ms > 0) else ("+" if self.tempo_registrado > self.TEMPO_ALVO else "")
            txt_diff = f"DIFERENÇA: {sinal}{self.erro_ms} ms ({self.direcao_erro})"
            cor_diff = COLOR_GREEN if self.erro_ms == 0 else (COLOR_CYAN if self.erro_ms <= 250 else COLOR_YELLOW)
            surf_diff = fonte_med.render(txt_diff, True, cor_diff)
            superficie.blit(surf_diff, surf_diff.get_rect(center=(self.btn_gatilho.rect.centerx, self.btn_gatilho.rect.top + 138)))

            # Classificação
            surf_cls = fonte_med.render(f"★ {self.classificacao} ★", True, self.cor_classificacao)
            superficie.blit(surf_cls, surf_cls.get_rect(center=(self.btn_gatilho.rect.centerx, self.btn_gatilho.rect.top + 174)))

            # Dica para reiniciar
            surf_re = fonte_peq.render(f"{inst_entrada} para jogar novamente", True, COLOR_TEXT_DIM)
            superficie.blit(surf_re, surf_re.get_rect(center=(self.btn_gatilho.rect.centerx, self.btn_gatilho.rect.bottom - 22)))

        # Painel Inferior de Estatísticas
        painel_stats = pygame.Rect(162, 420, 700, 110)
        pygame.draw.rect(superficie, COLOR_PANEL, painel_stats, border_radius=14)
        pygame.draw.rect(superficie, COLOR_BORDER, painel_stats, width=2, border_radius=14)

        if self.estado == "RESULTADO":
            surf_res = fonte_med.render(f"PONTUAÇÃO: {self.pontos} / 1000 PONTOS    |    TEMPO ALVO: 5.000 s", True, COLOR_TEXT)
            superficie.blit(surf_res, surf_res.get_rect(center=(512, 452)))

            rec_txt = f"MELHOR RECORDE: {self.recorde_erro_ms} ms de diferença" if self.recorde_erro_ms is not None else "RECORD: --"
            surf_rec = fonte_peq.render(rec_txt, True, COLOR_YELLOW)
            superficie.blit(surf_rec, surf_rec.get_rect(center=(512, 492)))
        elif self.estado == "ESTIMANDO":
            surf_inst = fonte_med.render("CONTE MENTALMENTE EM SILÊNCIO: 1... 2... 3... 4... 5!", True, COLOR_YELLOW)
            superficie.blit(surf_inst, surf_inst.get_rect(center=(512, 460)))
            surf_sub = fonte_peq.render("Aperte o botão quando achar que exatamente 5.000 segundos se passaram.", True, COLOR_TEXT_DIM)
            superficie.blit(surf_sub, surf_sub.get_rect(center=(512, 492)))
        else:
            surf_inst = fonte_med.render("OBJETIVO: PARAR O CRONÔMETRO EM EXATAMENTE 5.000 SEGUNDOS", True, COLOR_CYAN)
            superficie.blit(surf_inst, surf_inst.get_rect(center=(512, 460)))
            surf_sub = fonte_peq.render("Use [BT1], [BT2] ou toque na tela para iniciar e para parar.", True, COLOR_TEXT_DIM)
            superficie.blit(surf_sub, surf_sub.get_rect(center=(512, 492)))

    def encerrar(self) -> None:
        self.hw.apagar_leds()
        self.audio.parar_todos()

    def solicitou_retorno(self) -> bool:
        return self.retorno_menu
