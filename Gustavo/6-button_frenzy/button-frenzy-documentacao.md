# 14 — Button Frenzy: Desafio de Velocidade

## 1. Apresentação

O Button Frenzy é um jogo do projeto Tech Arcade que desafia o participante a pressionar um botão o maior número de vezes possível em dez segundos. O objetivo é explorar a agilidade dos dedos e a interação com sistemas embarcados.

O projeto funciona sem computador, display, buzzer ou sensores adicionais. Utiliza o mesmo circuito do Perfect Time, alterando apenas o código.

## 2. Funcionamento e regras

1. Os dois LEDs piscam lentamente enquanto aguardam um jogador.
2. O participante pressiona e solta o botão para iniciar.
3. O LED vermelho pisca três vezes, em uma contagem regressiva de três segundos.
4. O LED verde acende, indicando o início da partida.
5. Durante dez segundos, cada novo pressionamento válido vale um ponto. Manter o botão pressionado não gera pontos adicionais.
6. O LED vermelho acende por um segundo ao término da partida.
7. O Arduino verifica o recorde e apresenta a pontuação por meio dos LEDs.
8. Após a apresentação e uma pausa de cinco segundos, o sistema aguarda a liberação do botão e retorna ao estado inicial.

## 3. Materiais necessários

| Componente | Quantidade | Função |
|---|---:|---|
| Arduino Uno R3 | 1 | Controle do jogo |
| Push button | 1 | Entrada do jogador |
| LED verde | 1 | Partida ativa e dezenas da pontuação |
| LED vermelho | 1 | Contagem regressiva, encerramento e unidades |
| Resistor de 220 Ω | 2 | Limitação da corrente dos LEDs |
| Protoboard | 1 | Montagem do circuito |
| Jumpers | Conforme necessário | Conexões elétricas |
| Cabo USB e fonte USB de 5 V | 1 de cada | Programação e alimentação |
| Base ou caixa | Opcional | Fixação e proteção dos componentes |

## 4. Ligações elétricas

| Componente | Conexão |
|---|---|
| Botão | D2 e GND |
| LED verde | D5, resistor de 220 Ω, ânodo do LED; cátodo ao GND |
| LED vermelho | D6, resistor de 220 Ω, ânodo do LED; cátodo ao GND |

```text
D2 ---- Botão ---------------- GND
D5 ---- 220 Ω ---- LED verde -- GND
D6 ---- 220 Ω ---- LED vermelho GND
```

O botão utiliza `INPUT_PULLUP`: solto corresponde a `HIGH` e pressionado corresponde a `LOW`. Não é necessário resistor externo para o botão. Em botões de quatro terminais, utilize dois terminais que não estejam permanentemente interligados. Todos os componentes compartilham o GND.

## 5. Construção física

1. Desligue a alimentação do Arduino antes de montar o circuito.
2. Conecte o GND do Arduino ao barramento negativo da protoboard.
3. Posicione o botão sobre a divisão central da protoboard e conecte-o ao D2 e ao GND.
4. Instale os LEDs, observando a polaridade: normalmente a perna maior é o ânodo e a menor é o cátodo.
5. Instale um resistor de 220 Ω em série com cada LED e realize as conexões da tabela.
6. Conecte o Arduino ao computador e carregue o arquivo `button_frenzy.ino` pela Arduino IDE.
7. Teste os componentes e execute uma partida completa.
8. Para a exposição, fixe o botão e os LEDs em uma base ou caixa, deixando o botão acessível e protegendo os fios. Utilize um botão resistente a pressionamentos repetidos.
9. Alimente o Arduino por USB para operar sem computador.

## 6. Pontuação e sinalizações

Cada pressionamento válido vale um ponto. A velocidade média é calculada dividindo a pontuação por dez segundos.

| Sinalização | Significado |
|---|---|
| Ambos piscando lentamente | Aguardando jogador |
| Vermelho piscando três vezes | Contagem regressiva |
| Verde aceso | Partida em andamento |
| Vermelho aceso por um segundo | Tempo esgotado |
| Ambos piscando três vezes | Novo recorde |
| Piscadas verdes após o resultado | Grupos de dez pontos |
| Piscadas vermelhas após o resultado | Unidades restantes |

