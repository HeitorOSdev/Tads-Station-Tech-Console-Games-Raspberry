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
        self.borda_descida = {"BT1": False, "BT2": False, "BT3": False, "BT4": False, "BT5": False}

        # Timer para o botão universal de saída (Segurar BT5 por 1.5 segundos)
        self.tempo_inicio_bt5 = 0.0
        self.solicitou_retorno_menu = False

    def processar(self, eventos_pygame: list[pygame.event.Event]):
        """Atualiza o estado consolidado dos controles físicos e emulados."""
        self.hw.atualizar()

        # Copia estados atuais dos botões físicos
        for btn in self.estado_atual.keys():
            self.estado_atual[btn] = self.hw.esta_pressionado(btn)

        # Mapeia teclas de teclado para auxiliar testes fora da Raspberry Pi
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_1] or teclas[pygame.K_LEFT]:
            self.estado_atual["BT1"] = True
        if teclas[pygame.K_2] or teclas[pygame.K_UP]:
            self.estado_atual["BT2"] = True
        if teclas[pygame.K_3] or teclas[pygame.K_DOWN]:
            self.estado_atual["BT3"] = True
        if teclas[pygame.K_4] or teclas[pygame.K_RIGHT]:
            self.estado_atual["BT4"] = True
        if teclas[pygame.K_5] or teclas[pygame.K_RETURN] or teclas[pygame.K_SPACE]:
            self.estado_atual["BT5"] = True

        # Processa cliques e teclas avulsas nos eventos Pygame
        for evento in eventos_pygame:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.solicitou_retorno_menu = True

        # Calcula transições de borda (apenas no instante do clique)
        for btn, atual in self.estado_atual.items():
            anterior = self.estado_anterior[btn]
            self.borda_descida[btn] = (atual and not anterior)
            self.estado_anterior[btn] = atual

        # Verificação do botão de retorno ao menu (Segurar BT5 por 1.5s)
        agora = time.time()
        if self.estado_atual["BT5"]:
            if self.tempo_inicio_bt5 == 0.0:
                self.tempo_inicio_bt5 = agora
            elif (agora - self.tempo_inicio_bt5) >= 1.5:
                self.solicitou_retorno_menu = True
        else:
            self.tempo_inicio_bt5 = 0.0

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
