# Perfect Time — Desafio de Percepção do Tempo

Projeto 13 do Tech Arcade, desenvolvido com Arduino para explorar a percepção temporal de forma lúdica, utilizando o mínimo de componentes eletrônicos.

## 1. Objetivo

O jogador deve estimar mentalmente cinco segundos, sem consultar um relógio. Quanto menor a diferença entre o tempo registrado e o tempo ideal, maior a pontuação.

O jogo funciona de forma independente, sem computador, display, buzzer ou sensores adicionais. O Monitor Serial é utilizado apenas para consultar resultados detalhados e realizar testes.

## 2. Funcionamento

1. Os dois LEDs piscam lentamente enquanto aguardam um jogador.
2. O jogador pressiona o botão para iniciar a contagem. O LED verde acende.
3. O jogador solta o botão e estima mentalmente cinco segundos.
4. O jogador pressiona novamente o botão para encerrar a contagem.
5. O Arduino calcula a diferença absoluta em relação ao tempo ideal e apresenta a classificação por meio dos LEDs.
6. Caso seja obtido um novo recorde, os dois LEDs piscam juntos três vezes.
7. Após as sinalizações e uma espera de cinco segundos, o jogo retorna ao estado inicial.

Caso não haja um segundo pressionamento dentro do limite de 30 segundos, a tentativa é encerrada sem pontuação.

## 3. Materiais necessários

| Componente | Quantidade | Função |
|---|---:|---|
| Arduino Uno R3 | 1 | Controle do jogo e medição do tempo |
| Push button | 1 | Iniciar e encerrar a contagem |
| LED verde | 1 | Indicar contagem e resultados positivos |
| LED vermelho | 1 | Indicar resultados de menor precisão |
| Resistor de 220 Ω | 2 | Limitar a corrente dos LEDs |
| Protoboard | 1 | Montagem do circuito |
| Jumpers | Conforme necessário | Conexões elétricas |
| Cabo USB e fonte compatível | 1 conjunto | Alimentação e programação |
| Base ou caixa | Opcional | Fixação e proteção da montagem física |

## 4. Ligações elétricas

| Componente | Ligação |
|---|---|
| Botão | D2 e GND |
| LED verde | D5, resistor de 220 Ω, ânodo; cátodo ao GND |
| LED vermelho | D6, resistor de 220 Ω, ânodo; cátodo ao GND |

```text
D2 ── Botão ── GND
D5 ── Resistor 220 Ω ── LED verde (+ → −) ── GND
D6 ── Resistor 220 Ω ── LED vermelho (+ → −) ── GND
```

O botão utiliza `INPUT_PULLUP`: quando solto, a leitura é `HIGH`; quando pressionado, é `LOW`. Não é necessário resistor externo para o botão. Em botões de quatro terminais, utilize contatos eletricamente distintos, que se conectam somente ao pressionar.

## 5. Como construir

1. Com o Arduino desligado, conecte seu GND ao barramento negativo da protoboard.
2. Posicione o botão sobre a divisão central da protoboard e conecte seus contatos ao D2 e ao GND.
3. Insira os dois LEDs, observando a polaridade: a perna maior normalmente é o ânodo e a menor é o cátodo.
4. Conecte o D5 ao ânodo do LED verde por meio de um resistor de 220 Ω.
5. Repita a ligação para o LED vermelho utilizando D6 e outro resistor de 220 Ω.
6. Conecte os dois cátodos ao GND comum.
7. Carregue o código `perfect_time.ino` no Arduino e teste o circuito.
8. Opcionalmente, fixe o circuito em uma caixa ou base, deixando o botão e os LEDs acessíveis. Identifique o objetivo: “Acerte os 5 segundos”.

Utilize alimentação USB ou outra fonte compatível com o Arduino. Evite curtos-circuitos e proteja as conexões durante o uso pelo público.

## 6. Pontuação e classificação

O erro é a diferença absoluta entre o tempo medido e 5.000 ms.

```text
Erro = |tempo registrado − 5000|
Pontuação = 1000 − min(erro, 1000)
```

Cada milissegundo de diferença desconta um ponto, até o mínimo de zero.

| Erro | Classificação | Sinalização |
|---|---|---|
| 0–100 ms | Perfeito | Verde pisca 5 vezes rapidamente |
| 101–250 ms | Excelente | Verde pisca 3 vezes |
| 251–500 ms | Bom | Verde acende por 1 segundo |
| 501–1000 ms | Regular | Vermelho pisca 2 vezes |
| Acima de 1000 ms | Ruim | Vermelho pisca 5 vezes rapidamente |
| Novo recorde | Menor erro registrado | Ambos piscam 3 vezes, após a classificação |

Exemplo: um tempo de 5,120 segundos produz erro de 120 ms, pontuação de 880 e classificação Excelente.

O recorde corresponde ao menor erro absoluto, não necessariamente ao menor tempo. A primeira tentativa válida estabelece o recorde inicial.

## 7. Simulação no Tinkercad

1. Crie um circuito e adicione o Arduino Uno, a protoboard, o botão, os LEDs e os resistores.
2. Realize as ligações descritas anteriormente.
3. Abra **Código**, selecione o modo **Texto** e cole o conteúdo de `perfect_time.ino`.
4. Inicie a simulação e abra o Monitor Serial (9600 baud).
5. Pressione e solte o botão; aguarde aproximadamente cinco segundos e pressione novamente.
6. Confira o tempo, o erro, a pontuação, a classificação e o recorde.
7. Repita com tempos menores e maiores que cinco segundos para testar as sinalizações.
8. Teste também uma tentativa abandonada, mantendo o botão solto por mais de 30 segundos após iniciar.

O mesmo código é utilizado na simulação e na montagem física.

## 8. Estrutura do código

| Função | Responsabilidade |
|---|---|
| `setup()` | Configurar pinos e comunicação serial |
| `loop()` | Executar a partida, medir o tempo e calcular resultados |
| `aguardarJogador()` | Sinalizar disponibilidade e detectar o início |
| `aguardarLiberacao()` | Aguardar a soltura do botão e aplicar uma espera de 30 ms |
| `mostrarResultado()` | Classificar o erro e sinalizar com os LEDs |
| `piscarLed()` | Piscar um LED individualmente |
| `piscarTodos()` | Piscar os dois LEDs simultaneamente |
| `apagarLeds()` | Desligar os LEDs |

### Parâmetros configuráveis

| Parâmetro | Valor padrão |
|---|---:|
| `tempoIdeal` | 5000 ms |
| `tempoResultado` | 5000 ms |
| `tempoLimite` | 30000 ms |

A medição utiliza `millis()`, sem necessidade de um relógio externo. Caso o tempo ideal seja alterado, atualize também as mensagens e instruções do jogo.

## 9. Limitações e validação

- O recorde é armazenado na RAM e perdido ao desligar ou reiniciar o Arduino.
- Os LEDs indicam a classificação; a pontuação numérica e o tempo exato são exibidos somente no Monitor Serial.
- O código utiliza esperas bloqueantes durante as sinalizações e a liberação do botão. Se o botão permanecer pressionado, a espera pela liberação pode impedir a aplicação imediata do limite de 30 segundos.
- A espera de 30 ms após a liberação auxilia no tratamento de contatos mecânicos, mas não constitui uma filtragem completa de todos os pressionamentos.
- O código e a montagem ainda precisam ser validados no Tinkercad e no protótipo físico.

## 10. Organização do repositório

```text
13-perfect-time/
├── perfect_time.ino
└── README.md
```

O arquivo `perfect_time.ino` contém o código-fonte do jogo. Este documento deve ser salvo como `README.md` na mesma pasta.
