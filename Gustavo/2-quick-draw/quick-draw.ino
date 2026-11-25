
const byte botao1 = 2;
const byte botao2 = 3;

const byte led1 = 5;
const byte led2 = 6;
const byte ledPartida = 7;

const byte buzzer = 8;

enum Estado {
  AGUARDANDO,
  AGUARDANDO_LIBERACAO,
  CONTAGEM,
  REACAO,
  RESULTADO
};

Estado estado = AGUARDANDO;

unsigned long inicioContagem;
unsigned long inicioReacao;
unsigned long tempo1 = 0;
unsigned long tempo2 = 0;

const unsigned long tempoLimite = 5000;

bool respondeu1 = false;
bool respondeu2 = false;

// Novas variáveis para iniciar com um botão por vez
bool pronto1 = false;
bool pronto2 = false;

void setup() {
  pinMode(botao1, INPUT_PULLUP);
  pinMode(botao2, INPUT_PULLUP);

  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(ledPartida, OUTPUT);

  pinMode(buzzer, OUTPUT);

  Serial.begin(9600);
  randomSeed(analogRead(A0));

  Serial.println("=== QUICK DRAW ===");
  Serial.println("Cada jogador deve pressionar seu botao para iniciar.");
}

void loop() {
  bool pressionado1 = digitalRead(botao1) == LOW;
  bool pressionado2 = digitalRead(botao2) == LOW;

  switch (estado) {

    case AGUARDANDO:

      // Cada jogador pode pressionar seu botao separadamente
      if (pressionado1) {
        pronto1 = true;
      }

      if (pressionado2) {
        pronto2 = true;
      }

      // Quando os dois estiverem prontos, inicia a preparacao
      if (pronto1 && pronto2) {
        digitalWrite(led1, LOW);
        digitalWrite(led2, LOW);
        digitalWrite(ledPartida, LOW);

        tempo1 = 0;
        tempo2 = 0;
        respondeu1 = false;
        respondeu2 = false;

        Serial.println("\nPreparem-se!");
        estado = AGUARDANDO_LIBERACAO;
      }
      break;

    case AGUARDANDO_LIBERACAO:

      if (!pressionado1 && !pressionado2) {
        inicioContagem = millis() + random(2000, 6000);
        estado = CONTAGEM;
      }
      break;

    case CONTAGEM:

      if (pressionado1 || pressionado2) {
        Serial.println("QUEIMA DE LARGADA!");

        if (pressionado1) {
          Serial.println("Jogador 1 foi desclassificado!");
          digitalWrite(led2, HIGH);
        } else {
          Serial.println("Jogador 2 foi desclassificado!");
          digitalWrite(led1, HIGH);
        }

        tone(buzzer, 300, 700);
        estado = RESULTADO;
        break;
      }

      if ((long)(millis() - inicioContagem) >= 0) {
        digitalWrite(ledPartida, HIGH);
        tone(buzzer, 1500, 200);

        inicioReacao = millis();

        Serial.println("VALENDO!");
        estado = REACAO;
      }
      break;

    case REACAO:

      if (pressionado1 && !respondeu1) {
        tempo1 = millis() - inicioReacao;
        respondeu1 = true;
      }

      if (pressionado2 && !respondeu2) {
        tempo2 = millis() - inicioReacao;
        respondeu2 = true;
      }

      if ((respondeu1 && respondeu2) ||
          millis() - inicioReacao >= tempoLimite) {

        digitalWrite(ledPartida, LOW);

        Serial.println("\n=== RESULTADO ===");

        if (respondeu1) {
          Serial.print("Jogador 1: ");
          Serial.print(tempo1);
          Serial.println(" ms");
        } else {
          Serial.println("Jogador 1: nao respondeu.");
        }

        if (respondeu2) {
          Serial.print("Jogador 2: ");
          Serial.print(tempo2);
          Serial.println(" ms");
        } else {
          Serial.println("Jogador 2: nao respondeu.");
        }

        if (!respondeu1 && !respondeu2) {
          Serial.println("Ninguem respondeu!");
        }
        else if (!respondeu1) {
          Serial.println("Jogador 2 venceu!");
          digitalWrite(led2, HIGH);
        }
        else if (!respondeu2) {
          Serial.println("Jogador 1 venceu!");
          digitalWrite(led1, HIGH);
        }
        else if (tempo1 < tempo2) {
          Serial.println("Jogador 1 venceu!");
          digitalWrite(led1, HIGH);
        }
        else if (tempo2 < tempo1) {
          Serial.println("Jogador 2 venceu!");
          digitalWrite(led2, HIGH);
        }
        else {
          Serial.println("Empate!");
        }

        tone(buzzer, 800, 500);
        estado = RESULTADO;
      }
      break;

    case RESULTADO:

      // Os jogadores precisam soltar os botoes
      // antes de iniciar uma nova partida.
      if (!pressionado1 && !pressionado2) {
        pronto1 = false;
        pronto2 = false;

        estado = AGUARDANDO;
        Serial.println("\nNova partida: cada jogador pressione seu botao.");
      }
      break;
  }
}


