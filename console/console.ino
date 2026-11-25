// ============================================================================
// TECH ARCADE — MINI CONSOLE UNIFICADO
// Plataforma: Arduino Uno R3 (ATmega328P) + Display OLED I2C 128x64 (SSD1306)
//
// Jogos Integrados:
// 1. Memory Master (Genius de 4 Cores e Notas Musicais)
// 2. Quick Draw (Duelo de Reflexo para 2 Jogadores)
// 3. Punch Meter (Medidor de Força com Sensor Piezoelétrico)
// 4. Steady Hands (Mão Firme com Pista de Arame e Vidas)
// 5. Campo Minado (Desafio Eletrônico com 5 Posições e 2 Minas)
//
// Engenharia de Software:
// - Programação Orientada a Objetos (POO), Clean Code e Máquina de Estados
// - Temporização não-bloqueante baseada em millis()
// - Otimização estrita de memória Flash (macros F()) e SRAM (< 1.3 KB estático)
// - Combinação universal para retorno ao menu: Segurar BT5 por 1.8 segundos
// ============================================================================

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ----------------------------------------------------------------------------
// CONFIGURAÇÕES DO DISPLAY OLED (I2C)
// ----------------------------------------------------------------------------
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
#define OLED_I2C_ADDR 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// ----------------------------------------------------------------------------
// PINAGEM DO CONSOLE (UNIFICADA E COMPARTILHADA)
// ----------------------------------------------------------------------------
const uint8_t PINOS_BOTOES[5] = {2, 3, 4, 5, 6};    // BT1 a BT5 (INPUT_PULLUP)
const uint8_t PINOS_LEDS[5]   = {7, 8, 9, 10, 12};  // LED1 a LED5 (OUTPUT)
const uint8_t PINO_BUZZER     = 11;                 // Buzzer Passivo (PWM Timer 2)
const uint8_t PINO_PIEZO      = A0;                 // Sensor de Força (Punch Meter)
const uint8_t PINO_ARAME      = A1;                 // Contato do Arame (Steady Hands)
const uint8_t PINO_RANDOM     = A2;                 // Semente aleatória (Flutuante)

// Índices amigáveis dos botões
#define BT_1 0  // Vermelho / P1 / Esq
#define BT_2 1  // Verde / P2 / Cima / Anterior
#define BT_3 2  // Azul / Baixo / Próximo / Início Steady
#define BT_4 3  // Amarelo / Dir / Fim Steady
#define BT_5 4  // Branco / Select / Ação / Menu

// ----------------------------------------------------------------------------
// GERENCIADOR DE HARDWARE: ENTRADAS, SAÍDAS E ÁUDIO
// ----------------------------------------------------------------------------
class HardwareManager {
private:
  bool estadoAnterior[5];
  bool estadoAtual[5];
  unsigned long ultimoDebounce[5];
  const unsigned long tempoDebounce = 35;

public:
  void inicializar() {
    for (uint8_t i = 0; i < 5; i++) {
      pinMode(PINOS_BOTOES[i], INPUT_PULLUP);
      estadoAnterior[i] = HIGH;
      estadoAtual[i] = HIGH;
      ultimoDebounce[i] = 0;

      pinMode(PINOS_LEDS[i], OUTPUT);
      digitalWrite(PINOS_LEDS[i], LOW);
    }

    pinMode(PINO_BUZZER, OUTPUT);
    pinMode(PINO_ARAME, INPUT_PULLUP);
    pinMode(PINO_PIEZO, INPUT);

    randomSeed(analogRead(PINO_RANDOM));
  }

  void atualizarBotoes() {
    unsigned long agora = millis();
    for (uint8_t i = 0; i < 5; i++) {
      bool leitura = digitalRead(PINOS_BOTOES[i]);
      if (leitura != estadoAnterior[i]) {
        ultimoDebounce[i] = agora;
      }
      if ((agora - ultimoDebounce[i]) > tempoDebounce) {
        estadoAtual[i] = leitura;
      }
      estadoAnterior[i] = leitura;
    }
  }

  bool estaPressionado(uint8_t idx) const {
    return estadoAtual[idx] == LOW;
  }

  bool acabouDePressionar(uint8_t idx) {
    static bool ultimoEstadoEstavel[5] = {HIGH, HIGH, HIGH, HIGH, HIGH};
    bool bordaDescida = (estadoAtual[idx] == LOW && ultimoEstadoEstavel[idx] == HIGH);
    ultimoEstadoEstavel[idx] = estadoAtual[idx];
    return bordaDescida;
  }

