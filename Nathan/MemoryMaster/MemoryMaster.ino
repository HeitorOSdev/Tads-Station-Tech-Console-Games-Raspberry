//Mapeamento dos pinos
#define pin_bt1 13
#define pin_bt2 12
#define pin_bt3 11
#define pin_led1 7
#define pin_led2 6
#define pin_led3 5
#define pin_buzzer 3

//Mapeamento das notas do buzzer
#define C5     523
#define D5     587
#define E5     659
#define B4     493
#define A_sus4 466 
#define A4     440

//Variáveis globais
int number_random = 0;         
int memory_number[100];          
int memory_position = 0;         
int botao_position = 0;          

//Flags dos botões
bool flag1 = 0;
bool flag2 = 0;
bool flag3 = 0;


void ler_botoes();
void acender_led(int n);
bool validar_execucao();
void mostrar_sequencia_leds();
int random_generator();
void end_game();

void setup() {

  pinMode(pin_bt1,INPUT_PULLUP);
  pinMode(pin_bt2,INPUT_PULLUP);
  pinMode(pin_bt3,INPUT_PULLUP);

  
  pinMode(pin_led1,OUTPUT);
  pinMode(pin_led2,OUTPUT);
  pinMode(pin_led3,OUTPUT);

  randomSeed(analogRead(A0));

  for(int i=0; i<100; i++){
    memory_number[i] = 0;  
  }

  number_random = random_generator();               
  memory_number[memory_position] = number_random;   
  acender_led(number_random);                       
}

void loop() {

  if(validar_execucao() == 1){
    delay(200);
    memory_position += 1; 
    number_random = random_generator();
    memory_number[memory_position] = number_random;

    mostrar_sequencia_leds();
  }
}

//Função para ler botões
void ler_botoes(){
  if(!digitalRead(pin_bt1)){
    flag1 = 1;  
    delay(30);
  }

  if(!digitalRead(pin_bt2)){
    flag2 = 1;  
    delay(30);
  }

  if(!digitalRead(pin_bt3)){
    flag3 = 1;  
    delay(30);
  }
  
  if(digitalRead(pin_bt1) && flag1){
    flag1 = 0;
    acender_led(1);
    delay(30);
    botao_position = 1;
  } 

  if(digitalRead(pin_bt2) && flag2){
    flag2 = 0;
    acender_led(2);
    delay(30);
    botao_position = 2;
  } 

  if(digitalRead(pin_bt3) && flag3){
    flag3 = 0;
    acender_led(3);
    delay(30);
    botao_position = 3;
  }
}


void acender_led(int n){
  if(n==1){
    digitalWrite(pin_led1,HIGH);
    digitalWrite(pin_led2,LOW);  
    digitalWrite(pin_led3,LOW);
    tone(pin_buzzer,C5);
    delay(250);
    noTone(pin_buzzer);
    digitalWrite(pin_led1,LOW);
    digitalWrite(pin_led2,LOW);  
    digitalWrite(pin_led3,LOW);
    delay(250);
  }
  else if(n==2){
    digitalWrite(pin_led1,LOW);
    digitalWrite(pin_led2,HIGH);  
    digitalWrite(pin_led3,LOW); 
    tone(pin_buzzer,D5);
    delay(250);
    noTone(pin_buzzer);
    digitalWrite(pin_led1,LOW);
    digitalWrite(pin_led2,LOW);  
    digitalWrite(pin_led3,LOW);
    delay(250);
  } 
  else if(n==3){
    digitalWrite(pin_led1,LOW);
    digitalWrite(pin_led2,LOW);  
    digitalWrite(pin_led3,HIGH); 
    tone(pin_buzzer,E5);
    delay(250);
    noTone(pin_buzzer);
    digitalWrite(pin_led1,LOW);
    digitalWrite(pin_led2,LOW);  
    digitalWrite(pin_led3,LOW);
    delay(250);
  }   
}


bool validar_execucao(){
  int varredura = 0;
  while(varredura < 100){
    ler_botoes();
    if (botao_position != 0){
      if(memory_number[varredura] != botao_position){
        botao_position = 0;
        end_game();
        return 0;
        break;
      }  
       else{
        varredura += 1; 
        botao_position = 0;
       }
    }

    if(memory_number[varredura] == 0){
      return 1;
      break;  
    }
  }
}


void mostrar_sequencia_leds(){
  for(int i=0; i<100; i++){
    if (memory_number[i] != 0){
      acender_led(memory_number[i]);
    }else{
      break; 
     }  
  }  
}


int random_generator(){
  int num = 0;
  int media = 0;
  for(int i=0; i<10; i++){
    num += random(0,1000);  
  }

  media = num/10;
  media = (media%3)+1;

  return media;
}


void end_game(){
  int tempo = 2000;

  tone(pin_buzzer, C5);
  delay(tempo/12);
  tone(pin_buzzer, B4);
  delay(tempo/12);
  tone(pin_buzzer, A_sus4);
  delay(tempo/12);

  tone(pin_buzzer, A4);
  delay(tempo/2);
  noTone(pin_buzzer);

  for(int i=0; i<100; i++){
    memory_number[i] = 0;  
  }

  memory_position = 0;

  delay(1000);
  number_random = random_generator();
  memory_number[memory_position] = number_random;
  acender_led(memory_number[memory_position]);
}
