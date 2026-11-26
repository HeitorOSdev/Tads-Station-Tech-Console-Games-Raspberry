# GUIA PRÁTICO DEFINITIVO DE MONTAGEM E INSTALAÇÃO (100% DIGITAL)
## Tech Arcade Console — Raspberry Pi 3 B+ & Display Touch 7" (1024x600)

---

## 1. Visão Geral do Console (7 Jogos 100% Digitais)

O **Tech Arcade Console** é uma plataforma de entretenimento de alta performance, 100% digital e sem a necessidade de conversores analógicos ou chips externos complexos.

O console integra **sete jogos completos**, operando a 60 FPS com gráficos acelerados por hardware (Pygame-CE), áudio estéreo sintetizado e controle unificado por **5 Botões Físicos + Tela Touchscreen 1024x600**:

1. **Memory Master:** Desafio da memória clássico ("Genius") com 4 cores sonoras e visuais progressivas.
2. **Quick Draw:** Duelo de reflexos para 2 participantes com tela dividida, queima de largada e medição em milissegundos.
3. **Steady Hands:** Pista de arame condutor com proteção contra estática (ESD), 3 vidas, cronômetro de precisão e alarme.
4. **Campo Minado:** 5 cápsulas táteis com 2 minas sorteadas e efeitos visuais/sonoros de explosão e vitória.
5. **Perfect Time:** Desafio de percepção temporal de 5.000 segundos com medição em microssegundos (`time.perf_counter()`).
6. **Button Frenzy:** Teste de agilidade e velocidade: maior quantidade de cliques em 10 segundos com cálculo de CPS.
7. **Ping Pong Arcade:** Clássico Pong para 2 jogadores (P1 vs P2) com física real, aceleração da bola e disputa até 5 pontos.

---

## 2. Lista de Materiais e Componentes (Simples e Acessíveis)

> [!TIP]
> **Sobre as cores dos botões:** Os botões físicos **NÃO precisam ser coloridos**! Quaisquer 5 pushbuttons normais pretos ou da mesma cor funcionam perfeitamente, pois a tela Touch e os LEDs já realizam toda a identificação visual.

| Item | Componente | Quantidade | Função no Console |
| :---: | :--- | :---: | :--- |
| **1** | **Raspberry Pi 3 B+** | 1 | Processamento central, engine Pygame e áudio |
| **2** | **Display Touch 7" HDMI IPS (1024x600)** | 1 | Interface visual e tela touch capacitiva/resistiva |
| **3** | **Cartão MicroSD 8GB, 16GB ou 32GB** | 1 | Armazenamento do sistema operacional e jogos |
| **4** | **Pushbuttons comuns (6x6mm, 12x12mm ou arcade)** | 5 | BT1, BT2, BT3, BT4 e BT5 *(qualquer cor serve)* |
| **5** | **LEDs Difusos 5mm** | 5 | 1 Vermelho, 1 Verde, 1 Azul, 1 Amarelo, 1 Laranja |
| **6** | **Resistores para os LEDs (3.3V)** | 5 | 3x 270 Ω (Verm/Amar/Laranja), 1x 220 Ω (Verde), 1x 100 Ω (Azul) |
| **7** | **Resistor de Proteção ESD** | 1 | 1x 1 kΩ (em série com a pista de arame) |
| **8** | **Arame Rígido + Argola Metálica** | 1 conjunto | Pista do jogo *Steady Hands* |
| **9** | **Protoboard + Jumpers Macho-Fêmea** | 1 conjunto | Montagem das conexões |
| **10**| **Fonte de Alimentação 5V / 3.0A (Micro-USB)** | 1 | Alimentação estável do conjunto |

---

## 3. Tabela de Pinagem Unificada dos 40 Pinos da Raspberry Pi 3 B+

> [!CAUTION]
> **SEGURANÇA ELÉTRICA (3.3V):**
> Todos os botões utilizam `INPUT_PULLUP` interno da Raspberry Pi e fecham contato apenas no **GND**. Nunca ligue nenhum pino de GPIO na linha de 5V.

