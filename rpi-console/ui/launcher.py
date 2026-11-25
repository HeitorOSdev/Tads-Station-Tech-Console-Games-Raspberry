"""
Launcher Principal / Menu Carrossel em Alta Definição (1024x600).
Apresenta os 7 jogos oficiais do Tech Arcade:
- Navegação fluida por Toque na Tela Touchscreen
- Navegação física pelos Botões da GPIO:
  * BT2 (Cima / Anterior) e BT3 (Baixo / Próximo) para alternar jogos
  * BT5 (Select / Confirmar) para iniciar
"""

import pygame
from core.game_interface import Jogo
from ui.components import TouchButton, HeaderBar, COLOR_BG, COLOR_PANEL, COLOR_BORDER, COLOR_CYAN, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_YELLOW, COLOR_GREEN


class Launcher:
    """Menu Arcade moderno em tela cheia com cartões touch para 7 jogos."""

    def __init__(self, lista_jogos: list[Jogo]):
        self.jogos = lista_jogos
        self.indice_selecionado = 0
        self.header = HeaderBar("TECH ARCADE CONSOLE — 7 JOGOS", botao_voltar=False)

        # Botões de navegação por toque na base
        self.btn_anterior = TouchButton(60, 480, 220, 56, "< ANTERIOR (BT2)", COLOR_CYAN)
        self.btn_jogar = TouchButton(362, 475, 300, 66, "JOGAR AGORA! (BT5)", COLOR_GREEN)
        self.btn_proximo = TouchButton(744, 480, 220, 56, "PRÓXIMO > (BT3)", COLOR_CYAN)

    def processar_eventos(self, eventos_pygame: list[pygame.event.Event], input_mgr) -> Jogo | None:
        """Processa interações de toque e botões físicos da GPIO."""
        # 1. Comandos Físicos da GPIO
        if input_mgr.foi_pressionado("BT2"):
            self.indice_selecionado = (self.indice_selecionado - 1) % len(self.jogos)

        if input_mgr.foi_pressionado("BT3"):
            self.indice_selecionado = (self.indice_selecionado + 1) % len(self.jogos)

        if input_mgr.foi_pressionado("BT5"):
            return self.jogos[self.indice_selecionado]

        # 2. Interações por Toque na Tela Touch
        for evento in eventos_pygame:
            if self.btn_anterior.processar_evento(evento):
                self.indice_selecionado = (self.indice_selecionado - 1) % len(self.jogos)

            elif self.btn_proximo.processar_evento(evento):
                self.indice_selecionado = (self.indice_selecionado + 1) % len(self.jogos)

            elif self.btn_jogar.processar_evento(evento):
                return self.jogos[self.indice_selecionado]

            # Toque direto no card central
            elif evento.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
                pos = evento.pos if hasattr(evento, "pos") else (int(evento.x * 1024), int(evento.y * 600))
                rect_central = pygame.Rect(312, 100, 400, 350)
                if rect_central.collidepoint(pos):
                    return self.jogos[self.indice_selecionado]

        return None

    def renderizar(self, superficie: pygame.Surface, fonte_tit: pygame.font.Font, fonte_med: pygame.font.Font, fonte_peq: pygame.font.Font):
        superficie.fill(COLOR_BG)
        self.header.renderizar(superficie, fonte_tit, fonte_peq)

        # Desenho dos 7 jogos em carrossel dinâmico
        total = len(self.jogos)
        for i, jogo in enumerate(self.jogos):
            offset = i - self.indice_selecionado

            # Normalização para carrossel circular contínuo
            if offset > total // 2:
                offset -= total
            elif offset < -total // 2:
                offset += total

            if abs(offset) <= 2:
                cx = 512 + (offset * 370)
                cy = 270

                if offset == 0:
                    # Card em destaque central
                    rect = pygame.Rect(cx - 190, cy - 165, 380, 340)
                    pygame.draw.rect(superficie, (6, 8, 16), rect.move(0, 6), border_radius=16)
                    pygame.draw.rect(superficie, COLOR_PANEL, rect, border_radius=16)
                    pygame.draw.rect(superficie, COLOR_CYAN, rect, width=3, border_radius=16)

                    # Indicador de Índice (Ex: JOGO 1 DE 7)
                    surf_idx = fonte_peq.render(f"JOGO {i + 1} DE {total}", True, COLOR_YELLOW)
                    superficie.blit(surf_idx, surf_idx.get_rect(center=(cx, cy - 135)))

                    # Título do jogo
                    surf_nome = fonte_tit.render(jogo.get_nome(), True, COLOR_TEXT)
                    superficie.blit(surf_nome, surf_nome.get_rect(center=(cx, cy - 105)))

                    # Linha divisória
                    pygame.draw.line(superficie, COLOR_BORDER, (cx - 150, cy - 80), (cx + 150, cy - 80), 2)

                    # Descrição
                    palavras = jogo.get_descricao().split()
                    linhas = []
                    linha_atual = ""
                    for p in palavras:
                        if len(linha_atual + p) < 32:
                            linha_atual += p + " "
                        else:
                            linhas.append(linha_atual)
                            linha_atual = p + " "
                    linhas.append(linha_atual)

                    for idx_l, l in enumerate(linhas[:4]):
                        surf_l = fonte_peq.render(l.strip(), True, COLOR_TEXT_DIM)
                        superficie.blit(surf_l, surf_l.get_rect(center=(cx, cy - 40 + (idx_l * 24))))

                    # Badge de toque
                    badge_rect = pygame.Rect(cx - 130, cy + 95, 260, 44)
                    pygame.draw.rect(superficie, (20, 50, 85), badge_rect, border_radius=8)
                    surf_badge = fonte_peq.render("TOQUE PARA INICIAR (BT5)", True, COLOR_YELLOW)
                    superficie.blit(surf_badge, surf_badge.get_rect(center=badge_rect.center))

                elif abs(offset) == 1:
                    # Cards laterais menores
                    rect = pygame.Rect(cx - 130, cy - 120, 260, 240)
                    pygame.draw.rect(superficie, (18, 22, 36), rect, border_radius=12)
                    pygame.draw.rect(superficie, COLOR_BORDER, rect, width=1, border_radius=12)

                    surf_nome = fonte_med.render(jogo.get_nome(), True, COLOR_TEXT_DIM)
                    superficie.blit(surf_nome, surf_nome.get_rect(center=(cx, cy - 50)))

                    surf_sub = fonte_peq.render(f"#{i+1}", True, COLOR_BORDER)
                    superficie.blit(surf_sub, surf_sub.get_rect(center=(cx, cy + 20)))

        # Renderiza os botões de controle na base
        self.btn_anterior.renderizar(superficie, fonte_peq)
        self.btn_jogar.renderizar(superficie, fonte_med)
        self.btn_proximo.renderizar(superficie, fonte_peq)