  bool acabouDeSoltar(uint8_t idx) {
    static bool ultimoEstadoEstavel[5] = {HIGH, HIGH, HIGH, HIGH, HIGH};
    bool bordaSubida = (estadoAtual[idx] == HIGH && ultimoEstadoEstavel[idx] == LOW);
    ultimoEstadoEstavel[idx] = estadoAtual[idx];
    return bordaSubida;
  }

  void setLed(uint8_t idx, bool ligado) {
    if (idx < 5) digitalWrite(PINOS_LEDS[idx], ligado ? HIGH : LOW);
  }

  void apagarLeds() {
    for (uint8_t i = 0; i < 5; i++) digitalWrite(PINOS_LEDS[i], LOW);
  }

  void acenderLeds() {
    for (uint8_t i = 0; i < 5; i++) digitalWrite(PINOS_LEDS[i], HIGH);
  }

  void bip(uint16_t freq, uint16_t duracaoMs) {
    tone(PINO_BUZZER, freq, duracaoMs);
  }

  void somContinuo(uint16_t freq) {
    tone(PINO_BUZZER, freq);
  }

  void pararSom() {
    noTone(PINO_BUZZER);
  }

  bool leituraArame() {
    return digitalRead(PINO_ARAME) == LOW; // LOW quando encosta na argola
  }

  int leituraPiezo() {
    return analogRead(PINO_PIEZO);
  }
};

HardwareManager hw;

// ----------------------------------------------------------------------------
// INTERFACE BASE ABSTRATA DE JOGO (POLIMORFISMO E SOLID)
// ----------------------------------------------------------------------------
class Jogo {
public:
  virtual void iniciar() = 0;
  virtual void atualizar() = 0;
  virtual void encerrar() = 0;
  virtual const __FlashStringHelper* getNome() const = 0;
  virtual ~Jogo() {}
};

// ============================================================================
// JOGO 1: MEMORY MASTER (GENIUS DE 4 CORES COM NOTAS MUSICAIS)
// ============================================================================
class JogoMemoryMaster : public Jogo {
private:
  enum EstadoMM { MM_APRESENTAR, MM_TOCAR_SEQ, MM_SUA_VEZ, MM_VITORIA, MM_DERROTA, MM_AGUARDA_RESTART };
  EstadoMM estado;

  const uint16_t tons[4] = {262, 330, 392, 523}; // Dó, Mi, Sol, Dó agudo
  uint8_t sequencia[32];
  uint8_t rodadaAtual;
  uint8_t passoApresentacao;
  uint8_t passoJogador;
  uint8_t recorde;

  unsigned long timerPasso;
  unsigned long tempoLimiteEntrada;
  bool ledLigadoNaSeq;

  int calcularTempoAceso() const {
    int t = 600 - (rodadaAtual * 30);
    return t < 180 ? 180 : t;
  }

  int calcularPausa() const {
    int p = 250 - (rodadaAtual * 12);
    return p < 80 ? 80 : p;
  }

public:
  JogoMemoryMaster() : estado(MM_APRESENTAR), rodadaAtual(0), recorde(0) {}

  const __FlashStringHelper* getNome() const override {
    return F("1. Memory Master");
  }

  void iniciar() override {
    rodadaAtual = 0;
    passoJogador = 0;
    sequencia[0] = random(0, 4);
    rodadaAtual = 1;
    estado = MM_APRESENTAR;
    timerPasso = millis();

    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(16, 20);
    display.print(F("MEMORY MASTER"));
    display.setCursor(20, 36);
    display.print(F("Memorize a luz!"));
    display.display();
    delay(900);

    passoApresentacao = 0;
    ledLigadoNaSeq = false;
    estado = MM_TOCAR_SEQ;
    timerPasso = millis();
  }

