"""
Gerenciador de Áudio Polifônico com Síntese Procedural de Efeitos Arcade.
Permite executar sons retro em 16-bit PCM sem depender de arquivos WAV externos obrigatórios:
- Notas musicais puras (Genius)
- Bips de largada e tiros (Quick Draw)
- Efeito sonoro de impacto e dinamômetro (Punch Meter)
- Alarme de erro e faísca elétrica (Steady Hands)
- Explosão e fanfarra de vitória (Campo Minado)
"""

import math
import struct
import pygame


class AudioManager:
    """Gerenciador e sintetizador de som procedural para console Pygame."""

    def __init__(self):
        self.inicializado = False
        self.sons = {}
        self._inicializar_mixer()

    def _inicializar_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.inicializado = True
            self._sintetizar_banco_de_efeitos()
        except Exception as e:
            print(f"[AUDIO ALERTA] Falha ao inicializar subsistema de áudio ({e}). O console operará em modo mudo.")
            self.inicializado = False

    def _gerar_onda_senoidal(self, freq: float, duracao_s: float, volume: float = 0.5) -> pygame.mixer.Sound:
        """Sintetiza uma onda sonora senoidal suave em formato 16-bit estéreo."""
        taxa = 44100
        n_amostras = int(taxa * duracao_s)
        buffer = bytearray()
        amplitude = int(32767 * volume)

        for i in range(n_amostras):
            t = i / taxa
            # Envelope simples para evitar cliques (fade-in / fade-out suave)
            fade = 1.0
            if i < 300:
                fade = i / 300
            elif i > (n_amostras - 300):
                fade = (n_amostras - i) / 300

            valor = int(amplitude * fade * math.sin(2.0 * math.pi * freq * t))
            amostra = struct.pack("<hh", valor, valor)  # Estéreo (L, R)
            buffer.extend(amostra)

        return pygame.mixer.Sound(buffer=bytes(buffer))

    def _gerar_ruido_explosao(self, duracao_s: float = 0.6, volume: float = 0.7) -> pygame.mixer.Sound:
        """Gera efeito de explosão sintetizada para o Campo Minado."""
        import random
        taxa = 44100
        n_amostras = int(taxa * duracao_s)
        buffer = bytearray()
        amplitude = int(32767 * volume)

        for i in range(n_amostras):
            decay = (1.0 - (i / n_amostras)) ** 2
            ruido = random.uniform(-1.0, 1.0)
            valor = int(amplitude * decay * ruido)
            amostra = struct.pack("<hh", valor, valor)
            buffer.extend(amostra)

        return pygame.mixer.Sound(buffer=bytes(buffer))

    def _sintetizar_banco_de_efeitos(self):
        """Pré-computa os efeitos sonoros para latência zero durante a execução."""
        try:
            # Tons do Memory Master (Dó, Mi, Sol, Dó agudo)
            self.sons["genius_0"] = self._gerar_onda_senoidal(262, 0.25, 0.45)
            self.sons["genius_1"] = self._gerar_onda_senoidal(330, 0.25, 0.45)
            self.sons["genius_2"] = self._gerar_onda_senoidal(392, 0.25, 0.45)
            self.sons["genius_3"] = self._gerar_onda_senoidal(523, 0.25, 0.45)

            # Efeitos gerais
            self.sons["menu_move"] = self._gerar_onda_senoidal(900, 0.04, 0.25)
            self.sons["menu_select"] = self._gerar_onda_senoidal(1400, 0.08, 0.35)
            self.sons["largada"] = self._gerar_onda_senoidal(1600, 0.2, 0.6)
            self.sons["tiro"] = self._gerar_onda_senoidal(880, 0.15, 0.5)
            self.sons["erro"] = self._gerar_onda_senoidal(180, 0.4, 0.6)
            self.sons["acerto"] = self._gerar_onda_senoidal(1200, 0.1, 0.35)
            self.sons["vitoria"] = self._gerar_onda_senoidal(1046, 0.4, 0.5)
            self.sons["explosao"] = self._gerar_ruido_explosao(0.7, 0.65)
            self.sons["choque"] = self._gerar_onda_senoidal(350, 0.18, 0.55)
        except Exception as e:
            print(f"[AUDIO] Erro na síntese sonora: {e}")

    def tocar(self, nome_efeito: str):
        """Dispara a reprodução de um efeito sonoro pré-carregado."""
        if not self.inicializado:
            return
        som = self.sons.get(nome_efeito)
        if som:
            som.play()

    def parar_todos(self):
        if self.inicializado:
            pygame.mixer.stop()
