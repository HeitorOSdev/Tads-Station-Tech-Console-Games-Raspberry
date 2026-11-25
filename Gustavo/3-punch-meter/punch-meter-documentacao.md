# PUNCH METER --- Teste de Força

## 1. Sobre o projeto

O Punch Meter é um jogo eletrônico inspirado nas máquinas de soco de parques de diversões. Desenvolvido para o projeto TECH ARCADE, utiliza um Arduino Uno e um sensor piezoelétrico para detectar impactos e atribuir uma pontuação de 0 a 1000.

O sistema funciona de maneira independente, sem interface gráfica ou computador externo. Os LEDs indicam o nível atingido e o buzzer emite sinais sonoros. O Monitor Serial permite acompanhar os valores durante os testes.

A pontuação representa a intensidade relativa do impacto captado pelo sensor, e não uma medição de força em newtons ou quilogramas-força.

## 2. Funcionamento do jogo

1.  O Arduino aguarda um impacto na superfície acolchoada.
2.  O piezoelétrico converte a vibração mecânica em um sinal elétrico.
3.  Quando a leitura analógica atinge o limite de 30, o Arduino inicia uma janela de captura de 50 ms.
4.  O maior valor registrado nessa janela é convertido em uma pontuação de 0 a 1000.
5.  Os LEDs acendem progressivamente de acordo com a pontuação.
6.  O buzzer emite sinais sonoros e uma sequência especial caso seja estabelecido um novo recorde.
7.  O resultado permanece visível por pelo menos 5 segundos, além do tempo das animações e dos sinais sonoros.
8.  Os LEDs apagam e o sistema aguarda outro impacto.

O recorde é armazenado na memória RAM e é perdido quando o Arduino é desligado ou reiniciado.

## 3. Componentes necessários

  ----------------------------------------------------------------------------------------------------------------------------------
  Componente                                                       Quantidade Função
  ---------------------------------------------- ---------------------------- ------------------------------------------------------
  Arduino Uno R3                                                            1 Controla o jogo e processa as leituras

  Piezoelétrico passivo                                                     1 Detecta impactos e vibrações

  Buzzer piezoelétrico passivo                                              1 Emite sinais sonoros

  Resistor de 1 MΩ                                                          1 Descarrega o sensor piezoelétrico

  Resistor de 10 kΩ                                                         1 Limita a corrente na entrada analógica

  Diodo Schottky BAT85 ou equivalente adequado                              2 Protege a entrada contra picos positivos e negativos

  LED verde                                                                 2 Indica os níveis 1 e 2

  LED amarelo                                                               1 Indica o nível 3

  LED laranja                                                               1 Indica o nível 4

  LED vermelho                                                              1 Indica o nível 5

  Resistor de 220 Ω                                                         5 Limita a corrente dos LEDs

  Protoboard                                                                1 Montagem do circuito

  Jumpers                                                 Conforme necessário Conexões elétricas

  Potenciômetro de 10 kΩ                                         1 (opcional) Simula o sinal do sensor no Tinkercad

  Estrutura resistente e acolchoamento                    Conforme necessário Recebe os impactos na montagem física
  ----------------------------------------------------------------------------------------------------------------------------------

## 4. Ligações dos componentes

### 4.1. Sensor piezoelétrico e proteção

  Terminal ou componente                   Conexão
  ---------------------------------------- --------------------------------------
  Terminal negativo do piezo               GND
  Terminal positivo do piezo               Uma extremidade do resistor de 10 kΩ
  Outra extremidade do resistor de 10 kΩ   A0
  Resistor de 1 MΩ                         Entre os dois terminais do piezo
  Ânodo do diodo D1                        A0
  Cátodo do diodo D1                       5V
  Ânodo do diodo D2                        GND
  Cátodo do diodo D2                       A0

O cátodo dos diodos normalmente é identificado por uma faixa no corpo do componente.

O resistor de 1 MΩ fica em paralelo com o piezo; o resistor de 10 kΩ fica em série com a entrada A0. Os diodos limitam as excursões de tensão em relação aos barramentos de alimentação.

**Atenção:** não conecte o piezo diretamente ao Arduino. Impactos podem gerar tensões positivas e negativas elevadas. O circuito apresentado é uma proteção inicial: antes de aplicar impactos fortes, verifique com um osciloscópio se a tensão e a corrente permanecem dentro dos limites dos componentes e da entrada do Arduino. Se necessário, utilize proteção adicional ou atenuação. Não aplique impactos com a placa desligada.

### 4.2. LEDs

  LED        Pino digital                Cátodo (-)
  ---------- --------------------------- ------------
  Verde 1    D2, via resistor de 220 Ω   GND
  Verde 2    D3, via resistor de 220 Ω   GND
  Amarelo    D4, via resistor de 220 Ω   GND
  Laranja    D5, via resistor de 220 Ω   GND
  Vermelho   D6, via resistor de 220 Ω   GND