  void atualizar() override {
    unsigned long agora = millis();

    switch (estado) {
      case MM_TOCAR_SEQ: {
        int tempoAceso = calcularTempoAceso();
        int pausa = calcularPausa();

        if (!ledLigadoNaSeq) {
          if (agora - timerPasso >= (unsigned long)pausa) {
            uint8_t cor = sequencia[passoApresentacao];
            hw.setLed(cor, true);
            hw.somContinuo(tons[cor]);
            ledLigadoNaSeq = true;
            timerPasso = agora;

            display.clearDisplay();
            display.setCursor(20, 10);
            display.print(F("RODADA "));
            display.print(rodadaAtual);
            display.setCursor(16, 32);
            display.print(F("OBSERVE A SEQUENCIA"));
            display.display();
          }
        } else {
          if (agora - timerPasso >= (unsigned long)tempoAceso) {
            hw.apagarLeds();
            hw.pararSom();
            ledLigadoNaSeq = false;
            timerPasso = agora;
            passoApresentacao++;

            if (passoApresentacao >= rodadaAtual) {
              passoJogador = 0;
              estado = MM_SUA_VEZ;
              tempoLimiteEntrada = agora + 5000;

              display.clearDisplay();
              display.setCursor(20, 10);
              display.print(F("RODADA "));
              display.print(rodadaAtual);
              display.setCursor(30, 32);
              display.print(F(">> SUA VEZ! <<"));
              display.display();
            }
          }
        }
        break;
      }

      case MM_SUA_VEZ: {
        if (agora > tempoLimiteEntrada) {
          estado = MM_DERROTA;
          timerPasso = agora;
          return;
        }

        // Verifica toque nos botões 1 a 4
        for (uint8_t i = 0; i < 4; i++) {
          if (hw.acabouDePressionar(i)) {
            hw.setLed(i, true);
            hw.somContinuo(tons[i]);

            if (i == sequencia[passoJogador]) {
              passoJogador++;
              tempoLimiteEntrada = agora + 5000;

              // Aguarda soltar para apagar
              while (hw.estaPressionado(i)) {
                hw.atualizarBotoes();
                delay(5);
              }
              hw.setLed(i, false);
              hw.pararSom();

              if (passoJogador >= rodadaAtual) {
                // Completou a rodada
                if (rodadaAtual >= 32) {
                  estado = MM_VITORIA;
                } else {
                  rodadaAtual++;
                  sequencia[rodadaAtual - 1] = random(0, 4);
                  passoApresentacao = 0;
                  ledLigadoNaSeq = false;
                  estado = MM_TOCAR_SEQ;
                  timerPasso = agora + 400;

                  display.clearDisplay();
                  display.setCursor(32, 28);
                  display.print(F("CORRETO!"));
                  display.display();
                  delay(400);
                }
              }
              return;
            } else {
              // Errou a cor
              while (hw.estaPressionado(i)) {
                hw.atualizarBotoes();
                delay(5);
              }
              hw.setLed(i, false);
              hw.pararSom();
              estado = MM_DERROTA;
              timerPasso = agora;
              return;
            }
          }
        }
        break;
      }

      case MM_DERROTA: {
        hw.apagarLeds();
        hw.bip(150, 600);
        for (uint8_t p = 0; p < 3; p++) {
          hw.acenderLeds();
          delay(120);
          hw.apagarLeds();
          delay(120);
        }

        uint8_t pontos = (rodadaAtual > 0) ? (rodadaAtual - 1) : 0;
        if (pontos > recorde) recorde = pontos;

        display.clearDisplay();
        display.setCursor(28, 12);
        display.print(F("FIM DE JOGO!"));
        display.setCursor(20, 30);
        display.print(F("Pontos: "));
        display.print(pontos);
        display.setCursor(20, 44);
        display.print(F("Recorde: "));
        display.print(recorde);
        display.display();

        estado = MM_AGUARDA_RESTART;
        timerPasso = agora + 2000;
        break;
      }

      case MM_VITORIA: {
        if (32 > recorde) recorde = 32;
        display.clearDisplay();
        display.setCursor(16, 20);
        display.print(F("VITORIA TOTAL!"));
        display.setCursor(20, 38);
        display.print(F("Mestre da Memoria!"));
        display.display();

        for (uint8_t i = 0; i < 4; i++) {
          hw.setLed(i, true);
          hw.bip(tons[i], 120);
          delay(140);
          hw.setLed(i, false);
        }
        hw.acenderLeds();
        hw.bip(1047, 500);
        delay(600);
        hw.apagarLeds();

        estado = MM_AGUARDA_RESTART;
        timerPasso = agora + 2000;
        break;
      }

      case MM_AGUARDA_RESTART: {
        if (agora > timerPasso) {
          iniciar();
        }
        break;
      }
    }
  }

  void encerrar() override {
    hw.apagarLeds();
    hw.pararSom();
  }
};

