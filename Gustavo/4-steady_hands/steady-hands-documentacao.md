# 06 — Steady Hands: Teste de Precisão

## Aviso sobre a simulação no Tinkercad

Na versão do Tinkercad, os três botões permitem simular a dinâmica lúdica do jogo. O botão conectado ao **D2 representa o contato entre a argola metálica e o arame do percurso**. Na montagem física, esse botão deve ser retirado e substituído pelo conjunto de arame e argola com cabo isolado, ligados por fios ao Arduino.

Os botões de início (D3) e conclusão (D4) permanecem na versão física. Não é necessário modificar o código `.ino`, pois tanto o botão de simulação quanto o contato metálico fecham o circuito entre D2 e GND.

## 1. Objetivo

O Steady Hands é um jogo de habilidade que testa a precisão, a concentração e a coordenação motora do participante. O objetivo é conduzir uma argola metálica ao longo de um percurso de arame, sem encostar nele, no menor tempo possível.

## 2. Funcionamento e regras

1. O participante posiciona a argola no início do percurso e pressiona o botão de início.
2. O cronômetro começa e o LED amarelo acende. Os três LEDs verdes representam as vidas disponíveis.
3. A cada novo contato detectado entre a argola e o arame, uma vida é perdida, o buzzer emite um aviso e o LED vermelho indica o contato.
4. Manter o contato continuamente não elimina várias vidas de uma só vez. O código utiliza detecção de transição e um intervalo mínimo de 80 ms entre erros registrados.
5. Ao chegar ao final do percurso, o participante pressiona o botão de conclusão, sem tocar no arame.
6. Caso perca as três vidas, a partida termina em derrota.
7. O Arduino informa o tempo, os erros e o recorde pelo Monitor Serial. O menor tempo entre partidas concluídas com sucesso é considerado o recorde, independentemente da quantidade de erros.
8. Após a sinalização sonora e cinco segundos de exibição do resultado, o sistema restaura as vidas e aguarda a liberação dos botões para uma nova partida.

O jogo funciona sem computador durante a utilização física. O Monitor Serial é necessário apenas para consultar os valores numéricos de tempo e recorde. O recorde é mantido na memória RAM e é perdido quando o Arduino é desligado ou reiniciado.

## 3. Materiais necessários

| Material | Quantidade | Finalidade |
|---|---:|---|
| Arduino Uno R3 | 1 | Controle do jogo |
| Protoboard | 1 | Montagem do circuito |
| Push button | 2 (físico) ou 3 (Tinkercad) | Início, conclusão e simulação de contato |
| LED verde | 3 | Indicação das vidas |
| LED vermelho | 1 | Indicação de erro |
| LED amarelo | 1 | Indicação de partida ativa |
| Resistor de 220 Ω | 5 | Limitação de corrente dos LEDs |
| Buzzer piezoelétrico passivo | 1 | Avisos sonoros |
| Arame metálico rígido, sem revestimento | 1 | Construção do percurso físico |
| Argola metálica condutora | 1 | Peça móvel do jogador |
| Cabo ou empunhadura isolante | 1 | Sustentação da argola |
| Base de madeira ou plástico | 1 | Fixação do percurso |
| Fio flexível isolado e jumpers | Conforme necessário | Conexões elétricas |
| Fonte USB de 5 V adequada ao Arduino | 1 | Alimentação |

## 4. Ligações elétricas

| Componente | Pino do Arduino | Outra conexão |
|---|---|---|
| Arame do percurso (ou botão de erro no Tinkercad) | D2 | Argola (ou outro terminal do botão) ao GND |
| Botão de início | D3 | GND |
| Botão de conclusão | D4 | GND |
| LED verde 1 | D5 | GND, com resistor de 220 Ω em série |
| LED verde 2 | D6 | GND, com resistor de 220 Ω em série |
| LED verde 3 | D7 | GND, com resistor de 220 Ω em série |
| Buzzer passivo | D8 (+) | GND (-) |
| LED vermelho | D9 | GND, com resistor de 220 Ω em série |
| LED amarelo | D10 | GND, com resistor de 220 Ω em série |

### LEDs

Conecte cada pino digital ao ânodo (perna maior) do LED através de um resistor individual de 220 Ω. Conecte o cátodo (perna menor) ao GND.

### Botões e sensor de contato