Cada LED deve possuir seu próprio resistor em série. A ligação segue a ordem:

`Pino digital → resistor de 220 Ω → ânodo do LED → cátodo do LED → GND`

### 4.3. Buzzer sonoro

  Terminal       Conexão
  -------------- ---------
  Positivo (+)   D8
  Negativo (-)   GND

Utilize um buzzer piezoelétrico passivo compatível com a saída do Arduino. O código utiliza a função `tone()` para produzir diferentes frequências.

### 4.4. Alimentação

Conecte o GND do Arduino ao barramento negativo da protoboard e o 5V ao barramento positivo. Todos os componentes devem compartilhar o mesmo GND. Alimente a placa por USB ou outra fonte adequada.

## 5. Resumo dos pinos

  Pino   Função
  ------ --------------------------------------------
  A0     Entrada analógica do sensor
  D2     LED verde 1
  D3     LED verde 2
  D4     LED amarelo
  D5     LED laranja
  D6     LED vermelho
  D8     Buzzer sonoro
  5V     Alimentação e referência do diodo superior
  GND    Terra comum

## 6. Sistema de pontuação

O Arduino Uno utiliza um conversor analógico-digital de 10 bits, com leituras de 0 a 1023. O código converte o pico registrado para uma escala de 0 a 1000 utilizando `map()` e `constrain()`.

  Pontuação   Nível           LEDs acesos
  ----------- ------------- -------------
  1--200      Fraco                     1
  201--400    Moderado                  2
  401--600    Forte                     3
  601--800    Muito forte               4
  801--1000   Extremo                   5

Leituras inferiores ao limite de detecção não iniciam uma rodada. Os LEDs permanecem apagados enquanto o sistema aguarda um impacto.

## 7. Teste no Tinkercad

Como a simulação não reproduz adequadamente os impactos mecânicos sobre o piezo, utilize um potenciômetro de 10 kΩ como substituto temporário do sensor e de seu circuito de proteção. O mesmo código pode ser utilizado nas duas montagens.

  Terminal do potenciômetro   Conexão
  --------------------------- ---------
  Extremidade 1               GND
  Terminal central (cursor)   A0
  Extremidade 2               5V

1.  Monte os LEDs e o buzzer conforme as ligações anteriores.
2.  Conecte o potenciômetro no lugar do circuito do sensor.
3.  Cole o código no editor de texto do Arduino.
4.  Deixe o potenciômetro na posição correspondente a 0 V e inicie a simulação.
5.  Abra o Monitor Serial a 9600 baud.
6.  Aumente rapidamente o valor do potenciômetro para simular um impacto.
7.  Confira a pontuação, os LEDs e os sinais sonoros.
8.  Retorne o potenciômetro a zero antes de terminar a exibição do resultado, evitando disparos repetidos.

Esse teste valida a lógica do programa, mas não valida a resposta mecânica nem a proteção elétrica do sensor real. A janela de 50 ms também pode dificultar a simulação de um pico com o mouse.

## 8. Montagem física

Fixe o sensor atrás de uma superfície resistente e acolchoada, de modo que ele receba as vibrações sem contato direto com a mão do participante. Proteja os fios e a eletrônica e mantenha a estrutura estável, sem bordas expostas ou partes rígidas acessíveis na área de impacto.

Comece com toques leves e aumente gradualmente a intensidade somente após verificar a segurança elétrica e mecânica. Não incentive impactos máximos em um protótipo não validado.

## 9. Calibração e parâmetros do código

  Variável             Valor inicial Função
  ------------------ --------------- ---------------------------------------
  `limiteImpacto`                 30 Leitura mínima para iniciar a captura
  `impactoMaximo`               1023 Referência superior da pontuação
  `janelaCaptura`              50 ms Intervalo de busca pelo pico
  `tempoResultado`           5000 ms Tempo de manutenção do resultado

Ajuste o limite de detecção e a referência máxima após testes com a estrutura definitiva. Se diferentes impactos atingirem 1023, o sinal está saturando e pode exigir atenuação elétrica. A montagem, a posição do sensor e a vibração influenciam a pontuação.

O código atual utiliza esperas bloqueantes durante a apresentação do resultado e não exige que o sinal retorne abaixo do limite antes de iniciar outra captura. Assim, um sinal persistente pode provocar uma nova rodada automaticamente. A implementação também não mede a componente negativa do sinal piezoelétrico.

## 10. Identificação do projeto

-   **Nome:** Punch Meter --- Teste de Força
-   **Projeto:** TECH ARCADE
-   **Pasta:** `01-punch-meter`
-   **Plataforma:** Arduino Uno R3
-   **Linguagem:** C/C++ (Arduino)
-   **Simulador:** Tinkercad
-   **Participantes:** um por tentativa
-   **Objetivo educacional:** demonstrar sensores, leitura analógica, processamento de sinais, pontuação e controle de saídas digitais.
-   **Status:** código proposto; simulação e montagem física ainda precisam ser validadas.
