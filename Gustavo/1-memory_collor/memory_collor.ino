const byte botoes[] = {2, 3};
const byte leds[] = {5, 6};

const byte tamanhoMaximo = 100;

const unsigned long tempoResposta = 10000;

byte sequencia[tamanhoMaximo];

int rodada = 0;
int recorde = 0;

void setup() {

  for (int i = 0; i < 2; i++) {
    pinMode(botoes[i], INPUT_PULLUP);
    pinMode(leds[i], OUTPUT);
  }

  Serial.begin(9600);

  randomSeed(analogRead(A0));

  Serial.println("=== MEMORY MASTER ===");
}

void loop() {

  aguardarJogador();

  rodada = 0;

  Serial.println("\n=== NOVA PARTIDA ===");

  delay(1000);

  while (rodada < tamanhoMaximo) {

    // Adiciona uma nova luz a sequencia
    sequencia[rodada] = random(0, 2);

    rodada++;

    Serial.print("Rodada: ");
    Serial.println(rodada);

    mostrarSequencia();

    if (!verificarResposta()) {

      finalizarPartida(rodada - 1);

      return;
    }

    Serial.println("Sequencia correta!");

    // Sinaliza acerto
    piscarTodos(1, 200);

    delay(700);
  }

  // Jogador atingiu o limite de rodadas
  Serial.println("JOGO COMPLETADO!");

  finalizarPartida(tamanhoMaximo);
}

void aguardarJogador() {

  Serial.println("\nPressione qualquer botao para iniciar.");

  while (true) {

    bool estado = (millis() / 500) % 2;

    digitalWrite(leds[0], estado);
    digitalWrite(leds[1], estado);

    if (digitalRead(botoes[0]) == LOW ||
        digitalRead(botoes[1]) == LOW) {

      apagarLeds();

      aguardarLiberacao();

      return;
    }

    delay(10);
  }
}

void mostrarSequencia() {

  // A velocidade aumenta a cada rodada
  int tempoLed = max(200, 600 - rodada * 15);

  for (int i = 0; i < rodada; i++) {

    byte ledAtual = sequencia[i];

    digitalWrite(leds[ledAtual], HIGH);

    delay(tempoLed);

    digitalWrite(leds[ledAtual], LOW);

    delay(250);
  }
}

bool verificarResposta() {

  for (int i = 0; i < rodada; i++) {

    int resposta = lerBotao();

    // Tempo limite ou botoes simultaneos
    if (resposta < 0) {
      return false;
    }

    digitalWrite(leds[resposta], HIGH);

    delay(150);

    digitalWrite(leds[resposta], LOW);

    if (resposta != sequencia[i]) {

      Serial.println("Resposta incorreta!");

      return false;
    }
  }

  return true;
}

int lerBotao() {

  unsigned long inicio = millis();

  while (millis() - inicio < tempoResposta) {

    bool verde = digitalRead(botoes[0]) == LOW;
    bool vermelho = digitalRead(botoes[1]) == LOW;

    if (verde || vermelho) {

      delay(30);

      verde = digitalRead(botoes[0]) == LOW;
      vermelho = digitalRead(botoes[1]) == LOW;

      if (verde && vermelho) {

        aguardarLiberacao();

        return -1;
      }

      if (verde || vermelho) {

        int resposta = verde ? 0 : 1;

        aguardarLiberacao();

        return resposta;
      }
    }

    delay(5);
  }

  Serial.println("Tempo esgotado!");

  return -1;
}

void aguardarLiberacao() {

  while (digitalRead(botoes[0]) == LOW ||
         digitalRead(botoes[1]) == LOW) {

    delay(10);
  }

  delay(30);
}

void finalizarPartida(int pontos) {

  Serial.println("\n=== RESULTADO ===");

  Serial.print("Pontuacao: ");
  Serial.println(pontos);

  if (pontos > recorde) {

    recorde = pontos;

    Serial.println("NOVO RECORDE!");
  }

  Serial.print("Recorde: ");
  Serial.println(recorde);

  if (pontos == tamanhoMaximo) {

    piscarTodos(5, 400);

  } else {

    piscarTodos(5, 100);
  }

  delay(2000);
}

void piscarTodos(int vezes, int intervalo) {

  for (int i = 0; i < vezes; i++) {

    digitalWrite(leds[0], HIGH);
    digitalWrite(leds[1], HIGH);

    delay(intervalo);

    apagarLeds();

    delay(intervalo);
  }
}

void apagarLeds() {

  digitalWrite(leds[0], LOW);
  digitalWrite(leds[1], LOW);
}