Os pinos D2, D3 e D4 utilizam `INPUT_PULLUP`, portanto não necessitam de resistores externos de pull-up. Utilize terminais eletricamente opostos dos push buttons. Todos os componentes devem compartilhar o GND do Arduino.

- `HIGH`: circuito aberto, sem contato ou botão solto.
- `LOW`: circuito fechado, contato metálico ou botão pressionado.

```text
Montagem física:
D2 ─── arame do percurso
              contato eventual
GND ── fio flexível ── argola metálica

Tinkercad:
D2 ─── botão de erro ─── GND
```

## 5. Como construir a versão física

1. Separe uma base firme de madeira ou plástico, com espaço para o percurso e os botões.
2. Modele um arame rígido condutor, preferencialmente de 2 a 3 mm de espessura, formando curvas de diferentes dificuldades. Evite revestimentos isolantes na área de contato.
3. Construa uma argola metálica fechada e lisa, com abertura suficiente para passar pelo percurso. Passe a argola pelo arame antes de fixar definitivamente suas extremidades.
4. Fixe as extremidades do arame à base, protegendo pontas cortantes. Mantenha o percurso estável e eletricamente isolado de outras partes condutoras.
5. Prenda a argola a uma empunhadura isolante e conecte-a ao GND com um fio flexível suficientemente longo para percorrer todo o trajeto. Garanta alívio de tração para não romper o fio.
6. Conecte o arame ao D2. Verifique a continuidade elétrica da argola e do arame e certifique-se de que não exista contato permanente entre eles.
7. Instale o botão de início próximo ao começo do percurso e o de conclusão próximo ao final. Posicione os LEDs em local visível e fixe o buzzer e o circuito.
8. Carregue o código no Arduino, alimente-o por USB e teste os contatos, as vidas, os botões e a sinalização sonora antes de disponibilizar o jogo.

### Níveis de dificuldade sugeridos

| Diâmetro interno da argola | Dificuldade |
|---|---|
| 40 mm | Fácil |
| 25 mm | Média |
| 15 mm | Difícil |

Essas dimensões são sugestões e devem ser ajustadas conforme a espessura e as curvas do arame. Utilize somente baixa tensão do Arduino; nunca conecte o percurso à rede elétrica.

## 6. Como testar no Tinkercad

1. Crie um circuito com Arduino Uno, protoboard, três botões, cinco LEDs, cinco resistores de 220 Ω e um piezo passivo.
2. Monte as ligações da seção 4, substituindo o conjunto de arame e argola por um botão entre D2 e GND.
3. Abra a opção **Código**, selecione o modo **Texto** e cole o conteúdo do arquivo `steady_hands.ino`.
4. Inicie a simulação e abra o Monitor Serial (9600 baud).
5. Pressione e solte D3 para iniciar a partida.
6. Pressione e solte D2 para simular cada erro, respeitando o intervalo mínimo de 80 ms entre erros.
7. Pressione D4 antes de perder todas as vidas para simular a conclusão do percurso.
8. Repita o teste com três erros para verificar a derrota e aguarde o reinício automático.

Nenhum botão precisa ser pressionado simultaneamente, permitindo testar com apenas um mouse.

## 7. Organização do código

O arquivo `steady_hands.ino` utiliza as seguintes funções:

| Função | Responsabilidade |
|---|---|
| `setup()` | Configura os pinos e a comunicação serial |
| `loop()` | Detecta início, contatos e conclusão |
| `iniciarPartida()` | Restaura as vidas e inicia o cronômetro |
| `registrarErro()` | Desconta uma vida e aciona o buzzer |
| `atualizarVidas()` | Atualiza os LEDs verdes |
| `finalizarPartida()` | Apresenta o resultado, atualiza o recorde e prepara a próxima partida |

### Parâmetros principais

| Parâmetro | Valor |
|---|---|
| `totalVidas` | 3 |
| `debounceContato` | 80 ms |
| `tempoResultado` | 5000 ms |
| Comunicação serial | 9600 baud |

## 8. Estrutura do projeto

```text
06-steady-hands/
├── steady_hands.ino
└── README.md
```

## 9. Limitações e validação

O botão de conclusão não verifica automaticamente se a argola chegou ao final do percurso; a conclusão depende do cumprimento das regras pelo participante. O código e a construção física ainda precisam ser validados experimentalmente. A simulação com botões verifica a lógica eletrônica, mas não reproduz a dificuldade mecânica do percurso real.
