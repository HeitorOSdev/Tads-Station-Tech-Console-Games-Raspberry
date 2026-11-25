// =====================================================================
// MEMORY MASTER — Desafio da Memória
// Jogo no estilo "Genius" para Arduino Uno R3
// Tech Arcade — Mostra de Profissões
// =====================================================================
//
// O Arduino mostra uma sequência de luzes e sons. O participante deve
// repetir a sequência apertando os botões na mesma ordem. A cada rodada
// uma nova cor é adicionada ao final e a sequência fica mais rápida.
//
// O mesmo código funciona no Tinkercad e na montagem física.
// =====================================================================

// ---------- Pinos ----------
const int NUM_CORES = 4;

// Índices: 0 = Vermelho, 1 = Verde, 2 = Azul, 3 = Amarelo
const int pinosBotoes[NUM_CORES] = {2, 3, 4, 5};
const int pinosLeds[NUM_CORES]   = {8, 9, 10, 11};
const int pinoBuzzer = 12;

// Frequência (Hz) do som de cada cor
const int tons[NUM_CORES] = {262, 330, 392, 523};  // Dó, Mi, Sol, Dó agudo

const char* nomesCores[NUM_CORES] = {"Vermelho", "Verde", "Azul", "Amarelo"};

// ---------- Configurações do jogo ----------
const int TAMANHO_MAXIMO = 32;            // Rodadas para vencer o jogo
const unsigned long TEMPO_RESPOSTA = 5000; // Tempo máximo para cada toque (ms)

const int TEMPO_ACESO_INICIAL = 600;  // Duração de cada luz na rodada 1 (ms)
const int TEMPO_ACESO_MINIMO  = 180;  // Duração mínima de cada luz (ms)
const int REDUCAO_POR_RODADA  = 35;   // Quanto a luz fica mais curta por rodada (ms)

const int PAUSA_INICIAL = 250;        // Pausa entre luzes na rodada 1 (ms)
const int PAUSA_MINIMA  = 80;         // Pausa mínima entre luzes (ms)

const int TEMPO_DEBOUNCE = 30;        // Filtro de ruído dos botões (ms)

// ---------- Estado do jogo ----------
int sequencia[TAMANHO_MAXIMO];
int rodada = 0;      // Quantidade de cores na sequência atual
int recorde = 0;     // Melhor pontuação desde que o Arduino foi ligado

// ---------- Protótipos das funções ----------
void aguardarInicio();
void jogar();
void mostrarSequencia();
bool lerRespostaJogador();
int esperarBotao(unsigned long limite);
int lerBotaoPressionado();
void esperarSoltar(int botao);
void esperarSoltarTodos();
void acenderCor(int cor, int duracao);
void apagarTodos();
void acenderTodos();
void animacaoInicio();
void fimDeJogo();
void vitoria();

// =====================================================================
void setup() {
  for (int i = 0; i < NUM_CORES; i++) {
    pinMode(pinosBotoes[i], INPUT_PULLUP);
    pinMode(pinosLeds[i], OUTPUT);
    digitalWrite(pinosLeds[i], LOW);
  }
  pinMode(pinoBuzzer, OUTPUT);

  Serial.begin(9600);
  randomSeed(analogRead(A0));  // A0 desconectado gera um valor inicial variável

  Serial.println("=== MEMORY MASTER - Desafio da Memoria ===");
}

// =====================================================================
void loop() {
  aguardarInicio();
  jogar();
}

// ---------------------------------------------------------------------
// Fica em modo de espera (luzes girando) até alguém apertar um botão.
// ---------------------------------------------------------------------
void aguardarInicio() {
  Serial.println();
  Serial.println("Aperte qualquer botao para comecar.");

  int led = 0;
  unsigned long ultimaTroca = 0;

  while (lerBotaoPressionado() == -1) {
    if (millis() - ultimaTroca >= 200) {
      apagarTodos();
      digitalWrite(pinosLeds[led], HIGH);
      led = (led + 1) % NUM_CORES;
      ultimaTroca = millis();
    }
  }

  apagarTodos();
  esperarSoltarTodos();
  animacaoInicio();
}

// ---------------------------------------------------------------------
// Uma partida completa: repete rodadas até o jogador errar ou vencer.
// ---------------------------------------------------------------------
void jogar() {
  rodada = 0;
  Serial.println("Partida iniciada! Memorize a sequencia.");
  delay(800);

  while (true) {
    // Adiciona uma nova cor ao final da sequência
    sequencia[rodada] = random(0, NUM_CORES);
    rodada++;

    Serial.print("\nRodada ");
    Serial.println(rodada);

    mostrarSequencia();

    if (!lerRespostaJogador()) {
      fimDeJogo();
      return;
    }

    if (rodada >= TAMANHO_MAXIMO) {
      vitoria();
      return;
    }

    Serial.println("Correto!");
    delay(700);  // Pequena pausa antes da próxima rodada
  }
}

