"""
Camada de Entrada Unificada (Input Manager).
Unifica:
1. Eventos de Toque (Touchscreen via Pygame MOUSEBUTTON / FINGER)
2. Teclas de teclado (1, 2, 3, 4, 5, Setas, Espaço, Esc para debug e testes)
3. Botões físicos da GPIO da Raspberry Pi (BT1 a BT5)
"""

import time
import pygame
from core.hardware import HardwareManager


class InputManager:
    """Gerencia entradas unificadas com detecção de bordas e combinação universal de saída."""

    def __init__(self, hardware: HardwareManager):
        self.hw = hardware
        self.estado_anterior = {"BT1": False, "BT2": False, "BT3": False, "BT4": False, "BT5": False}
        self.estado_atual = {"BT1": False, "BT2": False, "BT3": False, "BT4": False, "BT5": False}
        self.borda_descida = {"BT1": False, "BT2": False, "BT3": False, "BT4": False, "BT5": False, "MODO_TOUCH": True}

        # Modo de entrada atual: "TOUCH" ou "FISICO" (Alterna dinamicamente)
        self.modo_entrada = "TOUCH"

        # Timer para o botão universal de saída (Segurar BT2 por 1.5s, ou BT1+BT2 juntos, ou BT5)
        self.tempo_inicio_retorno = 0.0
        self.solicitou_retorno_menu = False

    def processar(self, eventos_pygame: list[pygame.event.Event]):
        """Atualiza o estado consolidado dos controles físicos e emulados."""
        self.hw.atualizar()

        # Detecção de interação touch nos eventos
        for evento in eventos_pygame:
            if evento.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                self.modo_entrada = "TOUCH"
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.solicitou_retorno_menu = True
                else:
                    self.modo_entrada = "FISICO"

        # Copia estados atuais dos botões físicos
        houve_acao_fisica = False
        for btn in ("BT1", "BT2", "BT3", "BT4", "BT5"):
            press = self.hw.esta_pressionado(btn)
            self.estado_atual[btn] = press
            if press:
                houve_acao_fisica = True

        # Mapeia teclas de teclado para auxiliar testes fora da Raspberry Pi
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_1] or teclas[pygame.K_LEFT]:
            self.estado_atual["BT1"] = True
            houve_acao_fisica = True
        if teclas[pygame.K_2] or teclas[pygame.K_UP]:
            self.estado_atual["BT2"] = True
            houve_acao_fisica = True
        if teclas[pygame.K_3] or teclas[pygame.K_DOWN]:
            self.estado_atual["BT3"] = True
            houve_acao_fisica = True
        if teclas[pygame.K_4] or teclas[pygame.K_RIGHT]:
            self.estado_atual["BT4"] = True
            houve_acao_fisica = True
        if teclas[pygame.K_5] or teclas[pygame.K_RETURN] or teclas[pygame.K_SPACE]:
            self.estado_atual["BT5"] = True
            houve_acao_fisica = True

        if houve_acao_fisica:
            self.modo_entrada = "FISICO"

        # Calcula transições de borda (apenas no instante do clique)
        for btn in ("BT1", "BT2", "BT3", "BT4", "BT5"):
            anterior = self.estado_anterior[btn]
            atual = self.estado_atual[btn]
            self.borda_descida[btn] = (atual and not anterior)
            self.estado_anterior[btn] = atual

        self.borda_descida["MODO_TOUCH"] = (self.modo_entrada == "TOUCH")

        # Verificação do comando universal de retorno ao menu:
        # 1. Segurar BT2 (ou BT4) por 1.5s
        # 2. Ou pressionar BT1 + BT2 juntos por 1.0s
        # 3. Ou segurar BT5 por 1.5s (caso ainda esteja conectado)
        agora = time.time()
        segurando_saida = (
            (self.estado_atual["BT1"] and (self.estado_atual["BT2"] or self.estado_atual["BT4"])) or
            self.estado_atual["BT2"] or
            self.estado_atual["BT4"] or
            self.estado_atual["BT5"]
        )

        # Se ambos os botões estão pressionados, retorno rápido (1.0s)
        limite_tempo = 1.0 if (self.estado_atual["BT1"] and (self.estado_atual["BT2"] or self.estado_atual["BT4"])) else 1.5

        if segurando_saida:
            if self.tempo_inicio_retorno == 0.0:
                self.tempo_inicio_retorno = agora
            elif (agora - self.tempo_inicio_retorno) >= limite_tempo:
                self.solicitou_retorno_menu = True
        else:
            self.tempo_inicio_retorno = 0.0

    def exibir_botoes_touch(self) -> bool:
        """Retorna True se os botões auxiliares touch devem ser desenhados na tela."""
        return self.modo_entrada == "TOUCH"

    def foi_pressionado(self, nome_botao: str) -> bool:
        """Retorna True apenas no frame em que o botão foi acionado."""
        return self.borda_descida.get(nome_botao, False)

    def esta_segurando(self, nome_botao: str) -> bool:
        """Retorna True enquanto o botão permanecer pressionado."""
        return self.estado_atual.get(nome_botao, False)

    def consumir_retorno_menu(self) -> bool:
        """Verifica e consome a flag de retorno ao menu principal."""
        ret = self.solicitou_retorno_menu
        self.solicitou_retorno_menu = False
        return ret
