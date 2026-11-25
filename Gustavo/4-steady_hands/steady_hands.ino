const byte arame = 2;
const byte botaoInicio = 3;
const byte botaoFim = 4;

const byte ledsVidas[] = {5, 6, 7};

const byte buzzer = 8;
const byte ledErro = 9;
const byte ledPartida = 10;

const byte totalVidas = 3;

const unsigned long tempoResultado = 5000;
const unsigned long debounceContato = 80;

byte vidas = totalVidas;

bool jogando = false;
bool contatoAnterior = false;

unsigned long inicioPartida = 0;
unsigned long ultimoErro = 0;
unsigned long recorde = 0;

void setup() {

  pinMode(arame, INPUT_PULLUP);
  pinMode(botaoInicio, INPUT_PULLUP);
  pinMode(botaoFim, INPUT_PULLUP);

  pinMode(buzzer, OUTPUT);
  pinMode(ledErro, OUTPUT);
  pinMode(ledPartida, OUTPUT);

  for (int i = 0; i < totalVidas; i++) {
    pinMode(ledsVidas[i], OUTPUT);
  }

  Serial.begin(9600);

  atualizarVidas();

  Serial.println("=== STEADY HANDS ===");
  Serial.println("Aperte o botao para iniciar.");
}

void loop() {

  if (!jogando) {

    if (digitalRead(botaoInicio) == LOW &&
        digitalRead(botaoFim) == HIGH &&
        digitalRead(arame) == HIGH) {

      iniciarPartida();
    }

    return;
  }

  bool contato = digitalRead(arame) == LOW;

  digitalWrite(ledErro, contato ? HIGH : LOW);

  // Detecta um novo contato
  if (contato && !contatoAnterior) {

    if (millis() - ultimoErro >= debounceContato) {

      ultimoErro = millis();

      registrarErro();

      if (vidas == 0) {
        finalizarPartida(false);
        return;
      }
    }
  }

  contatoAnterior = contato;

  // Detecta a conclusao do percurso
  if (digitalRead(botaoFim) == LOW && !contato) {

    finalizarPartida(true);
  }
}

void iniciarPartida() {

  vidas = totalVidas;

  contatoAnterior = false;
  jogando = true;

  atualizarVidas();

  digitalWrite(ledPartida, HIGH);
  digitalWrite(ledErro, LOW);

  tone(buzzer, 1200, 200);

  inicioPartida = millis();
  ultimoErro = inicioPartida - debounceContato;

  Serial.println("\n=== PARTIDA INICIADA ===");
  Serial.println("Vidas: 3");
}

void registrarErro() {

  if (vidas > 0) {
    vidas--;
  }

  atualizarVidas();

  tone(buzzer, 400, 300);

  Serial.print("ERRO! Vidas restantes: ");
  Serial.println(vidas);
}

void atualizarVidas() {

  for (int i = 0; i < totalVidas; i++) {

    digitalWrite(
      ledsVidas[i],
      i < vidas ? HIGH : LOW
    );
  }
}

void finalizarPartida(bool venceu) {

  unsigned long tempo = millis() - inicioPartida;

  jogando = false;

  digitalWrite(ledPartida, LOW);

  Serial.println("\n=== RESULTADO ===");

  Serial.print("Tempo: ");
  Serial.print(tempo / 1000.0, 2);
  Serial.println(" segundos");

  Serial.print("Erros: ");
  Serial.println(totalVidas - vidas);

  if (venceu) {

    Serial.println("PERCURSO CONCLUIDO!");

    if (recorde == 0 || tempo < recorde) {

      recorde = tempo;

      Serial.println("NOVO RECORDE!");

      tone(buzzer, 1500, 200);
      delay(250);

      tone(buzzer, 2000, 200);
      delay(250);

      tone(buzzer, 2500, 400);

    } else {

      tone(buzzer, 1800, 500);
    }

  } else {

    Serial.println("GAME OVER!");

    digitalWrite(ledErro, HIGH);

    tone(buzzer, 500, 300);
    delay(350);

    tone(buzzer, 300, 600);
  }

  if (recorde > 0) {

    Serial.print("Recorde: ");
    Serial.print(recorde / 1000.0, 2);
    Serial.println(" segundos");
  }

  delay(tempoResultado);

  digitalWrite(ledErro, LOW);

  vidas = totalVidas;

  atualizarVidas();

  // Aguarda a liberacao dos botoes
  while (digitalRead(botaoInicio) == LOW ||
         digitalRead(botaoFim) == LOW) {
    delay(10);
  }

  Serial.println("\nAguardando novo jogador...");
}