"""
Script de Teste Rápido dos LEDs Físicos da Raspberry Pi 3 B.
Permite checar a pinagem e a ordem das cores sem precisar abrir o jogo.
Execute no terminal da Raspberry Pi com:
python3 test_leds.py
"""

import time
import sys
from core.hardware import HardwareManager

def testar():
    print("=" * 60)
    print("   TESTE DE PINAGEM DOS LEDS — TECH ARCADE CONSOLE")
    print("=" * 60)

    hw = HardwareManager()

    leds_info = [
        (0, "Vermelho", "Pino 11 / GPIO 17 (BCM)"),
        (1, "Verde",    "Pino 13 / GPIO 27 (BCM)"),
        (2, "Azul",     "Pino 15 / GPIO 22 (BCM)"),
        (3, "Amarelo",  "Pino 16 / GPIO 23 (BCM)")
    ]

    print("\n[1/2] Testando cada LED individualmente por 1.5 segundo:\n")
    for idx, cor, pino in leds_info:
        print(f" -> Acendendo LED {idx + 1} ({cor}) no {pino}...")
        hw.set_led(idx, True)
        time.sleep(1.5)
        hw.set_led(idx, False)
        time.sleep(0.3)

    print("\n[2/2] Piscando todos os 4 LEDs juntos (3 vezes):\n")
    for _ in range(3):
        hw.acender_leds()
        time.sleep(0.4)
        hw.apagar_leds()
        time.sleep(0.3)

    hw.encerrar()
    print("\n[CONCLUÍDO] Teste finalizado! Se algum LED não acendeu, verifique a perna longa no pino e a perna curta no GND.")

if __name__ == "__main__":
    testar()
