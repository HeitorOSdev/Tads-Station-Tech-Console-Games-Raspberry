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

        # Texto centralizado (suporte a múltiplas linhas se houver \n)
        linhas = self.texto.split("\n")
        if len(linhas) <= 1:
            surf_texto = fonte.render(self.texto, True, COLOR_TEXT)
            rect_texto = surf_texto.get_rect(center=self.rect.center)
            superficie.blit(surf_texto, rect_texto)
        else:
            altura_linha = fonte.get_linesize()
            total_altura = len(linhas) * altura_linha
            y_inicial = self.rect.centery - (total_altura // 2) + (altura_linha // 2)
            for i, linha in enumerate(linhas):
                if linha.strip():
                    surf_texto = fonte.render(linha, True, COLOR_TEXT)
                    rect_texto = surf_texto.get_rect(center=(self.rect.centerx, y_inicial + i * altura_linha))
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


class SystemCommandBar:
    """
    Barra inferior de comandos do sistema (1024x50) que substitui a exibição dos LEDs no rodapé.
    Exibe os comandos principais de controle do console físico e touch:
    - O que cada botão físico faz com um clique simples ([BT1] e [BT2])
    - Ações acionadas ao segurar os botões (ex: 1.5s para Menu, 1.0s com ambos pressionados)
    - Barra dinâmica de progresso com feedback visual caso o jogador esteja segurando para retornar ao menu
    """

    def __init__(self, y: int = 550):
        self.y = y
        self.altura = 50

    def renderizar(
        self,
        superficie: pygame.Surface,
        fonte_peq: pygame.font.Font,
        estado_console: str = "MENU",
        progresso_retorno: float = 0.0
    ):
        # Fundo escuro com borda de destaque superior
        pygame.draw.rect(superficie, (12, 16, 28), (0, self.y, 1024, self.altura))
        pygame.draw.line(superficie, (45, 60, 95), (0, self.y), (1024, self.y), 2)

        # Se o usuário estiver segurando o comando de retorno, exibe feedback visual com barra de progresso
        if progresso_retorno > 0.06 and estado_console == "JOGANDO":
            largura_barra = 580
            altura_barra = 26
            rx = (1024 - largura_barra) // 2
            ry = self.y + 12

            # Fundo da barra
            pygame.draw.rect(superficie, (20, 25, 42), (rx, ry, largura_barra, altura_barra), border_radius=8)
            pygame.draw.rect(superficie, (90, 115, 165), (rx, ry, largura_barra, altura_barra), width=2, border_radius=8)

            # Preenchimento animado
            preenchimento = int(largura_barra * min(1.0, progresso_retorno))
            if preenchimento > 0:
                cor_preenchimento = (255, 205, 50) if progresso_retorno < 0.85 else (40, 240, 130)
                pygame.draw.rect(superficie, cor_preenchimento, (rx, ry, preenchimento, altura_barra), border_radius=8)

            pct = int(progresso_retorno * 100)
            txt_prog = f"RETORNANDO AO MENU PRINCIPAL... {pct}% (SOLTE PARA CANCELAR)"
            cor_txt = (15, 20, 30) if preenchimento > 290 else (240, 245, 255)
            surf_prog = fonte_peq.render(txt_prog, True, cor_txt)
            superficie.blit(surf_prog, surf_prog.get_rect(center=(512, ry + altura_barra // 2)))
            return

        y_l1 = self.y + 15
        y_l2 = self.y + 36

        if estado_console == "MENU":
            txt_l1 = "[BT1] Clique: Próximo Jogo (Carrossel)    •    [BT2] Clique: Iniciar / Confirmar    •    Touch: Seleção Direta"
            surf_l1 = fonte_peq.render(txt_l1, True, (220, 235, 255))
            superficie.blit(surf_l1, surf_l1.get_rect(center=(512, y_l1)))

            txt_l2 = "Segurar [BT2] por 1.5s (ou [BT1+BT2] 1.0s): Retornar ao Menu em Jogos    •    [DESLIGAR]: Topo Direito"
            surf_l2 = fonte_peq.render(txt_l2, True, (140, 160, 195))
            superficie.blit(surf_l2, surf_l2.get_rect(center=(512, y_l2)))
        else:
            txt_l1 = "[BT1] / [BT2] Clique: Ações Físicas do Jogo    •    Tela Touch: Toque Direto nos Elementos"
            surf_l1 = fonte_peq.render(txt_l1, True, (220, 235, 255))
            superficie.blit(surf_l1, surf_l1.get_rect(center=(512, y_l1)))

            txt_l2 = "Segurar [BT2] por 1.5s (ou [BT1+BT2] 1.0s): RETORNAR AO MENU PRINCIPAL    •    [<- VOLTAR]: Topo Esquerdo"
            surf_l2 = fonte_peq.render(txt_l2, True, (255, 215, 80))
            superficie.blit(surf_l2, surf_l2.get_rect(center=(512, y_l2)))


class HardwareLedBar:
    """Mostrador visual dos 5 LEDs físicos do console na parte inferior da tela (mantido para compatibilidade)."""

    CORES_LEDS = [
        (255, 60, 90),   # Vermelho
        (40, 240, 130),  # Verde
        (30, 144, 255),  # Azul
        (255, 215, 0),   # Amarelo
        (255, 140, 0)    # Laranja
    ]
    NOMES_LEDS = ["LED 1 (Vermelho)", "LED 2 (Verde)", "LED 3 (Azul)", "LED 4 (Amarelo)", "LED 5 (Laranja)"]

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