| Pino Físico | Identificador BCM | Conexão Externa | Função Compartilhada Unificada (7 Jogos) |
| :---: | :---: | :--- | :--- |
| **Pino 02** | **5V Power** | Alimentação da Tela Touch (Micro-USB) | Fornece 5V estáveis para o backlight da tela |
| **Pino 06 ou 09** | **GND** | Barramento Negativo (GND Comum) | Referência de 0V compartilhada na protoboard |
| **Pino 11** | **GPIO 17** *(GPIO 0 no diagrama)* | **LED 1 (Vermelho - 270Ω)** | Genius L1 (Dó), P1 QuickDraw, Vida 1 Steady, Gol P1 PingPong |
| **Pino 13** | **GPIO 27** *(GPIO 2 no diagrama)* | **LED 2 (Verde - 220Ω)** | Genius L2 (Mi), P2 QuickDraw, Vida 2 Steady, Gol P2 PingPong |
| **Pino 15** | **GPIO 22** *(GPIO 3 no diagrama)* | **LED 3 (Azul - 100Ω)** | Genius L3 (Sol), Partida QuickDraw, Vida 3 Steady, Minado 3 |
| **Pino 16** | **GPIO 23** *(GPIO 4 no diagrama)* | **LED 4 (Amarelo - 270Ω)** | Genius L4 (Dó Agudo), Partida Steady Hands, Minado 4 |
| **Pino 37** | **GPIO 26** | **LED 5 (Laranja - 270Ω)** | Alerta de Contato no Arame Steady Hands, Minado 5 |
| **Pino 29** | **GPIO 5** | **Botão 1 (BT1 - Esquerda Sup.)** | P1 QuickDraw, P1 PingPong Cima, Genius 0 (Vermelho), Frenzy, Perfect Time, Minado 1 |
| **Pino 31** | **GPIO 6** | **Botão 2 (BT2 - Esquerda Inf.)** | P1 PingPong Baixo, Genius 1 (Verde), Menu Anterior, Minado 2 |
| **Pino 33** | **GPIO 13** | **Botão 3 (BT3 - Direita Sup.)** | P2 PingPong Cima, Genius 2 (Azul), Início Steady Hands, Menu Próximo, Minado 3 |
| **Pino 35** | **GPIO 19** | **Botão 4 (BT4 - Direita Inf.)** | P2 QuickDraw, P2 PingPong Baixo, Genius 3 (Amarelo), Fim Steady Hands, Minado 4 |
| **Pino 18** | **GPIO 24** | **Botão 5 (BT5 - Centro Arcade)** | Menu Confirmar/Jogar, Minado 5, **Botão de Pânico (Segurar 1.5s sai para o menu)** |
| **Pino 36** | **GPIO 16** | **Pista de Arame (Mão Firme)** | Entrada de toque com **resistor de 1 kΩ em série** *(Argola no GND)* |

---

## 4. Passo a Passo Completo de Instalação (Do Zero)