// ============================================================================
// JOGO 2: QUICK DRAW (DUELO DE REFLEXO PARA 2 JOGADORES)
// ============================================================================
class JogoQuickDraw : public Jogo {
private:
  enum EstadoQD { QD_PRONTOS, QD_ESPERA_LARGADA, QD_REACAO, QD_RESULTADO, QD_REINICIO };
  EstadoQD estado;

  unsigned long horaLargada;
  unsigned long tempoLimite;
  unsigned long tempoP1;
  unsigned long tempoP2;
  bool p1Pronto;
  bool p2Pronto;
  bool p1Respondeu;
  bool p2Respondeu;
  unsigned long timerAutoReinicio;

public:
  JogoQuickDraw() : estado(QD_PRONTOS) {}

  const __FlashStringHelper* getNome() const override {
    return F("2. Quick Draw");
  }

  void iniciar() override {
    hw.apagarLeds();
    hw.pararSom();
    p1Pronto = false;
    p2Pronto = false;
    p1Respondeu = false;
    p2Respondeu = false;
    tempoP1 = 0;
    tempoP2 = 0;
    estado = QD_PRONTOS;

    display.clearDisplay();
    display.setCursor(18, 12);
    display.print(F("QUICK DRAW 2P"));
    display.setCursor(12, 30);
    display.print(F("P1 [BT1] | P2 [BT2]"));
    display.setCursor(8, 46);
    display.print(F("Apertem para armar!"));
    display.display();
  }

  void atualizar() override {
    unsigned long agora = millis();
    bool btn1 = hw.estaPressionado(BT_1);
    bool btn2 = hw.estaPressionado(BT_2);

    switch (estado) {
      case QD_PRONTOS: {
        if (btn1) { p1Pronto = true; hw.setLed(0, true); }
        if (btn2) { p2Pronto = true; hw.setLed(1, true); }

        if (p1Pronto && p2Pronto && !btn1 && !btn2) {
          hw.apagarLeds();
          display.clearDisplay();
          display.setCursor(24, 28);
          display.print(F("PREPAREM-SE..."));
          display.display();

          horaLargada = agora + random(2000, 5000);
          estado = QD_ESPERA_LARGADA;
        }
        break;
      }

      case QD_ESPERA_LARGADA: {
        // Detecção de Queima de Largada
        if (btn1 || btn2) {
          hw.bip(200, 600);
          display.clearDisplay();
          display.setCursor(10, 18);
          display.print(F("QUEIMA DE LARGADA!"));
          display.setCursor(12, 38);
          if (btn1) {
            display.print(F("P1 Desclassificado"));
            hw.setLed(1, true); // P2 vence
          } else {
            display.print(F("P2 Desclassificado"));
            hw.setLed(0, true); // P1 vence
          }
          display.display();

          estado = QD_REINICIO;
          timerAutoReinicio = agora + 4000;
        } else if (agora >= horaLargada) {
          // Sinal de partida!
          hw.setLed(2, true); // LED central de partida
          hw.bip(1500, 200);
          horaLargada = agora;
          tempoLimite = agora + 4000;
          estado = QD_REACAO;

          display.clearDisplay();
          display.setCursor(28, 26);
          display.setTextSize(2);
          display.print(F("FOGO!"));
          display.setTextSize(1);
          display.display();
        }
        break;
      }

      case QD_REACAO: {
        if (btn1 && !p1Respondeu) {
          tempoP1 = agora - horaLargada;
          p1Respondeu = true;
        }
        if (btn2 && !p2Respondeu) {
          tempoP2 = agora - horaLargada;
          p2Respondeu = true;
        }

        if ((p1Respondeu && p2Respondeu) || agora > tempoLimite) {
          hw.setLed(2, false);
          estado = QD_RESULTADO;
        }
        break;
      }

      case QD_RESULTADO: {
        display.clearDisplay();
        display.setCursor(14, 8);
        display.print(F("=== RESULTADO ==="));

        display.setCursor(10, 24);
        display.print(F("P1: "));
        if (p1Respondeu) { display.print(tempoP1); display.print(F(" ms")); }
        else { display.print(F("N/A")); }

        display.setCursor(10, 36);
        display.print(F("P2: "));
        if (p2Respondeu) { display.print(tempoP2); display.print(F(" ms")); }
        else { display.print(F("N/A")); }

        display.setCursor(10, 50);
        if (p1Respondeu && (!p2Respondeu || tempoP1 < tempoP2)) {
          display.print(F("Vencedor: P1!"));
          hw.setLed(0, true);
          hw.bip(800, 400);
        } else if (p2Respondeu && (!p1Respondeu || tempoP2 < tempoP1)) {
          display.print(F("Vencedor: P2!"));
          hw.setLed(1, true);
          hw.bip(800, 400);
        } else if (p1Respondeu && p2Respondeu && tempoP1 == tempoP2) {
          display.print(F("EMPATE EXATO!"));
        } else {
          display.print(F("Nenhum atirou!"));
        }
        display.display();

        estado = QD_REINICIO;
        timerAutoReinicio = millis() + 4500;
        break;
      }

      case QD_REINICIO: {
        if (agora > timerAutoReinicio && !btn1 && !btn2) {
          iniciar();
        }
        break;
      }
    }
  }

