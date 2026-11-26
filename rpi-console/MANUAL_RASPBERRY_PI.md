# GUIA PRÁTICO DEFINITIVO DE MONTAGEM E INSTALAÇÃO (100% DIGITAL)
## Tech Arcade Console — Raspberry Pi 3 B+ & Display Touch 7" (1024x600)

---

## 1. Visão Geral do Console (6 Jogos 100% Digitais)

O **Tech Arcade Console** é uma plataforma de entretenimento de alta performance, 100% digital e sem a necessidade de conversores analógicos ou chips externos complexos.

O console integra **seis jogos completos**, operando a 60 FPS com gráficos acelerados por hardware (Pygame-CE), áudio estéreo sintetizado e controle unificado por **2 Botões Físicos + Tela Touchscreen 1024x600**:

1. **Memory Master:** Desafio da memória clássico ("Genius") com 4 LEDs físicos e repetição touch.
2. **Ping Pong Arcade:** Clássico Pong para 2 jogadores (P1 vs P2) com movimento contínuo cadenciado e botões touch translúcidos.
3. **Quick Draw:** Duelo de reflexos para 2 participantes com queima de largada e medição em milissegundos.
4. **Campo Minado:** Campo clássico em grade 3x4 (12 células) com 3 minas e pistas numéricas para dedução lógica. Primeiro clique 100% seguro.
5. **Perfect Time:** Desafio de percepção temporal de 5.000 segundos com medição em microssegundos (`time.perf_counter()`).
6. **Button Frenzy:** Teste de agilidade e velocidade: maior quantidade de cliques em 10 segundos com cálculo de CPS.

---

## 2. Lista de Materiais e Componentes (Simples e Acessíveis)

> [!TIP]
> **Sobre os botões:** Agora o console necessita de apenas **2 botões físicos** (`BT1` e `BT2`) para navegar por todos os menus e jogar todas as modalidades! O jogo do arame foi descontinuado, dispensando arames e resistores adicionais.

| Item | Componente | Quantidade | Função no Console |
| :---: | :--- | :---: | :--- |
| **1** | **Raspberry Pi 3 B / 3 B+** | 1 | Processamento central, engine Pygame e áudio |
| **2** | **Display Touch 7" HDMI IPS (1024x600)** | 1 | Interface visual e tela touch |
| **3** | **Cartão MicroSD 8GB ou superior** | 1 | Armazenamento do sistema operacional e jogos |
| **4** | **Pushbuttons comuns (6x6mm, 12x12mm ou arcade)** | 2 | BT1 (Pino 29) e BT2 (Pino 31) |
| **5** | **LEDs Difusos 5mm** | 4 | 4 LEDs do Genius (Pinos 11, 13, 15, 16) |
| **6** | **Resistores para os LEDs (3.3V)** | 4 | 2x 270 Ω (Verm/Amar), 1x 220 Ω (Verde), 1x 100 Ω (Azul) |
| **7** | **Protoboard + Jumpers Macho-Fêmea** | 1 conjunto | Montagem das conexões |
| **8** | **Fonte de Alimentação 5V / 2.5A ou 3.0A (Micro-USB)** | 1 | Alimentação estável do conjunto |

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

## 8. Guia Rápido de Operação dos 6 Jogos (Sistema Otimizado para 2 Botões)

* **Navegação no Menu com 2 Botões:**
  * **BT1 (Pino Físico 29 / BCM 5):** Alterna ciclicamente para o próximo jogo no carrossel (PRÓXIMO >).
  * **BT2 (Pino Físico 31 / BCM 6):** Seleciona e inicia o jogo em destaque (JOGAR AGORA!).
  * Também é possível navegar e selecionar por toque direto na tela touch.
* **Retorno Universal ao Menu:**
  * Segurar o **BT2 por 1,5 segundos** (ou pressionar **BT1 + BT2 juntos por 1 segundo**) durante qualquer partida aborta o jogo e retorna ao menu.
  * O botão VOLTAR no topo da tela touch também permanece sempre acessível.
* **Desligamento Seguro:**
  * Toque no botão vermelho **DESLIGAR** no topo direito da tela touch do menu. No modal de confirmação: **BT1 Cancela** e **BT2 Confirma** o desligamento seguro do sistema.
* **Controles dos 6 Jogos:**
  1. **Memory Master (Genius das Cores):** Modos "COM LEDS" (padrão) e "SEM LEDS" (as cores brilham visualmente na tela, permitindo jogar apenas pelo display). Os LEDs físicos (Pinos 11, 13, 15, 16) continuam sempre ativos. Na resposta, use o seletor com 2 botões (**BT1** move o seletor entre as cores, **BT2** escolhe) ou toque direto nos quadrantes touch.
  2. **Ping Pong Arcade (Duelo 2P):** Raquetes contínuas e ritmo acelerado da bola (início dinâmico a 320 px/s e raquete a 270 px/s). O Jogador 1 (Esquerda) usa **BT1** (ou toque na metade esquerda) e o Jogador 2 (Direita) usa **BT2** (ou toque na metade direita) para inverter o sentido das raquetes.
  3. **Quick Draw (Duelo de Reação 2P):** Duelo rápido de faroeste. O Jogador 1 usa **BT1** e o Jogador 2 usa **BT2** (ou toque em cada lado da tela).
  4. **Campo Minado (Dedução Lógica Clássica):** Grade 3x4 (12 células) com 3 minas e pistas numéricas vizinhas (1, 2, 3...). O primeiro clique é sempre seguro e revela caminhos em cadeia. **BT1** move o cursor luminoso e **BT2** abre a célula selecionada (ou toque direto na tela).
  5. **Perfect Time (Tempo Perfeito 5.000s):** Pressione **BT1** ou **BT2** para iniciar a contagem cega e pressione novamente para parar o cronômetro com precisão de microssegundos.
  6. **Button Frenzy (Frenesi de Cliques em 10s):** Teste de agilidade. Pressione **BT1** ou **BT2** (ou alterne rapidamente os dedos entre os dois botões físicos) para obter a maior quantidade de cliques em 10 segundos.
