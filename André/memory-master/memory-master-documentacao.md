# MEMORY MASTER — Desafio da Memória

## 1. Sobre o projeto

O **Memory Master** é um jogo eletrônico de memória para um participante, inspirado no clássico **Genius**. O sistema apresenta uma sequência de luzes e sons, e o participante precisa memorizá-la e reproduzi-la apertando os botões na mesma ordem.

A cada rodada, uma nova cor é adicionada ao final da sequência e as luzes passam a piscar mais rápido. O Arduino controla os botões, os LEDs e o buzzer, sorteia a sequência, confere as respostas e registra a pontuação e o recorde.

## 2. Versão do código

Diferentemente do Quick Draw, o Memory Master possui **uma única versão do código**, que funciona tanto no Tinkercad quanto na montagem física. Como o jogo é para um participante e cada botão é pressionado individualmente, é possível jogar normalmente no simulador clicando nos botões com o mouse.

As principais configurações do jogo ficam reunidas no início do código e podem ser ajustadas sem alterar a lógica:

| Constante | Valor padrão | Função |
|---|---:|---|
| `TAMANHO_MAXIMO` | 32 | Número de rodadas para vencer o jogo |
| `TEMPO_RESPOSTA` | 5000 ms | Tempo máximo para apertar cada botão |
| `TEMPO_ACESO_INICIAL` | 600 ms | Duração de cada luz na primeira rodada |
| `TEMPO_ACESO_MINIMO` | 180 ms | Duração mínima de cada luz |
| `REDUCAO_POR_RODADA` | 35 ms | Quanto cada luz fica mais curta a cada rodada |
| `PAUSA_INICIAL` | 250 ms | Pausa entre luzes na primeira rodada |
| `PAUSA_MINIMA` | 80 ms | Pausa mínima entre luzes |

Para uma mostra com fila de visitantes, reduzir o `TAMANHO_MAXIMO` (por exemplo, para 15) deixa as partidas mais curtas.

## 3. Como o jogo funciona

1. Ao ligar, o sistema entra no **modo de espera**: os LEDs acendem um de cada vez, em círculo.
2. O participante aperta qualquer botão para começar. Uma animação de início é exibida.
3. O Arduino sorteia uma cor e a apresenta: o LED correspondente acende e o buzzer toca a nota daquela cor.
4. O participante repete a sequência apertando os botões. Enquanto um botão está pressionado, seu LED acende e sua nota toca.
5. Se acertar a sequência inteira, uma nova cor é adicionada ao final e a sequência completa é apresentada novamente, um pouco mais rápida.
6. O jogo termina quando o participante:
   - aperta um botão errado; ou
   - demora mais de 5 segundos para apertar o próximo botão.
7. No fim do jogo, todos os LEDs piscam com um som grave, e o Monitor Serial mostra a pontuação e o recorde.
8. Se o participante completar todas as rodadas (`TAMANHO_MAXIMO`), uma animação de vitória é exibida.
9. O sistema volta ao modo de espera para o próximo participante.

### Pontuação e recorde

- A **pontuação** é o número de rodadas completadas corretamente.
- O **recorde** é a maior pontuação alcançada desde que o Arduino foi ligado. Ao bater o recorde, o buzzer toca um som de comemoração. O recorde é perdido quando o Arduino é desligado ou reiniciado.

### Cores e sons

| Cor | Nota | Frequência |
|---|---|---:|
| Vermelho | Dó | 262 Hz |
| Verde | Mi | 330 Hz |
| Azul | Sol | 392 Hz |
| Amarelo | Dó agudo | 523 Hz |

Cada cor tem um som próprio. Isso ajuda o participante a memorizar a sequência também pela audição.

## 4. Componentes necessários

| Componente | Quantidade | Função |
|---|---:|---|
| Arduino Uno R3 | 1 | Controla o jogo |
| Pushbuttons (botões) | 4 | Um botão para cada cor |
| LEDs (vermelho, verde, azul e amarelo) | 4 | Apresentam a sequência e indicam o botão pressionado |
| Resistores de 220 Ω | 4 | Limitam a corrente dos LEDs |
| Buzzer piezo | 1 | Emite as notas e os sinais sonoros |
| Protoboard | 1 | Facilita a montagem |
| Jumpers | Conforme necessário | Realizam as conexões |

## 5. Ligações dos componentes

### 5.1. Botões

Os botões utilizam a configuração `INPUT_PULLUP`. Por isso, não precisam de resistores externos.

| Componente | Terminal | Conectar ao |
|---|---|---|
| Botão Vermelho | Um terminal | Pino digital 2 |
| Botão Vermelho | Terminal oposto | GND |
| Botão Verde | Um terminal | Pino digital 3 |
| Botão Verde | Terminal oposto | GND |
| Botão Azul | Um terminal | Pino digital 4 |
| Botão Azul | Terminal oposto | GND |
| Botão Amarelo | Um terminal | Pino digital 5 |
| Botão Amarelo | Terminal oposto | GND |