  void encerrar() override {
    hw.apagarLeds();
    hw.pararSom();
  }
};

// ============================================================================
// JOGO 3: PUNCH METER (MEDIDOR DE FORÇA COM SENSOR PIEZOELÉTRICO)
// ============================================================================
class JogoPunchMeter : public Jogo {
private:
  enum EstadoPM { PM_AGUARDANDO, PM_CAPTURANDO, PM_MOSTRAR, PM_ESPERA };
  EstadoPM estado;

  int picoMaximo;
  int recorde;
  unsigned long inicioJanela;
  unsigned long timerResultado;

public:
  JogoPunchMeter() : estado(PM_AGUARDANDO), picoMaximo(0), recorde(0) {}

  const __FlashStringHelper* getNome() const override {
    return F("3. Punch Meter");
  }

  void iniciar() override {
    hw.apagarLeds();
    hw.pararSom();
    estado = PM_AGUARDANDO;
    picoMaximo = 0;

    display.clearDisplay();
    display.setCursor(20, 14);
    display.print(F("PUNCH METER"));
    display.setCursor(14, 30);
    display.print(F("Acerte o alvo!"));
    display.setCursor(14, 46);
    display.print(F("Aguardando impacto"));
    display.display();
  }

  void atualizar() override {
    unsigned long agora = millis();
    int leitura = hw.leituraPiezo();

    switch (estado) {
      case PM_AGUARDANDO: {
        if (leitura >= 30) {
          picoMaximo = leitura;
          inicioJanela = agora;
          estado = PM_CAPTURANDO;
        }
        break;
      }

      case PM_CAPTURANDO: {
        if (leitura > picoMaximo) picoMaximo = leitura;

        if (agora - inicioJanela >= 50) {
          int pontos = map(picoMaximo, 30, 1023, 50, 1000);
          pontos = constrain(pontos, 0, 1000);
          uint8_t nivel = constrain((pontos + 199) / 200, 1, 5);

          hw.apagarLeds();
          for (uint8_t i = 0; i < nivel; i++) {
            hw.setLed(i, true);
            hw.bip(500 + (i * 250), 100);
            delay(120);
          }

          bool novoRecorde = false;
          if (pontos > recorde) {
            recorde = pontos;
            novoRecorde = true;
          }

          display.clearDisplay();
          display.setCursor(18, 8);
          display.print(F("PUNCH METER"));
          display.setCursor(10, 24);
          display.print(F("Pontos: "));
          display.print(pontos);

          display.setCursor(10, 38);
          display.print(F("Nivel: "));
          if (nivel == 1) display.print(F("FRACO"));
          else if (nivel == 2) display.print(F("MEDIO"));
          else if (nivel == 3) display.print(F("FORTE"));
          else if (nivel == 4) display.print(F("M.FORTE"));
          else display.print(F("EXTREMO!"));

          display.setCursor(10, 52);
          display.print(F("Recorde: "));
          display.print(recorde);
          if (novoRecorde) display.print(F(" *NOVO*"));
          display.display();

          if (novoRecorde) {
            hw.bip(1500, 150); delay(180);
            hw.bip(2000, 150); delay(180);
            hw.bip(2500, 350);
          } else {
            hw.bip(1000, 250);
          }

          timerResultado = agora + 4500;
          estado = PM_ESPERA;
        }
        break;
      }

      case PM_ESPERA: {
        if (agora > timerResultado) {
          iniciar();
        }
        break;
      }
    }
  }

  void encerrar() override {
    hw.apagarLeds();
    hw.pararSom();
  }
};

