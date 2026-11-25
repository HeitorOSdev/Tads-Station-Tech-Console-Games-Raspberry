# 07 — Memory Collor

## 1. Apresentação

O Memory Collor (originalmente Memory Master) é um jogo de memória desenvolvido para o projeto Tech Arcade. O objetivo é memorizar e reproduzir sequências de luzes utilizando dois botões.

O projeto utiliza uma quantidade mínima de componentes e funciona de forma independente, sem computador, display, buzzer ou sensores adicionais. O mesmo código pode ser utilizado no Tinkercad e na montagem física. O Monitor Serial é opcional e serve para acompanhar a pontuação e o recorde durante os testes.

## 2. Funcionamento do jogo

1. Os dois LEDs piscam lentamente enquanto aguardam um jogador.
2. O participante pressiona qualquer botão para iniciar e o solta.
3. O Arduino apresenta uma sequência aleatória de luzes verdes e vermelhas.
4. O participante reproduz a sequência pressionando os botões correspondentes, na mesma ordem.
5. A cada rodada correta, os dois LEDs piscam uma vez e uma nova cor é acrescentada à sequência anterior.
6. A velocidade de apresentação aumenta progressivamente.
7. Caso o participante erre, pressione os dois botões simultaneamente ou exceda o tempo de resposta, a partida termina.
8. Os dois LEDs piscam rapidamente cinco vezes para sinalizar a derrota. Após a apresentação do resultado, o jogo volta a aguardar um participante.

O limite é de 100 rodadas. Ao completar todas elas, os LEDs piscam cinco vezes lentamente, indicando a conclusão do jogo.

### Exemplo de sequência

| Rodada | Sequência possível |
| --- | --- |
| 1 | Verde |
| 2 | Verde, Vermelho |
| 3 | Verde, Vermelho, Vermelho |
| 4 | Verde, Vermelho, Vermelho, Verde |

## 3. Materiais necessários

| Componente | Quantidade |
| --- | ---: |
| Arduino Uno R3 | 1 |
| Push button | 2 |
| LED verde | 1 |
| LED vermelho | 1 |
| Resistor de 220 Ω | 2 |
| Protoboard | 1 |
| Jumpers | Conforme necessário |
| Cabo USB para alimentação e programação | 1 |
| Base ou caixa para montagem física | Opcional |

## 4. Ligações elétricas

| Componente | Pino do Arduino | Ligação |
| --- | --- | --- |
| Botão verde | D2 | Entre D2 e GND |
| Botão vermelho | D3 | Entre D3 e GND |
| LED verde | D5 | D5 → resistor de 220 Ω → ânodo; cátodo → GND |
| LED vermelho | D6 | D6 → resistor de 220 Ω → ânodo; cátodo → GND |

### Botões

Os botões utilizam `INPUT_PULLUP`, portanto não precisam de resistores externos. Quando soltos, a leitura é `HIGH`; quando pressionados, a leitura é `LOW`.

Em botões de quatro terminais, utilize dois terminais que não estejam permanentemente interligados. Posicione os botões sobre a divisão central da protoboard.

### LEDs

Cada LED deve possuir seu próprio resistor de 220 Ω em série. A perna maior normalmente corresponde ao ânodo (+), e a menor ao cátodo (-). Todos os componentes devem compartilhar o GND do Arduino.

```text
D2 ── Botão verde ───── GND
D3 ── Botão vermelho ── GND
D5 ── 220 Ω ── LED verde ───── GND
D6 ── 220 Ω ── LED vermelho ── GND
```

## 5. Como construir

1. Com o Arduino desligado, conecte seu GND ao barramento negativo da protoboard.
2. Posicione os dois botões e faça as ligações aos pinos D2 e D3 e ao GND.
3. Posicione os LEDs próximos aos respectivos botões.
4. Conecte os resistores em série com os LEDs e faça as ligações aos pinos D5 e D6.
5. Confira a polaridade dos LEDs e todas as conexões.
6. Conecte o Arduino ao computador e carregue o código `.ino` do projeto.
7. Teste os botões, as sequências e as sinalizações de acerto e erro.
8. Para a montagem definitiva, fixe os componentes em uma base ou caixa, identifique os botões pelas cores correspondentes e proteja as conexões.
9. Alimente o Arduino por USB com uma fonte adequada para operar sem computador.

