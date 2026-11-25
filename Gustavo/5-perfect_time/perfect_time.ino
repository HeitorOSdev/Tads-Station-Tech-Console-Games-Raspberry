const byte botao = 2;
const byte ledVerde = 5;
const byte ledVermelho = 6;

const unsigned long tempoIdeal = 5000;
const unsigned long tempoResultado = 5000;
const unsigned long tempoLimite = 30000;

unsigned long recorde = 0;
bool possuiRecorde = false;

void setup() {

  pinMode(botao, INPUT_PULLUP);

  pinMode(ledVerde, OUTPUT);
  pinMode(ledVermelho, OUTPUT);

  Serial.begin(9600);

  Serial.println("=== PERFECT TIME ===");
}

void loop() {

  aguardarJogador();

  digitalWrite(ledVerde, HIGH);

  unsigned long inicio = millis();

  Serial.println("\nPartida iniciada!");
  Serial.println("Tente acertar 5 segundos.");

  aguardarLiberacao();

  // Aguarda o segundo pressionamento
  while (digitalRead(botao) == HIGH) {

    if (millis() - inicio >= tempoLimite) {

      apagarLeds();

      Serial.println("Tempo limite atingido!");

      piscarLed(ledVermelho, 5, 100);

      delay(tempoResultado);

      return;
    }
  }

  unsigned long tempo = millis() - inicio;

  aguardarLiberacao();

  apagarLeds();

  // Calcula a diferenca absoluta
  unsigned long erro;

  if (tempo >= tempoIdeal) {
    erro = tempo - tempoIdeal;
  } else {
    erro = tempoIdeal - tempo;
  }

  // Calcula a pontuacao de 0 a 1000
  int pontos = 1000 - min(erro, 1000UL);

  Serial.println("\n=== RESULTADO ===");

  Serial.print("Tempo registrado: ");
  Serial.print(tempo / 1000.0, 3);
  Serial.println(" segundos");

  Serial.print("Diferenca: ");
  Serial.print(erro);
  Serial.println(" ms");

  Serial.print("Pontuacao: ");
  Serial.println(pontos);

  mostrarResultado(erro);

  // Verifica o recorde
  if (!possuiRecorde || erro < recorde) {

    recorde = erro;
    possuiRecorde = true;

    Serial.println("NOVO RECORDE!");

    piscarTodos(3, 200);
  }

  Serial.print("Melhor diferenca: ");
  Serial.print(recorde);
  Serial.println(" ms");

  delay(tempoResultado);

  apagarLeds();
}

void aguardarJogador() {

  Serial.println("\nPressione o botao para iniciar.");

  while (digitalRead(botao) == HIGH) {

    bool estado = (millis() / 500) % 2;

    digitalWrite(ledVerde, estado);
    digitalWrite(ledVermelho, estado);

    delay(5);
  }

  apagarLeds();
}

void aguardarLiberacao() {

  while (digitalRead(botao) == LOW) {
    delay(5);
  }

  delay(30);
}

void mostrarResultado(unsigned long erro) {

  if (erro <= 100) {

    Serial.println("PERFEITO!");
    piscarLed(ledVerde, 5, 100);

  } else if (erro <= 250) {

    Serial.println("EXCELENTE!");
    piscarLed(ledVerde, 3, 200);

  } else if (erro <= 500) {

    Serial.println("BOM!");
    piscarLed(ledVerde, 1, 1000);

  } else if (erro <= 1000) {

    Serial.println("REGULAR!");
    piscarLed(ledVermelho, 2, 300);

  } else {

    Serial.println("RUIM!");
    piscarLed(ledVermelho, 5, 100);
  }
}

void piscarLed(byte led, int vezes, int intervalo) {

  for (int i = 0; i < vezes; i++) {

    digitalWrite(led, HIGH);

    delay(intervalo);

    digitalWrite(led, LOW);

    delay(intervalo);
  }
}

void piscarTodos(int vezes, int intervalo) {

  for (int i = 0; i < vezes; i++) {

    digitalWrite(ledVerde, HIGH);
    digitalWrite(ledVermelho, HIGH);

    delay(intervalo);

    apagarLeds();

    delay(intervalo);
  }
}

void apagarLeds() {

  digitalWrite(ledVerde, LOW);
  digitalWrite(ledVermelho, LOW);
}