// ============================================================
// CODIGO ANTIGO - VERSAO ORIGINAL
// Mantido comentado para consulta.
// ============================================================

/*

const byte botao1 = 2;
const byte botao2 = 3;

const byte led1 = 5;
const byte led2 = 6;
const byte ledPartida = 7;

const byte buzzer = 8;

enum Estado {
  AGUARDANDO,
  AGUARDANDO_LIBERACAO,
  CONTAGEM,
  REACAO,
  RESULTADO
};

Estado estado = AGUARDANDO;

unsigned long inicioContagem;
unsigned long inicioReacao;
unsigned long tempo1 = 0;
unsigned long tempo2 = 0;

const unsigned long tempoLimite = 5000;

bool respondeu1 = false;
bool respondeu2 = false;

void setup() {
  pinMode(botao1, INPUT_PULLUP);
  pinMode(botao2, INPUT_PULLUP);

  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(ledPartida, OUTPUT);

  pinMode(buzzer, OUTPUT);

  Serial.begin(9600);
  randomSeed(analogRead(A0));

  Serial.println("=== QUICK DRAW ===");
  Serial.println("Jogadores: apertem os dois botoes para iniciar.");
}

void loop() {
  bool pressionado1 = digitalRead(botao1) == LOW;
  bool pressionado2 = digitalRead(botao2) == LOW;

  switch (estado) {

    case AGUARDANDO:

      if (pressionado1 && pressionado2) {
        digitalWrite(led1, LOW);
        digitalWrite(led2, LOW);
        digitalWrite(ledPartida, LOW);

        tempo1 = 0;
        tempo2 = 0;
        respondeu1 = false;
        respondeu2 = false;

        Serial.println("\nPreparem-se!");
        estado = AGUARDANDO_LIBERACAO;
      }
      break;

    case AGUARDANDO_LIBERACAO:

      if (!pressionado1 && !pressionado2) {
        inicioContagem = millis() + random(2000, 6000);
        estado = CONTAGEM;
      }
      break;

    case CONTAGEM:

      if (pressionado1 || pressionado2) {
        Serial.println("QUEIMA DE LARGADA!");

        if (pressionado1) {
          Serial.println("Jogador 1 foi desclassificado!");
          digitalWrite(led2, HIGH);
        } else {
          Serial.println("Jogador 2 foi desclassificado!");
          digitalWrite(led1, HIGH);
        }

        tone(buzzer, 300, 700);
        estado = RESULTADO;
        break;
      }

      if ((long)(millis() - inicioContagem) >= 0) {
        digitalWrite(ledPartida, HIGH);
        tone(buzzer, 1500, 200);

        inicioReacao = millis();

        Serial.println("VALENDO!");
        estado = REACAO;
      }
      break;

    case REACAO:

      if (pressionado1 && !respondeu1) {
        tempo1 = millis() - inicioReacao;
        respondeu1 = true;
      }

      if (pressionado2 && !respondeu2) {
        tempo2 = millis() - inicioReacao;
        respondeu2 = true;
      }

      if ((respondeu1 && respondeu2) ||
          millis() - inicioReacao >= tempoLimite) {

        digitalWrite(ledPartida, LOW);

        Serial.println("\n=== RESULTADO ===");

        if (respondeu1) {
          Serial.print("Jogador 1: ");
          Serial.print(tempo1);
          Serial.println(" ms");
        } else {
          Serial.println("Jogador 1: nao respondeu.");
        }

        if (respondeu2) {
          Serial.print("Jogador 2: ");
          Serial.print(tempo2);
          Serial.println(" ms");
        } else {
          Serial.println("Jogador 2: nao respondeu.");
        }

        if (!respondeu1 && !respondeu2) {
          Serial.println("Ninguem respondeu!");
        }
        else if (!respondeu1) {
          Serial.println("Jogador 2 venceu!");
          digitalWrite(led2, HIGH);
        }
        else if (!respondeu2) {
          Serial.println("Jogador 1 venceu!");
          digitalWrite(led1, HIGH);
        }
        else if (tempo1 < tempo2) {
          Serial.println("Jogador 1 venceu!");
          digitalWrite(led1, HIGH);
        }
        else if (tempo2 < tempo1) {
          Serial.println("Jogador 2 venceu!");
          digitalWrite(led2, HIGH);
        }
        else {
          Serial.println("Empate!");
        }

        tone(buzzer, 800, 500);
        estado = RESULTADO;
      }
      break;

    case RESULTADO:

      if (!pressionado1 && !pressionado2) {
        estado = AGUARDANDO;
        Serial.println("\nNova partida: apertem os dois botoes.");
      }
      break;
  }
}

*/
