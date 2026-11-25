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

    # Mapeamento BCM dos pinos da Raspberry Pi 3 B+
    PINOS_BOTOES = {
        "BT1": 17,  # Pino 11: P1 / Clicker / Start / Cor 0
        "BT2": 27,  # Pino 13: P2 / Menu Cima / Cor 1
        "BT3": 22,  # Pino 15: Menu Baixo / Start Steady / Cor 2
        "BT4": 23,  # Pino 16: Fim Steady / Cor 3
        "BT5": 24   # Pino 18: Select / Campo Minado 5 / Retorno ao Menu
    }

    PINOS_LEDS = [5, 6, 13, 19, 26]  # Pinos 29, 31, 33, 35, 37
    PINO_ARAME = 16                  # Pino 36: Contato da argola metálica

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

                # Sensor do arame com resistor de proteção
                self.sensor_arame = Button(self.PINO_ARAME, pull_up=True, bounce_time=0.04)

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
