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
        self.header = HeaderBar("TECH ARCADE CONSOLE — 7 JOGOS", botao_voltar=False, botao_desligar=True)

        # Modal de desligamento seguro
        self.modal_desligar = False
        self.btn_confirmar_desligar = TouchButton(290, 325, 200, 52, "SIM, DESLIGAR", (255, 60, 90))
        self.btn_cancelar_desligar = TouchButton(534, 325, 200, 52, "CANCELAR", COLOR_CYAN)

        # Botões de navegação por toque na base
        self.btn_anterior = TouchButton(60, 480, 220, 56, "< ANTERIOR (BT2)", COLOR_CYAN)
        self.btn_jogar = TouchButton(362, 475, 300, 66, "JOGAR AGORA! (BT5)", COLOR_GREEN)
        self.btn_proximo = TouchButton(744, 480, 220, 56, "PRÓXIMO > (BT3)", COLOR_CYAN)

    def processar_eventos(self, eventos_pygame: list[pygame.event.Event], input_mgr) -> Jogo | str | None:
        """Processa interações de toque e botões físicos da GPIO."""
        # Se o diálogo de desligar estiver aberto, captura apenas as ações dele
        if self.modal_desligar:
            for evento in eventos_pygame:
                if self.btn_confirmar_desligar.processar_evento(evento):
                    return "DESLIGAR"
                elif self.btn_cancelar_desligar.processar_evento(evento):
                    self.modal_desligar = False
                    return None
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    self.modal_desligar = False
                    return None
                elif evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_s):
                    return "DESLIGAR"

            if input_mgr.foi_pressionado("BT5"):
                return "DESLIGAR"
            if input_mgr.foi_pressionado("BT1") or input_mgr.foi_pressionado("BT2"):
                self.modal_desligar = False
            return None

        # 1. Comandos Físicos da GPIO
        if input_mgr.foi_pressionado("BT2"):
            self.indice_selecionado = (self.indice_selecionado - 1) % len(self.jogos)

        if input_mgr.foi_pressionado("BT3"):
            self.indice_selecionado = (self.indice_selecionado + 1) % len(self.jogos)

        if input_mgr.foi_pressionado("BT5"):
            return self.jogos[self.indice_selecionado]

        # 2. Interações por Toque na Tela Touch
        for evento in eventos_pygame:
            if self.header.processar_desligar(evento):
                self.modal_desligar = True
                return None

            elif self.btn_anterior.processar_evento(evento):
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

    def renderizar(self, superficie: pygame.Surface, fonte_tit: pygame.font.Font, fonte_med: pygame.font.Font, fonte_peq: pygame.font.Font, exibir_touch: bool = True):
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

                    # Badge central
                    badge_rect = pygame.Rect(cx - 130, cy + 95, 260, 44)
                    pygame.draw.rect(superficie, (20, 50, 85), badge_rect, border_radius=8)
                    txt_badge = "TOQUE PARA INICIAR (BT5)" if exibir_touch else "PRESSIONE BT5 PARA JOGAR"
                    surf_badge = fonte_peq.render(txt_badge, True, COLOR_YELLOW)
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

        # Renderiza os controles na base (Oculta botões touch se estiver em modo físico)
        if exibir_touch:
            self.btn_anterior.renderizar(superficie, fonte_peq)
            self.btn_jogar.renderizar(superficie, fonte_med)
            self.btn_proximo.renderizar(superficie, fonte_peq)
        else:
            rect_hud = pygame.Rect(112, 492, 800, 38)
            pygame.draw.rect(superficie, (18, 22, 36), rect_hud, border_radius=8)
            pygame.draw.rect(superficie, COLOR_BORDER, rect_hud, width=1, border_radius=8)
            surf_hud = fonte_peq.render("[BT2] ANTERIOR     |     [BT5] JOGAR     |     [BT3] PRÓXIMO", True, COLOR_TEXT_DIM)
            superficie.blit(surf_hud, surf_hud.get_rect(center=rect_hud.center))

        # Diálogo Modal de Desligamento Seguro
        if self.modal_desligar:
            overlay = pygame.Surface((1024, 600), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 210))
            superficie.blit(overlay, (0, 0))

            rect_modal = pygame.Rect(237, 140, 550, 270)
            pygame.draw.rect(superficie, (10, 12, 20), rect_modal.move(0, 8), border_radius=18)
            pygame.draw.rect(superficie, COLOR_PANEL, rect_modal, border_radius=18)
            pygame.draw.rect(superficie, (255, 60, 90), rect_modal, width=3, border_radius=18)

            surf_tit = fonte_tit.render("DESLIGAR O CONSOLE?", True, (255, 80, 100))
            superficie.blit(surf_tit, surf_tit.get_rect(center=(512, 185)))

            surf_desc1 = fonte_med.render("O Raspberry Pi será encerrado com total segurança.", True, COLOR_TEXT)
            superficie.blit(surf_desc1, surf_desc1.get_rect(center=(512, 230)))

            surf_desc2 = fonte_peq.render("Aguarde a luz verde apagar antes de desconectar da tomada.", True, COLOR_TEXT_DIM)
            superficie.blit(surf_desc2, surf_desc2.get_rect(center=(512, 265)))

            self.btn_confirmar_desligar.renderizar(superficie, fonte_med)
            self.btn_cancelar_desligar.renderizar(superficie, fonte_med)
