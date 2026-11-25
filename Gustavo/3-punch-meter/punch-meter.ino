const byte sensorPiezo = A0;
const byte buzzer = 8;

const byte leds[] = {2, 3, 4, 5, 6};
const byte quantidadeLeds = 5;

const int limiteImpacto = 30;
const int impactoMaximo = 1023;

const unsigned long janelaCaptura = 50;
const unsigned long tempoResultado = 5000;

int recorde = 0;

void setup() {
  pinMode(sensorPiezo, INPUT);
  pinMode(buzzer, OUTPUT);

  for (int i = 0; i < quantidadeLeds; i++) {
    pinMode(leds[i], OUTPUT);
  }

  Serial.begin(9600);

  Serial.println("=== PUNCH METER ===");
  Serial.println("Aguardando impacto...");

  tone(buzzer, 1000, 200);
}

void loop() {
  int leitura = analogRead(sensorPiezo);

  if (leitura >= limiteImpacto) {

    int pico = leitura;
    unsigned long inicio = millis();

    // Captura o maior valor do impacto
    while (millis() - inicio < janelaCaptura) {
      leitura = analogRead(sensorPiezo);

      if (leitura > pico) {
        pico = leitura;
      }
    }

    // Converte o impacto em pontuacao
    int pontos = map(
      pico, 0, impactoMaximo, 0, 1000
    );

    pontos = constrain(pontos, 0, 1000);

    Serial.println("\n=== RESULTADO ===");

    Serial.print("Pico do sensor: ");
    Serial.println(pico);

    Serial.print("Pontuacao: ");
    Serial.println(pontos);

    mostrarResultado(pontos);

    if (pontos > recorde) {
      recorde = pontos;

      Serial.println("NOVO RECORDE!");

      tone(buzzer, 1500, 200);
      delay(250);

      tone(buzzer, 2000, 200);
      delay(250);

      tone(buzzer, 2500, 400);
    } else {
      tone(buzzer, 1000, 300);
    }

    Serial.print("Recorde: ");
    Serial.println(recorde);

    delay(tempoResultado);

    apagarLeds();

    Serial.println("\nAguardando novo impacto...");
  }
}

void mostrarResultado(int pontos) {

  int nivel = constrain(
    (pontos + 199) / 200, 1, 5
  );

  for (int i = 0; i < nivel; i++) {
    digitalWrite(leds[i], HIGH);

    tone(buzzer, 600 + (i * 300), 100);

    delay(150);
  }

  if (nivel == 1) {
    Serial.println("Nivel: FRACO");
  }
  else if (nivel == 2) {
    Serial.println("Nivel: MODERADO");
  }
  else if (nivel == 3) {
    Serial.println("Nivel: FORTE");
  }
  else if (nivel == 4) {
    Serial.println("Nivel: MUITO FORTE");
  }
  else {
    Serial.println("Nivel: EXTREMO");
  }
}

void apagarLeds() {
  for (int i = 0; i < quantidadeLeds; i++) {
    digitalWrite(leds[i], LOW);
  }
}