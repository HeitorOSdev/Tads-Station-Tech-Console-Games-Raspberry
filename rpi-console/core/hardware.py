"""
Gerenciador de Hardware da Raspberry Pi 3 B+ (100% Digital e Desacoplado).
Gerencia:
- 5 Botões Físicos Arcade via GPIO (INPUT_PULLUP a 3.3V)
- 5 LEDs Físicos via GPIO (com resistores de 270R/220R/100R)
- Pista de Arame do Steady Hands (GPIO 16 com proteção ESD de 1k)
- Modo Simulação automático quando executado fora da Raspberry Pi (ex.: Windows/Linux PC)
"""

import sys
import time

try:
    from gpiozero import Button, LED
    RASPBERRY_HARDWARE = True
except (ImportError, Exception):
    RASPBERRY_HARDWARE = False


class HardwareManager:
    """
    Abstração robusta e puramente digital do hardware da Raspberry Pi 3 B+.
    Oferece API unificada para botões, LEDs e sensor da pista de arame.
    """

    # Mapeamento adaptado: LEDs nos pinos 11, 13, 15, 16 (marcados como GPIO 0, 2, 3, 4 no diagrama)
    # e Botões nos pinos 29, 31, 33, 35, 18
    PINOS_BOTOES = {
        "BT1": 5,   # Pino 29: BT1 (P1 / Cor 0 / Start / Esquerda Sup.)
        "BT2": 6,   # Pino 31: BT2 (P1 Desce / Cor 1 / Menu Cima / Esquerda Inf.)
        "BT3": 13,  # Pino 33: BT3 (P2 / Cor 2 / Início Steady / Direita Sup.)
        "BT4": 19,  # Pino 35: BT4 (P2 / Cor 3 / Fim Steady / Direita Inf.)
        "BT5": 24   # Pino 18: BT5 (Centro / Select / Retorno ao Menu 1.5s)
    }

    # LEDs: 4 LEDs do Genius nos Pinos 11, 13, 15, 16 + LED 5 no Pino 37
    PINOS_LEDS = [17, 27, 22, 23, 26]  # BCM 17 (P11), BCM 27 (P13), BCM 22 (P15), BCM 23 (P16), BCM 26 (P37)
    PINO_ARAME = 16                    # Pino 36: Contato da argola metálica (BCM 16 com 1k em série)

    def __init__(self):
        self.is_rpi = RASPBERRY_HARDWARE
        self.botoes = {}
        self.leds = []
        self.sensor_arame = None

        # Estados em cache (para sincronia visual com a UI)
        self.estados_botoes = {"BT1": False, "BT2": False, "BT3": False, "BT4": False, "BT5": False}
        self.estados_leds = [False, False, False, False, False]
        self.estado_arame = False

        self._inicializar_hardware()

    def _inicializar_hardware(self):
        if self.is_rpi:
            try:
                # Inicializa botões físicos com pull-up interno e debounce de 35ms
                for nome, pino in self.PINOS_BOTOES.items():
                    self.botoes[nome] = Button(pino, pull_up=True, bounce_time=0.035)

                # Inicializa LEDs
                for pino in self.PINOS_LEDS:
                    self.leds.append(LED(pino))

                print("[HARDWARE] Raspberry Pi 3 B+ GPIO inicializado com sucesso (Modo 100% Digital).")
            except Exception as e:
                print(f"[HARDWARE ALERTA] Falha ao acessar GPIO real ({e}). Alternando para modo Simulação.")
                self.is_rpi = False
        else:
            print("[HARDWARE INFO] Executando em ambiente Desktop (Modo Mock / Simulação de Hardware ativado).")

    def atualizar(self):
        """Atualiza a leitura dos periféricos físicos."""
        if self.is_rpi:
            for nome, btn in self.botoes.items():
                self.estados_botoes[nome] = btn.is_pressed

            if self.sensor_arame:
                self.estado_arame = self.sensor_arame.is_pressed

    def set_led(self, indice: int, ligado: bool):
        """Liga ou desliga um LED físico (0 a 4)."""
        if 0 <= indice < 5:
            self.estados_leds[indice] = ligado
            if self.is_rpi and indice < len(self.leds):
                if ligado:
                    self.leds[indice].on()
                else:
                    self.leds[indice].off()

    def apagar_leds(self):
        """Apaga todos os 5 LEDs físicos."""
        for i in range(5):
            self.set_led(i, False)

    def acender_leds(self):
        """Acende todos os 5 LEDs físicos."""
        for i in range(5):
            self.set_led(i, True)

    def esta_pressionado(self, nome_botao: str) -> bool:
        """Retorna True se o botão físico estiver ativo (pressionado)."""
        return self.estados_botoes.get(nome_botao, False)

    def contato_arame_ativo(self) -> bool:
        """Retorna True se a argola encostou no arame condutor."""
        return self.estado_arame

    # Métodos utilitários para simulação no teclado/mouse em desenvolvimento
    def simular_pressionamento_botao(self, nome_botao: str, pressionado: bool):
        if not self.is_rpi and nome_botao in self.estados_botoes:
            self.estados_botoes[nome_botao] = pressionado

    def simular_toque_arame(self, tocando: bool):
        if not self.is_rpi:
            self.estado_arame = tocando

    def encerrar(self):
        """Libera os recursos de GPIO com segurança."""
        self.apagar_leds()
        if self.is_rpi:
            for led in self.leds:
                led.close()
            for btn in self.botoes.values():
                btn.close()
            if self.sensor_arame:
                self.sensor_arame.close()
        print("[HARDWARE] Recursos de GPIO finalizados.")
