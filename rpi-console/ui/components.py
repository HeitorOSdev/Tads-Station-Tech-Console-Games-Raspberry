"""
Componentes Gráficos Reutilizáveis para Display Touch 7" (1024x600).
- TouchButton: Botões de toque com áreas de toque ampliadas (mínimo 60x60px)
- ArcadeCard: Cartões interativos do carrossel do menu principal
- HeaderBar: Barra de status superior com relógio, recordes e botão de saída
- HardwareLedBar: Indicadores visuais dos 5 LEDs físicos na tela
"""

import time
import pygame

# Paleta de Cores Neon Cyber-Arcade
COLOR_BG = (12, 14, 24)
COLOR_PANEL = (22, 27, 46)
COLOR_BORDER = (45, 55, 95)
COLOR_TEXT = (240, 245, 255)
COLOR_TEXT_DIM = (140, 150, 180)
COLOR_CYAN = (0, 230, 255)
COLOR_YELLOW = (255, 215, 0)
COLOR_RED = (255, 60, 90)
COLOR_GREEN = (40, 240, 130)
COLOR_BLUE = (30, 144, 255)
COLOR_ORANGE = (255, 140, 0)


class TouchButton:
    """Botão com detecção de toque, efeito de clique e estilo visual moderno."""

    def __init__(self, x: int, y: int, largura: int, altura: int, texto: str, cor_destaque=COLOR_CYAN, icone: str = ""):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.cor_destaque = cor_destaque
        self.icone = icone
        self.pressionado = False

    def processar_evento(self, evento: pygame.event.Event) -> bool:
        """Retorna True se o botão foi clicado ou tocado."""
        if evento.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            pos = evento.pos if hasattr(evento, "pos") else (int(evento.x * 1024), int(evento.y * 600))
            if self.rect.collidepoint(pos):
                self.pressionado = True

        elif evento.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
            if self.pressionado:
                self.pressionado = False
                pos = evento.pos if hasattr(evento, "pos") else (int(evento.x * 1024), int(evento.y * 600))
                if self.rect.collidepoint(pos):
                    return True

        return False

    def renderizar(self, superficie: pygame.Surface, fonte: pygame.font.Font):
        cor_fundo = (35, 45, 75) if not self.pressionado else (55, 70, 115)
        cor_borda = self.cor_destaque if self.pressionado else COLOR_BORDER

        # Sombra suave
        sombra_rect = self.rect.copy()
        sombra_rect.y += 3
        pygame.draw.rect(superficie, (5, 6, 12), sombra_rect, border_radius=10)

        # Corpo do botão
        pygame.draw.rect(superficie, cor_fundo, self.rect, border_radius=10)
        pygame.draw.rect(superficie, cor_borda, self.rect, width=2, border_radius=10)

        # Texto centralizado
        surf_texto = fonte.render(self.texto, True, COLOR_TEXT)
        rect_texto = surf_texto.get_rect(center=self.rect.center)
        superficie.blit(surf_texto, rect_texto)


class HeaderBar:
    """Barra superior com título, botão universal de saída e status."""

    def __init__(self, titulo: str, botao_voltar: bool = True, botao_desligar: bool = False):
        self.titulo = titulo
        self.btn_voltar = TouchButton(15, 10, 160, 42, "<- VOLTAR", COLOR_RED) if botao_voltar else None
        self.btn_desligar = TouchButton(865, 10, 145, 42, "DESLIGAR", COLOR_RED) if botao_desligar else None

    def processar_evento(self, evento: pygame.event.Event) -> bool:
        if self.btn_voltar:
            return self.btn_voltar.processar_evento(evento)
        return False

    def processar_desligar(self, evento: pygame.event.Event) -> bool:
        if self.btn_desligar:
            return self.btn_desligar.processar_evento(evento)
        return False

    def renderizar(self, superficie: pygame.Surface, fonte_tit: pygame.font.Font, fonte_sub: pygame.font.Font):
        # Fundo da barra superior
        pygame.draw.rect(superficie, COLOR_PANEL, (0, 0, 1024, 62))
        pygame.draw.line(superficie, COLOR_BORDER, (0, 62), (1024, 62), 2)

        if self.btn_voltar:
            self.btn_voltar.renderizar(superficie, fonte_sub)

        if self.btn_desligar:
            self.btn_desligar.renderizar(superficie, fonte_sub)

        # Título
        surf_tit = fonte_tit.render(self.titulo, True, COLOR_TEXT)
        rect_tit = surf_tit.get_rect(center=(512, 31))
        superficie.blit(surf_tit, rect_tit)

        # Relógio
        hora_str = time.strftime("%H:%M:%S")
        surf_hora = fonte_sub.render(hora_str, True, COLOR_TEXT_DIM)
        pos_x = 760 if self.btn_desligar else 930
        superficie.blit(surf_hora, (pos_x, 22))


class HardwareLedBar:
    """Mostrador visual dos 5 LEDs físicos do console na parte inferior da tela."""

    CORES_LEDS = [
        (255, 60, 90),   # Vermelho
        (40, 240, 130),  # Verde
        (30, 144, 255),  # Azul
        (255, 215, 0),   # Amarelo
        (255, 140, 0)    # Laranja
    ]
    NOMES_LEDS = ["LED 1 (D5)", "LED 2 (D6)", "LED 3 (D13)", "LED 4 (D19)", "LED 5 (D26)"]

    def __init__(self, y: int = 555):
        self.y = y

    def renderizar(self, superficie: pygame.Surface, estados: list[bool], fonte: pygame.font.Font):
        pygame.draw.rect(superficie, (16, 20, 34), (0, self.y, 1024, 45))
        pygame.draw.line(superficie, COLOR_BORDER, (0, self.y), (1024, self.y), 1)

        largura_item = 1024 // 5
        for i in range(5):
            cx = (i * largura_item) + (largura_item // 2)
            cy = self.y + 22
            ligado = estados[i] if i < len(estados) else False

            cor_ativa = self.CORES_LEDS[i] if ligado else (50, 55, 75)
            # Halo luminoso
            if ligado:
                pygame.draw.circle(superficie, (cor_ativa[0]//2, cor_ativa[1]//2, cor_ativa[2]//2), (cx - 45, cy), 12)
            pygame.draw.circle(superficie, cor_ativa, (cx - 45, cy), 8)
            pygame.draw.circle(superficie, (200, 210, 240), (cx - 45, cy), 8, width=1)

            # Rótulo
            surf_lbl = fonte.render(self.NOMES_LEDS[i], True, COLOR_TEXT if ligado else COLOR_TEXT_DIM)
            superficie.blit(surf_lbl, (cx - 28, cy - 8))
