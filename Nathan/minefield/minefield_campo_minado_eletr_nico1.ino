// Mapeamento dos pinos
#define pin_bt1 13
#define pin_bt2 12
#define pin_bt3 11
#define pin_bt4 10
#define pin_bt5 9

#define pin_led1 6 //Vermelho
#define pin_led2 5 //Azul
#define pin_led3 4 //Cinza 
#define pin_led4 3 //Amarelo
#define pin_led5 2 //Verde

#define pin_buzzer 7

// Variaveis globais
bool minas[5];
bool utilizados[5];

int botao_position = 0;
int quantidade_minas = 2;
int caminhos_seguros = 0;

bool flag1 = 0;
bool flag2 = 0;
bool flag3 = 0;
bool flag4 = 0;
bool flag5 = 0;

bool fim_de_jogo = 0;

// Prototipos das funcoes
void ler_botoes();
void acender_led(int n);
void apagar_leds();
void gerar_minas();
void validar_execucao();
void end_game();

// Configuracao inicial
void setup() {

  pinMode(pin_bt1, INPUT_PULLUP);
  pinMode(pin_bt2, INPUT_PULLUP);
  pinMode(pin_bt3, INPUT_PULLUP);
  pinMode(pin_bt4, INPUT_PULLUP);
  pinMode(pin_bt5, INPUT_PULLUP);

  pinMode(pin_led1, OUTPUT);
  pinMode(pin_led2, OUTPUT);
  pinMode(pin_led3, OUTPUT);
  pinMode(pin_led4, OUTPUT);
  pinMode(pin_led5, OUTPUT);
  
  pinMode(pin_buzzer, OUTPUT);
  randomSeed(analogRead(A0));
  Serial.begin(9600);
  gerar_minas();
  Serial.println("MINEFIELD");
  Serial.println("Encontre os 3 caminhos seguros!");
}

// Loop principal
void loop() {
  if (!fim_de_jogo) {
    ler_botoes();
    validar_execucao();
  }

  else {
    end_game();
    delay(5000);
    gerar_minas();
    fim_de_jogo = 0;
    caminhos_seguros = 0;
    apagar_leds();
    Serial.println("NOVO JOGO!");
  }
}

// Funcao para ler os botoes
void ler_botoes() {

  if (!digitalRead(pin_bt1)) {
    flag1 = 1;
    delay(30);
  }

  if (!digitalRead(pin_bt2)) {
    flag2 = 1;
    delay(30);
  }

  if (!digitalRead(pin_bt3)) {
    flag3 = 1;
    delay(30);
  }

  if (!digitalRead(pin_bt4)) {
    flag4 = 1;
    delay(30);
  }

  if (!digitalRead(pin_bt5)) {
    flag5 = 1;
    delay(30);
  }

  if (digitalRead(pin_bt1) && flag1) {
    flag1 = 0;
    botao_position = 1;
  }

  if (digitalRead(pin_bt2) && flag2) {
    flag2 = 0;
    botao_position = 2;
  }

  if (digitalRead(pin_bt3) && flag3) {
    flag3 = 0;
    botao_position = 3;
  }

  if (digitalRead(pin_bt4) && flag4) {
    flag4 = 0;
    botao_position = 4;
  }

  if (digitalRead(pin_bt5) && flag5) {
    flag5 = 0;
    botao_position = 5;
  }
}

// Funcao para acender o LED
void acender_led(int n) {
  if (n == 1) digitalWrite(pin_led1, HIGH);
  if (n == 2) digitalWrite(pin_led2, HIGH);
  if (n == 3) digitalWrite(pin_led3, HIGH);
  if (n == 4) digitalWrite(pin_led4, HIGH);
  if (n == 5) digitalWrite(pin_led5, HIGH);
}

// Funcao para apagar os LEDs
void apagar_leds() {
  digitalWrite(pin_led1, LOW);
  digitalWrite(pin_led2, LOW);
  digitalWrite(pin_led3, LOW);
  digitalWrite(pin_led4, LOW);
  digitalWrite(pin_led5, LOW);
}

// Funcao para gerar as minas
void gerar_minas() {

  for (int i = 0; i < 5; i++) {
    minas[i] = 0;
    utilizados[i] = 0;
  }

  int contador = 0;

  while (contador < quantidade_minas) {
    int posicao = random(0, 5);
    if (!minas[posicao]) {
      minas[posicao] = 1;
      contador++;
    }
  }
}

// Funcao para validar a jogada
void validar_execucao() {
  if (botao_position == 0) return;
  int posicao = botao_position - 1;
  botao_position = 0;
  if (utilizados[posicao]) {
    return;
  }
  
  utilizados[posicao] = 1;
  if (minas[posicao]) {
    Serial.println("BOOM! VOCE ENCONTROU UMA MINA!");
    tone(pin_buzzer, 150, 1000);
    fim_de_jogo = 1;

  } else {
    caminhos_seguros++;
    acender_led(posicao + 1);
    Serial.println("CAMINHO SEGURO!");
    Serial.print("Caminhos seguros: ");
    Serial.println(caminhos_seguros);
    tone(pin_buzzer, 1000, 150);

    if (caminhos_seguros == 3) {
      Serial.println("PARABENS! VOCE VENCEU!");
      fim_de_jogo = 1;
    }
  }
}

// Funcao para encerrar o jogo
void end_game() {

  if (caminhos_seguros == 3) {
    Serial.println("VOCE VENCEU!");
    tone(pin_buzzer, 1500, 1000);

  } else {
    Serial.println("VOCE PERDEU!");
    tone(pin_buzzer, 200, 1000);
  }
}
