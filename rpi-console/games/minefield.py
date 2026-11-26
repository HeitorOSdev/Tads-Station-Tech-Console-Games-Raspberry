"""
Jogo 5: Campo Minado Clássico Arcade (Minesweeper com Dedução Lógica).
Grade 3x4 (12 Células) com 3 Minas Ocultas e Pistas Numéricas Clássicas:
- Elimina a aleatoriedade pura: células revelam o número de minas vizinhas (1, 2, 3...)
- Primeiro clique 100% seguro (nunca é mina na primeira jogada)
- Revelação em cadeia automática para células vazias (0 minas vizinhas)
- Totalmente jogável tanto por Toque na Tela quanto com 2 Botões (BT1 = Navegar, BT2 = Abrir)
"""

import random
import time
import pygame
from core.game_interface import Jogo
from core.hardware import HardwareManager
from core.audio_manager import AudioManager
from ui.components import HeaderBar, COLOR_BG, COLOR_PANEL, COLOR_BORDER, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_CYAN


class JogoCampoMinado(Jogo):
    LINHAS = 3
    COLUNAS = 4
    TOTAL_CELULAS = LINHAS * COLUNAS  # 12
    TOTAL_MINAS = 3
    TOTAL_SEGURAS = TOTAL_CELULAS - TOTAL_MINAS  # 9

    def __init__(self, hw: HardwareManager, audio: AudioManager):
        self.hw = hw
        self.audio = audio
        self.header = HeaderBar("CAMPO MINADO — DEDUÇÃO LÓGICA")
        self.retorno_menu = False

        self.minas = [False] * self.TOTAL_CELULAS
        self.descobertos = [False] * self.TOTAL_CELULAS
        self.contagem_vizinhos = [0] * self.TOTAL_CELULAS
        self.primeiro_clique = True
        self.seguras_abertas = 0
        self.estado = "JOGANDO"  # JOGANDO, VITORIA, DERROTA
        self.timer_reinicio = 0.0
        self.mina_detonada_idx = -1
        self.cursor = 0
        self.modo_touch = True
        self.ultimo_toque = 0.0

        # Criação dos retângulos das 12 células centralizadas na tela (1024x600)
        # Largura: 150px, Altura: 100px, Espaçamento: 18px
        largura_celula = 150
        altura_celula = 100
        espacamento = 18
        largura_grade = (self.COLUNAS * largura_celula) + ((self.COLUNAS - 1) * espacamento)
        x_inicial = (1024 - largura_grade) // 2
        y_inicial = 142

        self.rects_celulas = []
        for r in range(self.LINHAS):
            for c in range(self.COLUNAS):
                x = x_inicial + c * (largura_celula + espacamento)
                y = y_inicial + r * (altura_celula + espacamento)
                self.rects_celulas.append(pygame.Rect(x, y, largura_celula, altura_celula))

    def get_id(self) -> str:
        return "minefield"

    def get_nome(self) -> str:
        return "Campo Minado"

    def get_descricao(self) -> str:
        return "Campo Minado clássico: use a lógica dos números vizinhos para desarmar 3 minas em 12 células!"

    def iniciar(self) -> None:
        self.retorno_menu = False
        self.minas = [False] * self.TOTAL_CELULAS
        self.descobertos = [False] * self.TOTAL_CELULAS
        self.contagem_vizinhos = [0] * self.TOTAL_CELULAS
        self.primeiro_clique = True
        self.seguras_abertas = 0
        self.estado = "JOGANDO"
        self.mina_detonada_idx = -1
        self.cursor = 0
        self.ultimo_toque = 0.0
        self.hw.apagar_leds()

    def _obter_vizinhos(self, idx: int) -> list[int]:
        r, c = idx // self.COLUNAS, idx % self.COLUNAS
        viz = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.LINHAS and 0 <= nc < self.COLUNAS:
                    viz.append(nr * self.COLUNAS + nc)
        return viz

    def _gerar_tabuleiro(self, primeiro_idx: int):
        """Garante que o primeiro clique nunca seja uma mina e tenha boa abertura inicial."""
        self.minas = [False] * self.TOTAL_CELULAS
        viz_primeiro = set(self._obter_vizinhos(primeiro_idx))
        viz_primeiro.add(primeiro_idx)

        # Prefere colocar minas fora da vizinhança imediata do primeiro clique
        candidatos = [i for i in range(self.TOTAL_CELULAS) if i not in viz_primeiro]
        if len(candidatos) < self.TOTAL_MINAS:
            candidatos = [i for i in range(self.TOTAL_CELULAS) if i != primeiro_idx]

        posicoes_minas = random.sample(candidatos, self.TOTAL_MINAS)
        for p in posicoes_minas:
            self.minas[p] = True

        # Calcula a contagem de vizinhos para cada célula
        for i in range(self.TOTAL_CELULAS):
            if not self.minas[i]:
                self.contagem_vizinhos[i] = sum(1 for v in self._obter_vizinhos(i) if self.minas[v])

    def processar_eventos(self, eventos_pygame: list[pygame.event.Event], estado_botoes: dict[str, bool]) -> None:
        if "MODO_TOUCH" in estado_botoes:
            self.modo_touch = estado_botoes["MODO_TOUCH"]

        agora = time.time()
        for evento in eventos_pygame:
            if self.header.processar_evento(evento):
                self.retorno_menu = True

            # Toque nas células da tela (com debounce de 160ms)
            if evento.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                self.modo_touch = True
                if agora - self.ultimo_toque >= 0.16:
                    self.ultimo_toque = agora
                    pos = evento.pos if hasattr(evento, "pos") else (int(evento.x * 1024), int(evento.y * 600))
                    
                    if self.estado in ("VITORIA", "DERROTA"):
                        self.iniciar()
                        return

                    for i, rect in enumerate(self.rects_celulas):
                        if rect.collidepoint(pos):
                            self.cursor = i
                            self._revelar_posicao(i)
                            break

        # Comandos físicos com 2 botões (BT1 = Mover cursor, BT2 = Abrir célula)
        if self.estado in ("VITORIA", "DERROTA"):
            if estado_botoes.get("BT1") or estado_botoes.get("BT2"):
                self.iniciar()
                return

        if self.estado == "JOGANDO":
            # BT1: Avança o cursor para a próxima célula fechada
            if estado_botoes.get("BT1"):
                self.modo_touch = False
                self.cursor = (self.cursor + 1) % self.TOTAL_CELULAS
                # Pula células já abertas
                if not all(self.descobertos):
                    for _ in range(self.TOTAL_CELULAS):
                        if not self.descobertos[self.cursor]:
                            break
                        self.cursor = (self.cursor + 1) % self.TOTAL_CELULAS
                self.audio.tocar("menu_move")

            # BT2 (ou BT4 / BT5): Abre a célula apontada pelo cursor
            if estado_botoes.get("BT2") or estado_botoes.get("BT4") or estado_botoes.get("BT5"):
                self.modo_touch = False
                self._revelar_posicao(self.cursor)

    def _revelar_posicao(self, indice: int):
        if self.descobertos[indice]:
            return

        # Primeiro clique garante que não há mina
        if self.primeiro_clique:
            self._gerar_tabuleiro(indice)
            self.primeiro_clique = False

        agora = time.time()

        if self.minas[indice]:
            # Detonou mina!
            self.descobertos[indice] = True
            self.mina_detonada_idx = indice
            self.estado = "DERROTA"
            self.audio.tocar("explosao")
            self.hw.acender_leds()
            self.timer_reinicio = agora + 4.5
            # Revela todas as minas
            for i in range(self.TOTAL_CELULAS):
                if self.minas[i]:
                    self.descobertos[i] = True
            return

        # Revela célula segura e cascateia se for 0 vizinhos
        fila = [indice]
        while fila:
            atual = fila.pop(0)
            if self.descobertos[atual]:
                continue
            self.descobertos[atual] = True
            self.seguras_abertas += 1

            # Cascata para vizinhos se tiver 0 minas adjacentes
            if self.contagem_vizinhos[atual] == 0:
                for v in self._obter_vizinhos(atual):
                    if not self.descobertos[v] and not self.minas[v] and v not in fila:
                        fila.append(v)

        # Atualiza LEDs físicos conforme progresso
        leds_para_acender = int((self.seguras_abertas / self.TOTAL_SEGURAS) * 5)
        for led_i in range(5):
            self.hw.set_led(led_i, led_i < leds_para_acender)

        self.audio.tocar("acerto")

        # Verifica condição de vitória (todas as células seguras abertas)
        if self.seguras_abertas >= self.TOTAL_SEGURAS:
            self.estado = "VITORIA"
            self.audio.tocar("vitoria")
            self.hw.acender_leds()
            self.timer_reinicio = agora + 5.0

    def atualizar(self, dt: float) -> None:
        agora = time.time()
        if self.estado in ("VITORIA", "DERROTA") and agora >= self.timer_reinicio:
            self.iniciar()

    def renderizar(self, superficie: pygame.Surface) -> None:
        superficie.fill(COLOR_BG)
        fonte_tit = pygame.font.SysFont("arial", 22, bold=True)
        fonte_med = pygame.font.SysFont("arial", 18, bold=True)
        fonte_peq = pygame.font.SysFont("arial", 15)
        fonte_num = pygame.font.SysFont("arial", 36, bold=True)
        fonte_gra = pygame.font.SysFont("arial", 22, bold=True)

        self.header.renderizar(superficie, fonte_tit, fonte_peq)

        # Painel Superior de Status
        if self.estado == "JOGANDO":
            restantes = self.TOTAL_SEGURAS - self.seguras_abertas
            txt_status = f"MINAS: {self.TOTAL_MINAS}   |   CÉLULAS SEGURAS RESTANTES: {restantes} / {self.TOTAL_SEGURAS}"
            cor_status = COLOR_YELLOW
        elif self.estado == "DERROTA":
            txt_status = "BOOOOM! VOCÊ DETONOU UMA MINA! TOQUE OU APERTE [BT2] P/ RECOMEÇAR"
            cor_status = COLOR_RED
        else:
            txt_status = "PARABÉNS! CAMPO 100% DESARMADO COM SUCESSO! VITÓRIA!"
            cor_status = COLOR_GREEN

        surf_status = fonte_med.render(txt_status, True, cor_status)
        superficie.blit(surf_status, surf_status.get_rect(center=(512, 105)))

        # Cores clássicas dos números do Campo Minado
        cores_numeros = {
            1: COLOR_CYAN,
            2: COLOR_GREEN,
            3: COLOR_YELLOW,
            4: COLOR_RED,
        }

        # Desenho das 12 Células
        for i, rect in enumerate(self.rects_celulas):
            revelado = self.descobertos[i]
            selecionado = (i == self.cursor and not self.modo_touch)

            if not revelado:
                # Célula fechada
                cor_fundo = (28, 36, 56) if selecionado else COLOR_PANEL
                cor_borda = COLOR_YELLOW if selecionado else COLOR_BORDER
                largura_borda = 4 if selecionado else 2

                pygame.draw.rect(superficie, cor_fundo, rect, border_radius=12)
                pygame.draw.rect(superficie, cor_borda, rect, width=largura_borda, border_radius=12)

                if selecionado:
                    surf_cur = fonte_peq.render("[BT2] ABRIR", True, COLOR_YELLOW)
                    superficie.blit(surf_cur, surf_cur.get_rect(center=rect.center))
                else:
                    # Desenha um pequeno losango central para indicar botão tátil
                    pygame.draw.rect(superficie, (35, 45, 70), rect.inflate(-70, -45), border_radius=6)

            else:
                # Célula revelada
                if self.minas[i]:
                    # Mina
                    cor_fundo = (130, 20, 30) if i == self.mina_detonada_idx else (70, 22, 28)
                    cor_borda = COLOR_RED
                    pygame.draw.rect(superficie, cor_fundo, rect, border_radius=12)
                    pygame.draw.rect(superficie, cor_borda, rect, width=2, border_radius=12)

                    txt_mina = "💣 MINA" if i == self.mina_detonada_idx else "MINA"
                    surf_m = fonte_gra.render(txt_mina, True, (255, 230, 230))
                    superficie.blit(surf_m, surf_m.get_rect(center=rect.center))
                else:
                    # Célula segura
                    cor_fundo = (12, 16, 26)  # Fundo rebaixado
                    cor_borda = (26, 36, 56)
                    pygame.draw.rect(superficie, cor_fundo, rect, border_radius=12)
                    pygame.draw.rect(superficie, cor_borda, rect, width=1, border_radius=12)

                    qtd_viz = self.contagem_vizinhos[i]
                    if qtd_viz > 0:
                        cor_num = cores_numeros.get(qtd_viz, COLOR_TEXT)
                        surf_num = fonte_num.render(str(qtd_viz), True, cor_num)
                        superficie.blit(surf_num, surf_num.get_rect(center=rect.center))
                    else:
                        # Vazio (0 vizinhos)
                        pygame.draw.circle(superficie, (40, 50, 75), rect.center, 3)

        # Rodapé com instruções e modo de controle
        if self.modo_touch:
            msg_dica = "Toque em uma célula para abrir | Os números revelam minas vizinhas!"
        else:
            msg_dica = "[BT1] Mover Cursor     |     [BT2] Abrir Célula     |     Segure [BT2] 1.5s p/ Menu"
        surf_dica = fonte_peq.render(msg_dica, True, COLOR_TEXT_DIM)
        superficie.blit(surf_dica, surf_dica.get_rect(center=(512, 520)))

    def encerrar(self) -> None:
        self.hw.apagar_leds()
        self.audio.parar_todos()

    def solicitou_retorno(self) -> bool:
        return self.retorno_menu
