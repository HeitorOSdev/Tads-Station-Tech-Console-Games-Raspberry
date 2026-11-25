# QUICK DRAW — Teste de Reflexo

## 1. Sobre o projeto

O **Quick Draw** é um jogo eletrônico de reflexo para dois participantes. O objetivo é apertar o próprio botão o mais rápido possível depois que o sinal de largada aparecer.

O Arduino controla os botões, os LEDs e o buzzer, mede o tempo de reação dos jogadores e identifica o vencedor.

## 2. Versões do código

O projeto possui duas versões do código:

- **Primeira versão — teste no Tinkercad:** utiliza uma sequência de preparação em que o Jogador 1 pressiona e solta seu botão e, depois, o Jogador 2 faz o mesmo. Assim, é possível iniciar a partida usando apenas um mouse no simulador, sem precisar pressionar os dois botões simultaneamente.
- **Segunda versão — montagem física:** é a versão original, mantida comentada no final do código. Nela, os dois jogadores pressionam os botões simultaneamente para iniciar a preparação da partida, o que permite começar juntos no equipamento físico.

**Atenção:** a segunda versão está dentro de um comentário (`/* ... */`) e, portanto, não é executada enquanto permanecer comentada. Para utilizá-la no Arduino físico, descomente o código original e comente ou retire a primeira versão ativa. Não deixe as duas versões ativas ao mesmo tempo, pois elas declaram as mesmas variáveis e funções.

## 3. Como o jogo funciona

1. Os jogadores iniciam a partida conforme a versão utilizada.
2. O Arduino entra no estado de preparação.
3. Depois que os botões são soltos, o sistema sorteia um intervalo aleatório entre 2 e 6 segundos.
4. Ao terminar a espera, o LED central acende e o buzzer emite um sinal sonoro. Esse é o sinal de largada.
5. Cada jogador aperta seu botão o mais rápido possível.
6. O Arduino registra o tempo entre o sinal de largada e o pressionamento de cada botão.
7. Quando os dois jogadores respondem, ou quando o limite de 5 segundos termina, o sistema apresenta os tempos e indica o vencedor.
8. O LED correspondente ao vencedor acende. Para iniciar outra rodada, os botões precisam estar soltos.

### Queima de largada

Na versão de teste do Tinkercad, se algum jogador apertar um botão durante a espera aleatória, antes do sinal de largada, o sistema identifica uma queima de largada e desclassifica esse jogador.

## 4. Componentes necessários

| Componente | Quantidade | Função |
|---|---:|---|
| Arduino Uno R3 | 1 | Controla o jogo |
| Pushbuttons (botões) | 2 | Um botão para cada jogador |
| LEDs | 3 | Dois indicam o vencedor; um sinaliza a largada |
| Resistores de 220 Ω | 3 | Limitam a corrente dos LEDs |
| Buzzer piezo | 1 | Emite os sinais sonoros |
| Protoboard | 1 | Facilita a montagem |
| Jumpers | Conforme necessário | Realizam as conexões |

## 5. Ligações dos componentes

### 5.1. Botões

Os botões utilizam a configuração `INPUT_PULLUP`. Por isso, não precisam de resistores externos.

| Componente | Terminal | Conectar ao |
|---|---|---|
| Botão do Jogador 1 | Um terminal | Pino digital 2 |
| Botão do Jogador 1 | Terminal oposto | GND |
| Botão do Jogador 2 | Um terminal | Pino digital 3 |
| Botão do Jogador 2 | Terminal oposto | GND |

**Importante:** se forem utilizados pushbuttons de quatro pernas, coloque cada botão atravessando o vão central da protoboard. Utilize terminais de lados opostos do botão, pois as duas pernas do mesmo lado normalmente já são conectadas internamente.

### 5.2. LEDs

Cada LED deve possuir um resistor de 220 Ω em série.

| LED | Ânodo (perna maior), passando pelo resistor | Cátodo (perna menor) |
|---|---|---|
| LED do Jogador 1 | Pino digital 5 | GND |
| LED do Jogador 2 | Pino digital 6 | GND |
| LED de largada (central) | Pino digital 7 | GND |

A ligação de cada LED deve seguir esta ordem:

`Pino digital do Arduino → resistor de 220 Ω → ânodo do LED → cátodo do LED → GND`

O resistor também pode ficar entre o cátodo e o GND, desde que esteja em série com o LED.

### 5.3. Buzzer

| Terminal do buzzer | Conectar ao |
|---|---|
| Positivo (+) | Pino digital 8 |
| Negativo (-) | GND |

### 5.4. Alimentação e GND

- Conecte o pino **GND** do Arduino ao barramento negativo da protoboard.
- Utilize esse barramento como referência de GND para os botões, LEDs e buzzer.
- No Tinkercad, o Arduino pode ser alimentado pela própria simulação. Na montagem física, utilize uma alimentação adequada para a placa.

## 6. Resumo dos pinos do Arduino

| Pino | Componente |
|---|---|
| D2 | Botão do Jogador 1 |
| D3 | Botão do Jogador 2 |
| D5 | LED do Jogador 1 |
| D6 | LED do Jogador 2 |
| D7 | LED central de largada |
| D8 | Buzzer |
| GND | Terra comum dos componentes |
| A0 | Entrada analógica usada para inicializar a aleatoriedade |

O pino A0 não precisa receber nenhum componente: no código, ele é lido para inicializar o gerador de números aleatórios.

## 7. Significado dos LEDs

- **LED central (D7):** acende quando a largada é liberada. Apaga ao terminar a rodada.
- **LED do Jogador 1 (D5):** acende quando o Jogador 1 vence.
- **LED do Jogador 2 (D6):** acende quando o Jogador 2 vence.

Os LEDs laterais também são utilizados para indicar o vencedor em caso de queima de largada na versão de teste.

## 8. Como testar no Tinkercad

1. Monte o circuito conforme as tabelas de ligação.
2. Abra o editor de código do Arduino e selecione o modo texto.
3. Cole a primeira versão ativa do código.
4. Inicie a simulação.
5. Abra o Monitor Serial e configure a velocidade para **9600 baud**.
6. Na versão de teste, clique e solte o botão do Jogador 1 e depois clique e solte o botão do Jogador 2.
7. Aguarde o sinal de largada.
8. Pressione os botões e confira os tempos e o vencedor no Monitor Serial.

Para testar a queima de largada, pressione um dos botões durante a espera, antes de o LED central acender.

## 9. Observações

- O tempo de reação é calculado em milissegundos (`ms`).
- O intervalo aleatório de preparação é de 2.000 a 6.000 milissegundos.
- O tempo máximo para responder é de 5.000 milissegundos.
- O Monitor Serial é utilizado para visualizar os resultados; ele não é uma interface gráfica do jogo.
- Antes de utilizar o equipamento com o público, teste os botões, a polaridade dos LEDs, os resistores e o funcionamento do buzzer.
- O resultado depende da leitura dos botões e da resolução de tempo do Arduino. O projeto é uma demonstração educativa, não um instrumento profissional de medição esportiva.

## 10. Identificação do projeto

**Nome:** Quick Draw — Teste de Reflexo  
**Plataforma:** Arduino Uno R3  
**Simulador inicial:** Tinkercad  
**Participantes:** 2 jogadores  
**Objetivo:** medir e comparar o tempo de reação dos participantes.