Por exemplo, 37 pontos são apresentados como três piscadas verdes, uma pausa de um segundo e sete piscadas vermelhas. Cada piscada verde representa dez pontos; cada vermelha representa um ponto. Uma pontuação de zero não gera piscadas de pontuação.

### Classificação sugerida

| Pontuação | Classificação |
|---:|---|
| 0–20 | Iniciante |
| 21–40 | Intermediário |
| 41–60 | Rápido |
| 61–80 | Muito rápido |
| 81–100 | Especialista |
| Acima de 100 | Lendário |

As faixas são sugestões lúdicas para a exposição, não referências científicas, e não estão implementadas no código.

## 7. Simulação no Tinkercad

1. Crie um circuito com os componentes indicados ou reutilize o circuito do Perfect Time.
2. Confira as ligações conforme a tabela de pinos.
3. Abra a opção Código, selecione o modo Texto e cole o conteúdo de `button_frenzy.ino`.
4. Inicie a simulação e abra o Monitor Serial (9600 baud).
5. Pressione e solte o botão para iniciar. Aguarde a contagem regressiva.
6. Durante os dez segundos, clique repetidamente no botão.
7. Confira a pontuação no Monitor Serial e nas piscadas dos LEDs.
8. Teste também um pressionamento prolongado, uma partida sem pressionamentos e uma nova tentativa que supere o recorde.

O mesmo código é utilizado na simulação e na montagem física.

## 8. Estrutura do código

| Função | Responsabilidade |
|---|---|
| `setup()` | Configura pinos e comunicação serial |
| `loop()` | Executa o ciclo do jogo |
| `aguardarJogador()` | Aguarda o início da partida |
| `contagemRegressiva()` | Sinaliza os três segundos de preparação |
| `executarPartida()` | Cronometra e contabiliza pressionamentos válidos |
| `mostrarResultado()` | Exibe pontuação, velocidade média e recorde |
| `mostrarPontuacao()` | Converte a pontuação em piscadas |
| `piscarLed()` e `piscarTodos()` | Controlam as sinalizações luminosas |
| `aguardarLiberacao()` | Aguarda a soltura do botão |
| `apagarLeds()` | Desliga os LEDs |

### Parâmetros configuráveis

| Constante | Valor padrão | Descrição |
|---|---:|---|
| `duracaoPartida` | 10000 ms | Duração da partida |
| `tempoResultado` | 5000 ms | Pausa após a apresentação do resultado |
| `debounce` | 20 ms | Intervalo mínimo de estabilidade da leitura |

O debounce reduz a contagem indevida causada pelas oscilações dos contatos mecânicos. Tanto o pressionamento quanto a liberação precisam ser reconhecidos como estados estáveis. Se a duração da partida for alterada, ajuste também o cálculo da velocidade média, que atualmente divide os pontos por 10,0.

## 9. Limitações e cuidados

- O recorde é armazenado na RAM e é perdido ao desligar ou reiniciar o Arduino.
- Pressionamentos ou liberações inferiores ao intervalo de debounce podem não ser contabilizados.
- O resultado por piscadas pode demorar em pontuações elevadas; a pontuação zero não possui sinalização numérica própria.
- O Monitor Serial é opcional para jogar, mas facilita a conferência dos valores exatos e dos recordes.
- A velocidade obtida no Tinkercad pode diferir da montagem física devido à interação com o mouse e à simulação.
- Utilize baixa tensão, resistores nos LEDs e conexões firmes. Não conecte o circuito diretamente à rede elétrica.
- O código e a montagem ainda precisam ser validados experimentalmente.

## 10. Organização do repositório

```text
14-button-frenzy/
├── button_frenzy.ino
└── README.md
```

O arquivo `README.md` contém esta documentação; o arquivo `.ino` contém o código-fonte do jogo.