// ============================================================================
// JOGO 4: STEADY HANDS (TESTE DE PRECISÃO / MÃO FIRME NO ARAME)
// ============================================================================
class JogoSteadyHands : public Jogo {
private:
  enum EstadoSH { SH_ESPERA_INICIO, SH_JOGANDO, SH_RESULTADO, SH_PAUSA };
  EstadoSH estado;

  uint8_t vidas;
  unsigned long inicioPartida;
  unsigned long tempoDecorrido;
  unsigned long recordeTempo;
  unsigned long ultimoErro;
  bool contatoAnterior;
  unsigned long timerPausa;

  void atualizarLedsVidas() {
    hw.setLed(0, vidas >= 1);
    hw.setLed(1, vidas >= 2);
    hw.setLed(2, vidas >= 3);
  }

public:
  JogoSteadyHands() : estado(SH_ESPERA_INICIO), vidas(3), recordeTempo(0) {}

  const __FlashStringHelper* getNome() const override {
    return F("4. Steady Hands");
  }

  void iniciar() override {
    hw.apagarLeds();
    hw.pararSom();
    vidas = 3;
    contatoAnterior = false;
    estado = SH_ESPERA_INICIO;

    atualizarLedsVidas();
    display.clearDisplay();
    display.setCursor(18, 12);
    display.print(F("STEADY HANDS"));
    display.setCursor(14, 30);
    display.print(F("Aperte [BT3] p/"));
    display.setCursor(14, 44);
    display.print(F("iniciar percurso"));
    display.display();
  }

  void atualizar() override {
    unsigned long agora = millis();

    switch (estado) {
      case SH_ESPERA_INICIO: {
        if (hw.acabouDePressionar(BT_3)) {
          vidas = 3;
          atualizarLedsVidas();
          hw.setLed(3, true); // LED de partida ativa
          hw.bip(1200, 200);

          inicioPartida = agora;
          ultimoErro = agora;
          contatoAnterior = false;
          estado = SH_JOGANDO;

          display.clearDisplay();
          display.setCursor(16, 16);
          display.print(F("PERCURSO ATIVO!"));
          display.setCursor(16, 34);
          display.print(F("Vidas: 3"));
          display.display();
        }
        break;
      }

      case SH_JOGANDO: {
        bool contato = hw.leituraArame();
        hw.setLed(4, contato); // LED de erro acende em contato

        // Detecta novo toque com debounce
        if (contato && !contatoAnterior) {
          if (agora - ultimoErro >= 80) {
            ultimoErro = agora;
            if (vidas > 0) vidas--;
            atualizarLedsVidas();
            hw.bip(400, 250);

            display.clearDisplay();
            display.setCursor(20, 16);
            display.print(F("TOQUE NO ARAME!"));
            display.setCursor(20, 36);
            display.print(F("Vidas restantes: "));
            display.print(vidas);
            display.display();

            if (vidas == 0) {
              // Derrota
              tempoDecorrido = agora - inicioPartida;
              hw.setLed(3, false);
              hw.bip(300, 600);

              display.clearDisplay();
              display.setCursor(24, 20);
              display.print(F("GAME OVER!"));
              display.setCursor(12, 38);
              display.print(F("Vidas esgotadas!"));
              display.display();

              estado = SH_PAUSA;
              timerPausa = agora + 4000;
              return;
            }
          }
        }
        contatoAnterior = contato;

        // Conclusão do percurso apertando BT4 (Fim) sem estar em contato
        if (hw.acabouDePressionar(BT_4) && !contato) {
          tempoDecorrido = agora - inicioPartida;
          hw.setLed(3, false);

          bool novoRecorde = false;
          if (recordeTempo == 0 || tempoDecorrido < recordeTempo) {
            recordeTempo = tempoDecorrido;
            novoRecorde = true;
          }

          display.clearDisplay();
          display.setCursor(16, 10);
          display.print(F("CONCLUIDO!"));
          display.setCursor(10, 26);
          display.print(F("Tempo: "));
          display.print(tempoDecorrido / 1000.0, 2);
          display.print(F(" s"));

          display.setCursor(10, 40);
          display.print(F("Erros: "));
          display.print(3 - vidas);

          display.setCursor(10, 54);
          display.print(F("Rec: "));
          display.print(recordeTempo / 1000.0, 2);
          display.print(F(" s"));
          display.display();

          if (novoRecorde) {
            hw.bip(1500, 150); delay(180);
            hw.bip(2000, 200);
          } else {
            hw.bip(1800, 400);
          }

          estado = SH_PAUSA;
          timerPausa = agora + 4500;
        }
        break;
      }

      case SH_PAUSA: {
        if (agora > timerPausa) {
          iniciar();
        }
        break;
      }
    }
  }