// ---------------------------------------------------------------------
// Mostra a sequência. A velocidade aumenta a cada rodada.
// ---------------------------------------------------------------------
void mostrarSequencia() {
  int tempoAceso = TEMPO_ACESO_INICIAL - (rodada - 1) * REDUCAO_POR_RODADA;
  if (tempoAceso < TEMPO_ACESO_MINIMO) tempoAceso = TEMPO_ACESO_MINIMO;

  int pausa = PAUSA_INICIAL - (rodada - 1) * 15;
  if (pausa < PAUSA_MINIMA) pausa = PAUSA_MINIMA;

  Serial.print("Sequencia: ");
  for (int i = 0; i < rodada; i++) {
    Serial.print(nomesCores[sequencia[i]]);
    if (i < rodada - 1) Serial.print(" - ");

    acenderCor(sequencia[i], tempoAceso);
    delay(pausa);
  }
  Serial.println();
  Serial.println("Sua vez!");
}

// ---------------------------------------------------------------------
// Lê a resposta do jogador. Retorna true se acertou a sequência inteira.
// ---------------------------------------------------------------------
bool lerRespostaJogador() {
  for (int i = 0; i < rodada; i++) {
    int botao = esperarBotao(TEMPO_RESPOSTA);

    if (botao == -1) {
      Serial.println("Tempo esgotado!");
      return false;
    }

    // Acende a cor enquanto o botão estiver pressionado
    digitalWrite(pinosLeds[botao], HIGH);
    tone(pinoBuzzer, tons[botao]);
    esperarSoltar(botao);
    digitalWrite(pinosLeds[botao], LOW);
    noTone(pinoBuzzer);

    if (botao != sequencia[i]) {
      Serial.print("Errou! Voce apertou ");
      Serial.print(nomesCores[botao]);
      Serial.print(", o certo era ");
      Serial.println(nomesCores[sequencia[i]]);
      return false;
    }
  }
  return true;
}

// ---------------------------------------------------------------------
// Espera um botão por até "limite" ms. Retorna o índice ou -1 (tempo esgotado).
// ---------------------------------------------------------------------
int esperarBotao(unsigned long limite) {
  unsigned long inicio = millis();
  while (millis() - inicio < limite) {
    int botao = lerBotaoPressionado();
    if (botao != -1) return botao;
  }
  return -1;
}

// ---------------------------------------------------------------------
// Retorna o índice do botão pressionado (com debounce) ou -1 se nenhum.
// Com INPUT_PULLUP, o botão pressionado lê LOW.
// ---------------------------------------------------------------------
int lerBotaoPressionado() {
  for (int i = 0; i < NUM_CORES; i++) {
    if (digitalRead(pinosBotoes[i]) == LOW) {
      delay(TEMPO_DEBOUNCE);
      if (digitalRead(pinosBotoes[i]) == LOW) return i;
    }
  }
  return -1;
}

void esperarSoltar(int botao) {
  while (digitalRead(pinosBotoes[botao]) == LOW) { }
  delay(TEMPO_DEBOUNCE);
}

void esperarSoltarTodos() {
  for (int i = 0; i < NUM_CORES; i++) esperarSoltar(i);
}

// ---------------------------------------------------------------------
// Saídas: LEDs e buzzer
// ---------------------------------------------------------------------
void acenderCor(int cor, int duracao) {
  digitalWrite(pinosLeds[cor], HIGH);
  tone(pinoBuzzer, tons[cor]);
  delay(duracao);
  digitalWrite(pinosLeds[cor], LOW);
  noTone(pinoBuzzer);
}

void apagarTodos() {
  for (int i = 0; i < NUM_CORES; i++) digitalWrite(pinosLeds[i], LOW);
}

void acenderTodos() {
  for (int i = 0; i < NUM_CORES; i++) digitalWrite(pinosLeds[i], HIGH);
}

void animacaoInicio() {
  for (int i = 0; i < NUM_CORES; i++) acenderCor(i, 120);
  acenderTodos();
  tone(pinoBuzzer, 784, 300);
  delay(400);
  apagarTodos();
}

// ---------------------------------------------------------------------
// Fim de jogo: som de erro, pontuação e recorde
// ---------------------------------------------------------------------
void fimDeJogo() {
  int pontos = rodada - 1;  // Rodadas completadas com sucesso

  // Pisca todos os LEDs com som grave de erro
  for (int i = 0; i < 3; i++) {
    acenderTodos();
    tone(pinoBuzzer, 150);
    delay(250);
    apagarTodos();
    noTone(pinoBuzzer);
    delay(150);
  }

  Serial.println("\n=== FIM DE JOGO ===");
  Serial.print("Pontuacao: ");
  Serial.print(pontos);
  Serial.println(pontos == 1 ? " rodada" : " rodadas");

  if (pontos > recorde) {
    recorde = pontos;
    Serial.println("NOVO RECORDE!");
    tone(pinoBuzzer, 1047, 150);
    delay(200);
    tone(pinoBuzzer, 1319, 300);
    delay(350);
  }

  Serial.print("Recorde atual: ");
  Serial.println(recorde);

  esperarSoltarTodos();
  delay(1000);
}

void vitoria() {
  Serial.println("\n=== PARABENS! VOCE COMPLETOU TODAS AS RODADAS! ===");
  recorde = TAMANHO_MAXIMO;

  for (int volta = 0; volta < 3; volta++) {
    for (int i = 0; i < NUM_CORES; i++) acenderCor(i, 80);
  }
  acenderTodos();
  tone(pinoBuzzer, 1047, 600);
  delay(700);
  apagarTodos();

  Serial.print("Recorde atual: ");
  Serial.println(recorde);
  delay(1000);
}