**Importante:** se forem utilizados pushbuttons de quatro pernas, coloque cada botão atravessando o vão central da protoboard. Utilize terminais de lados opostos do botão, pois as duas pernas do mesmo lado normalmente já são conectadas internamente.

**Dica:** posicione cada botão logo abaixo do LED da mesma cor. Assim, o participante associa visualmente o botão à luz.

### 5.2. LEDs

Cada LED deve possuir um resistor de 220 Ω em série.

| LED | Ânodo (perna maior), passando pelo resistor | Cátodo (perna menor) |
|---|---|---|
| LED Vermelho | Pino digital 8 | GND |
| LED Verde | Pino digital 9 | GND |
| LED Azul | Pino digital 10 | GND |
| LED Amarelo | Pino digital 11 | GND |

A ligação de cada LED deve seguir esta ordem:

`Pino digital do Arduino → resistor de 220 Ω → ânodo do LED → cátodo do LED → GND`

O resistor também pode ficar entre o cátodo e o GND, desde que esteja em série com o LED.

### 5.3. Buzzer

| Terminal do buzzer | Conectar ao |
|---|---|
| Positivo (+) | Pino digital 12 |
| Negativo (-) | GND |

### 5.4. Alimentação e GND

- Conecte o pino **GND** do Arduino ao barramento negativo da protoboard.
- Utilize esse barramento como referência de GND para os botões, LEDs e buzzer.
- Se forem usadas as duas linhas negativas da protoboard (a de cima e a de baixo), ligue uma na outra com um jumper. No circuito do Tinkercad, essa ligação fica na extremidade direita da protoboard.
- No Tinkercad, o Arduino pode ser alimentado pela própria simulação. Na montagem física, utilize uma alimentação adequada para a placa.

## 6. Resumo dos pinos do Arduino

| Pino | Componente |
|---|---|
| D2 | Botão Vermelho |
| D3 | Botão Verde |
| D4 | Botão Azul |
| D5 | Botão Amarelo |
| D8 | LED Vermelho |
| D9 | LED Verde |
| D10 | LED Azul |
| D11 | LED Amarelo |
| D12 | Buzzer |
| GND | Terra comum dos componentes |
| A0 | Entrada analógica usada para inicializar a aleatoriedade |

O pino A0 não precisa receber nenhum componente: no código, ele é lido para inicializar o gerador de números aleatórios. Assim, a sequência muda a cada vez que o Arduino é ligado.

## 7. Significado dos LEDs

- **LEDs girando em círculo:** modo de espera. Aperte qualquer botão para começar.
- **Todos os LEDs em sequência e depois acesos juntos:** animação de início da partida.
- **Um LED aceso com som:** parte da sequência sendo apresentada ou botão pressionado pelo participante.
- **Todos os LEDs piscando três vezes com som grave:** fim de jogo (erro ou tempo esgotado).
- **LEDs girando rapidamente três vezes:** vitória, todas as rodadas completadas.

## 8. Como testar no Tinkercad

1. Monte o circuito conforme as tabelas de ligação.
2. Selecione cada LED e ajuste sua cor no painel de propriedades (vermelho, verde, azul e amarelo).
3. Abra o editor de código do Arduino e selecione o modo texto.
4. Cole o código `memory-master.ino`.
5. Inicie a simulação.
6. Abra o Monitor Serial e configure a velocidade para **9600 baud**.
7. Clique em qualquer botão para começar a partida.
8. Observe a sequência e repita-a clicando nos botões na mesma ordem.
9. Acompanhe as rodadas, a pontuação e o recorde no Monitor Serial.

Para testar o fim de jogo, clique em um botão errado ou espere mais de 5 segundos sem clicar.

O Monitor Serial também mostra a sequência de cada rodada com os nomes das cores. Isso facilita a conferência durante os testes.

## 9. Observações

- Os tempos do jogo são medidos em milissegundos (`ms`).
- A sequência começa com 600 ms por luz e fica 35 ms mais curta a cada rodada, até o mínimo de 180 ms.
- O tempo máximo para apertar cada botão é de 5.000 milissegundos.
- Os botões passam por um filtro de 30 ms (*debounce*), para que um único toque não seja contado mais de uma vez.
- O Monitor Serial é utilizado para visualizar os resultados; ele não é uma interface gráfica do jogo. Na mostra, o jogo pode ser jogado apenas com os LEDs e o buzzer.
- O Monitor Serial exibe a sequência de cada rodada. Na mostra, deixe-o fora da vista do participante.
- A função `tone()` usa um timer interno do Arduino que desativa o PWM dos pinos 3 e 11. Isso não afeta o projeto, pois esses pinos são usados apenas como entrada e saída digital.
- Antes de utilizar o equipamento com o público, teste os botões, a polaridade dos LEDs, os resistores e o funcionamento do buzzer.

## 10. Identificação do projeto

**Nome:** Memory Master — Desafio da Memória  
**Plataforma:** Arduino Uno R3  
**Simulador inicial:** Tinkercad  
**Participantes:** 1 jogador  
**Objetivo:** memorizar e reproduzir sequências de luzes e sons cada vez mais longas e rápidas.