  void encerrar() override {
    hw.apagarLeds();
    hw.pararSom();
  }
};

// ============================================================================
// JOGO 5: CAMPO MINADO (MINEFIELD COM 5 POSIÇÕES E 2 MINAS)
// ============================================================================
class JogoCampoMinado : public Jogo {
private:
  bool minas[5];
  bool descobertos[5];
  uint8_t acertosSeguros;
  bool fimDeJogo;
  unsigned long timerFim;

public:
  JogoCampoMinado() : acertosSeguros(0), fimDeJogo(false) {}

  const __FlashStringHelper* getNome() const override {
    return F("5. Campo Minado");
  }

  void iniciar() override {
    hw.apagarLeds();
    hw.pararSom();
    acertosSeguros = 0;
    fimDeJogo = false;

    for (uint8_t i = 0; i < 5; i++) {
      minas[i] = false;
      descobertos[i] = false;
    }

    // Sorteia exatamente 2 minas em 5 posições
    uint8_t minasColocadas = 0;
    while (minasColocadas < 2) {
      uint8_t pos = random(0, 5);
      if (!minas[pos]) {
        minas[pos] = true;
        minasColocadas++;
      }
    }

    display.clearDisplay();
    display.setCursor(20, 10);
    display.print(F("CAMPO MINADO"));
    display.setCursor(8, 28);
    display.print(F("Ache 3 caminhos!"));
    display.setCursor(8, 44);
    display.print(F("Cuidado: 2 minas"));
    display.display();
  }

  void atualizar() override {
    unsigned long agora = millis();

    if (fimDeJogo) {
      if (agora > timerFim) {
        iniciar();
      }
      return;
    }

    // Verifica botões 1 a 5
    for (uint8_t i = 0; i < 5; i++) {
      if (hw.acabouDePressionar(i)) {
        if (descobertos[i]) return; // Já escolhido

        descobertos[i] = true;

        if (minas[i]) {
          // Explodiu mina!
          fimDeJogo = true;
          timerFim = agora + 4000;
          hw.setLed(i, true);
          hw.bip(150, 800);

          display.clearDisplay();
          display.setCursor(24, 18);
          display.print(F("BOOOOM!"));
          display.setCursor(14, 36);
          display.print(F("Voce pisou na mina"));
          display.display();

          for (uint8_t b = 0; b < 3; b++) {
            hw.acenderLeds(); delay(100);
            hw.apagarLeds(); delay(100);
          }
        } else {
          // Seguro!
          acertosSeguros++;
          hw.setLed(i, true);
          hw.bip(1000, 150);

          display.clearDisplay();
          display.setCursor(16, 16);
          display.print(F("CAMINHO SEGURO!"));
          display.setCursor(24, 36);
          display.print(F("Seguros: "));
          display.print(acertosSeguros);
          display.print(F(" / 3"));
          display.display();

          if (acertosSeguros >= 3) {
            // Vitória total
            fimDeJogo = true;
            timerFim = agora + 4500;
            delay(200);
            hw.bip(1500, 600);

            display.clearDisplay();
            display.setCursor(20, 16);
            display.print(F("PARABENS!"));
            display.setCursor(14, 36);
            display.print(F("Campo desarmado!"));
            display.display();

            for (uint8_t v = 0; v < 3; v++) {
              hw.acenderLeds(); delay(120);
              hw.apagarLeds(); delay(120);
            }
          }
        }
        return;
      }
    }
  }

  void encerrar() override {
    hw.apagarLeds();
    hw.pararSom();
  }
};

// ============================================================================
// GERENCIADOR CENTRAL DO CONSOLE E MENU PRINCIPAL
// ============================================================================
enum EstadoConsole {
  CONSOLE_MENU,
  CONSOLE_JOGANDO
};

EstadoConsole estadoConsole = CONSOLE_MENU;
int8_t indiceMenu = 0;
const uint8_t TOTAL_JOGOS = 5;