## 6. Simulação no Tinkercad

1. Crie um circuito no Tinkercad Circuits.
2. Adicione os componentes eletrônicos da lista.
3. Realize as ligações conforme a tabela de pinos.
4. Abra a opção **Código** e selecione o modo **Texto**.
5. Cole o código do projeto e inicie a simulação.
6. Abra o Monitor Serial (9600 baud) para acompanhar os resultados.
7. Pressione qualquer botão, aguarde a apresentação das luzes e reproduza a sequência.
8. Teste uma resposta correta, uma incorreta e a ausência de resposta por dez segundos.

Não é necessário modificar o código para a montagem física. Nenhuma ação válida exige pressionar dois botões simultaneamente, permitindo jogar no simulador com apenas um mouse.

## 7. Pontuação e dificuldade

Cada rodada concluída vale um ponto. Se o jogador errar na quinta rodada, por exemplo, receberá quatro pontos.

| Rodada | Duração de cada luz |
| ---: | ---: |
| 1 | 585 ms |
| 5 | 525 ms |
| 10 | 450 ms |
| 20 | 300 ms |
| 30 em diante | 200 ms |

O intervalo entre luzes é de 250 ms. O jogador possui dez segundos para iniciar cada resposta. O código aguarda a liberação do botão antes de aceitar a próxima entrada.

O recorde corresponde à maior quantidade de rodadas concluídas desde que o Arduino foi ligado.

## 8. Sinalizações visuais

| Estado | Sinalização |
| --- | --- |
| Aguardando jogador | Dois LEDs piscam lentamente |
| Apresentação da sequência | LEDs acendem individualmente conforme a sequência |
| Resposta | LED correspondente ao botão pressionado acende brevemente após sua liberação |
| Rodada correta | Dois LEDs piscam uma vez |
| Derrota | Dois LEDs piscam rapidamente cinco vezes |
| Jogo completado | Dois LEDs piscam lentamente cinco vezes |

## 9. Organização do código

| Função | Responsabilidade |
| --- | --- |
| `setup()` | Configura pinos, comunicação serial e gerador aleatório |
| `loop()` | Controla as partidas e acrescenta novas cores |
| `aguardarJogador()` | Aguarda o início da partida |
| `mostrarSequencia()` | Apresenta a sequência de LEDs |
| `verificarResposta()` | Compara as respostas com a sequência armazenada |
| `lerBotao()` | Identifica o botão pressionado e controla o tempo de resposta |
| `aguardarLiberacao()` | Aguarda a liberação dos botões e reduz efeitos de rebote |
| `finalizarPartida()` | Registra a pontuação e sinaliza o resultado |
| `piscarTodos()` | Pisca os dois LEDs |
| `apagarLeds()` | Desliga os LEDs |

### Parâmetros configuráveis

- `tamanhoMaximo`: quantidade máxima de rodadas (100).
- `tempoResposta`: tempo limite para iniciar cada resposta (10.000 ms).
- `tempoLed`: duração da apresentação de cada luz, reduzida conforme a rodada, até o mínimo de 200 ms.

## 10. Limitações e cuidados

- A pontuação numérica e o recorde são exibidos somente no Monitor Serial; o jogo funciona sem ele.
- O recorde é armazenado na memória RAM e perdido ao desligar ou reiniciar o Arduino.
- Manter um botão pressionado pode bloquear temporariamente o jogo, pois o código aguarda sua liberação.
- Não conecte LEDs diretamente aos pinos sem resistores.
- A validação no Tinkercad e na montagem física deve ser realizada antes da utilização em eventos.

## 11. Estrutura sugerida do repositório

```text
07-memory-collor/
├── memory_collor.ino
└── README.md
```

O arquivo `.ino` contém o código do jogo e o `README.md` contém sua documentação.