### 4.1. Gravar o Sistema Operacional no Cartão MicroSD (Pelo PC)
1. Baixe o [Raspberry Pi Imager](https://www.raspberrypi.com/software/) no seu computador.
2. Abra o programa e selecione:
   * **Dispositivo:** `Raspberry Pi 3`
   * **Sistema Operacional:** `Raspberry Pi OS (32-bit)` *(versão padrão com desktop)*
   * **Armazenamento:** Selecione o seu cartão MicroSD (8GB ou superior)
3. Clique em **Próximo** e configure as opções do sistema:
   * Usuário: `pi` (ou seu nome de preferência)
   * Senha: crie sua senha
   * Wi-Fi: configure o SSID e senha da sua rede local
   * Habilite o serviço **SSH** para acesso remoto
4. Grave o cartão MicroSD e aguarde a verificação final.

### 4.2. Configurar a Resolução 1024x600 da Tela Touch no `config.txt`
Ainda com o cartão MicroSD conectado no computador:
1. Abra a partição chamada **`boot`** (ou **`bootfs`**).
2. Abra o arquivo **`config.txt`** com o Bloco de Notas ou VS Code.
3. No final do arquivo, adicione:
   ```ini
   # ===================================================
   # CONFIGURACAO TELA TOUCH 7" HDMI IPS (1024x600)
   # ===================================================
   hdmi_force_hotplug=1
   max_usb_current=1
   hdmi_group=2
   hdmi_mode=87
   hdmi_cvt 1024 600 60 6 0 0 0
   hdmi_drive=2
   ```
4. Salve o arquivo e ejete o cartão com segurança.

---

## 5. Montagem Física na Bancada (Circuito 100% Digital)

Com a Raspberry Pi **desligada**:

1. **Montagem do Display:**
   * Parafuse a Raspberry Pi 3 B+ nos espaçadores de latão atrás da tela de 7".
   * Conecte o adaptador HDMI rígido (ou cabo) entre a saída da Pi e a entrada da tela.
   * Conecte o cabo Micro-USB da porta USB da Pi para a porta marcada como **Touch** no display (fornece energia e dados do toque).
2. **Montagem da Protoboard:**
   * Conecte o Pino 6 da Pi (GND) na linha negativa (-) da protoboard.
   * **Os 5 Botões (BT1 a BT5):**
     * Conecte um lado de cada botão na linha **GND**.
     * Conecte o outro lado aos Pinos **11 (BT1)**, **13 (BT2)**, **15 (BT3)**, **16 (BT4)** e **18 (BT5)**.
   * **Os 5 LEDs:**
     * Conecte o cátodo (perna menor) de todos os LEDs na linha **GND**.
     * Conecte em série com o ânodo (perna maior):
       * LED 1 (Vermelho): Resistor de 270 Ω $\rightarrow$ **Pino 29 (GPIO 5)**
       * LED 2 (Verde): Resistor de 220 Ω $\rightarrow$ **Pino 31 (GPIO 6)**
       * LED 3 (Azul): Resistor de 100 Ω $\rightarrow$ **Pino 33 (GPIO 13)**
       * LED 4 (Amarelo): Resistor de 270 Ω $\rightarrow$ **Pino 35 (GPIO 19)**
       * LED 5 (Laranja): Resistor de 270 Ω $\rightarrow$ **Pino 37 (GPIO 26)**
   * **Pista de Arame (Steady Hands):**
     * Conecte a argola metálica móvel ao **GND** com fio flexível.
     * Conecte o arame rígido a um terminal do resistor de **1 kΩ**.
     * Conecte o outro terminal do resistor ao **Pino 36 (GPIO 16)**.

---

## 6. Instalação e Execução dos Jogos na Raspberry Pi

1. Insira o cartão MicroSD e ligue a fonte de 5V / 3.0A.
2. Abra o terminal e instale as dependências:
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-pygame python3-gpiozero
   ```
3. Navegue até a pasta do projeto `tech-arcade/rpi-console`:
   ```bash
   cd ~/tech-arcade/rpi-console
   pip3 install -r requirements.txt --break-system-packages
   ```
4. Teste a execução manual:
   ```bash
   python3 main.py
   ```

---

## 7. Configuração do Modo Console Kiosk (Auto-Start no Boot)

Para que o console ligue direto no menu do console sem exibir a área de trabalho do Linux:

1. Copie o arquivo de serviço systemd:
   ```bash
   sudo cp tech-arcade.service /etc/systemd/system/
   ```
2. Habilite o serviço:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable tech-arcade.service
   ```
3. Inicie o console de imediato:
   ```bash
   sudo systemctl start tech-arcade.service
   ```

---

## 8. Guia Rápido de Operação dos 7 Jogos

* **Navegação no Menu:** Botão **BT2** (Anterior), **BT3** (Próximo) e **BT5** (Confirmar/Entrar). Também pode usar o toque direto na tela.
* **Ocultação Inteligente de Toque:** Ao acionar qualquer botão físico, os botões virtuais da tela somem automaticamente para uma experiência arcade autêntica (com exceção do Jogo da Memória, botão `VOLTAR` e botão `DESLIGAR`).
* **Desligamento Seguro por Toque:** Botão vermelho **DESLIGAR** no topo direito da tela touch do menu. Ao tocar nele, uma janela de confirmação surge; confirmando, o sistema desliga o hardware e o sistema operacional com segurança sem risco de corromper o MicroSD.
* **Botão Universal de Pânico:** Segurar o **Botão 5 por 1,5 segundos** em qualquer jogo aborta a partida e retorna ao menu.
* **Controles dos Jogos:**
  1. **Memory Master:** A sequência pisca exclusivamente nos 4 LEDs físicos (Vermelho, Verde, Azul, Amarelo). A tela funciona como painel de status e interface touch (BT1..BT4 ou quadrantes coloridos).
  2. **Quick Draw:** Duelo 2P. P1 usa BT1 (esquerda) e P2 usa BT4 (direita - ergonômico, cada jogador em uma ponta).
  3. **Steady Hands:** BT3 (Início), BT4 (Fim) e pista de arame condutor (GPIO 16).
  4. **Campo Minado:** Botões BT1..BT5 ou toque direto nas 5 cápsulas.
  5. **Perfect Time:** BT1 inicia e para o cronômetro com latência zero (disparo instantâneo no toque ou clique).
  6. **Button Frenzy:** BT1 ou tamborilar de dedos na tela por 10 segundos com registro ágil de CPS.
  7. **Ping Pong Arcade:** Duelo 2P de Ping Pong até 5 pontos:
     * **Movimento Contínuo:** As raquetes se movimentam sozinhas e rebatem automaticamente nas bordas superior e inferior.
     * **Controle por Inversão:** Um toque no botão físico (**BT1** ou **BT2**) inverte instantaneamente a direção da raquete do Jogador 1 (Esquerda). Um toque em **BT3** ou **BT4** inverte a do Jogador 2 (Direita).
     * **Controles Touch Translúcidos:** Áreas touch semitransparentes no centro de cada campo permitem que os jogadores toquem na tela para inverter o sentido das raquetes sem obstruir a visão da bola.