// Instâncias estáticas dos jogos (sem alocação dinâmica com new/delete)
JogoMemoryMaster  jogoMM;
JogoQuickDraw     jogoQD;
JogoPunchMeter    jogoPM;
JogoSteadyHands   jogoSH;
JogoCampoMinado   jogoCM;

Jogo* jogos[TOTAL_JOGOS] = {
  &jogoMM,
  &jogoQD,
  &jogoPM,
  &jogoSH,
  &jogoCM
};

unsigned long inicioPressaoBT5 = 0;

void desenharMenu() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);

  // Cabeçalho
  display.setCursor(24, 2);
  display.print(F("= TECH ARCADE ="));
  display.drawFastHLine(0, 12, 128, SSD1306_WHITE);

  // Lista com 5 jogos
  for (uint8_t i = 0; i < TOTAL_JOGOS; i++) {
    uint8_t y = 16 + (i * 9);
    if (i == indiceMenu) {
      display.fillRect(0, y - 1, 128, 9, SSD1306_WHITE);
      display.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
      display.setCursor(4, y);
      display.print(F("> "));
      display.print(jogos[i]->getNome());
    } else {
      display.setTextColor(SSD1306_WHITE);
      display.setCursor(8, y);
      display.print(jogos[i]->getNome());
    }
  }

  display.display();
}

// ============================================================================
// ARDUINO SETUP & LOOP
// ============================================================================
void setup() {
  Serial.begin(9600);
  hw.inicializar();

  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDR)) {
    // Fallback caso I2C não responda
    while (true) {
      hw.setLed(0, true); delay(200); hw.setLed(0, false); delay(200);
    }
  }

  // Animação de Inicialização
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(28, 16);
  display.print(F("TECH ARCADE"));
  display.setCursor(16, 32);
  display.print(F("Mini Console v1.0"));
  display.setCursor(20, 48);
  display.print(F("Inicializando..."));
  display.display();

  for (uint8_t i = 0; i < 5; i++) {
    hw.setLed(i, true);
    hw.bip(300 + (i * 200), 80);
    delay(100);
    hw.setLed(i, false);
  }
  delay(500);

  estadoConsole = CONSOLE_MENU;
  desenharMenu();
}

void loop() {
  hw.atualizarBotoes();

  // --------------------------------------------------------------------------
  // CONTROLE DO RETORNO UNIVERSAL AO MENU (Segurar BT5 por 1.8 segundos)
  // --------------------------------------------------------------------------
  if (hw.estaPressionado(BT_5)) {
    if (inicioPressaoBT5 == 0) {
      inicioPressaoBT5 = millis();
    } else if (millis() - inicioPressaoBT5 >= 1800) {
      // Dispara retorno ao menu principal
      if (estadoConsole == CONSOLE_JOGANDO) {
        jogos[indiceMenu]->encerrar();
        hw.apagarLeds();
        hw.bip(400, 200);
        delay(220);
        hw.bip(250, 400);

        display.clearDisplay();
        display.setCursor(18, 26);
        display.print(F("VOLTANDO AO MENU..."));
        display.display();
        delay(700);

        estadoConsole = CONSOLE_MENU;
        desenharMenu();
        inicioPressaoBT5 = 0;
        return;
      }
    }
  } else {
    inicioPressaoBT5 = 0;
  }

  // --------------------------------------------------------------------------
  // MÁQUINA DE ESTADOS DO CONSOLE
  // --------------------------------------------------------------------------
  if (estadoConsole == CONSOLE_MENU) {
    // Navegação com BT2 (Cima) e BT3 (Baixo)
    if (hw.acabouDePressionar(BT_2)) {
      indiceMenu--;
      if (indiceMenu < 0) indiceMenu = TOTAL_JOGOS - 1;
      hw.bip(1200, 25);
      desenharMenu();
    }
    else if (hw.acabouDePressionar(BT_3)) {
      indiceMenu++;
      if (indiceMenu >= TOTAL_JOGOS) indiceMenu = 0;
      hw.bip(900, 25);
      desenharMenu();
    }
    // Confirmação com BT5 (Select)
    else if (hw.acabouDePressionar(BT_5)) {
      hw.bip(1600, 80);
      delay(90);
      hw.bip(2000, 150);

      estadoConsole = CONSOLE_JOGANDO;
      jogos[indiceMenu]->iniciar();
    }
  }
  else if (estadoConsole == CONSOLE_JOGANDO) {
    // Execução modular do jogo ativo
    jogos[indiceMenu]->atualizar();
  }
}
