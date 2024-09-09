const int MAX_MESSAGE_LENGTH = 16;
char message[MAX_MESSAGE_LENGTH];
int nextPosition = 0;

const int NUM_LEDS = 4;
const int ledPins[NUM_LEDS] = {10, 5, 6, 9};

const int MAX_VALUE = 2000;

void setup() {
  Serial.begin(9600);

  for (int i = 0; i < NUM_LEDS; i++) {
    pinMode(ledPins[i], OUTPUT);
  }
}

void loop() {
  while (Serial.available() > 0) { // シリアル通信でデータが送られてきている
    char c = Serial.read(); // 1文字読み込む
    if (c != '\n') { // 終端でなければ
      message[nextPosition++] = c; // メッセージとしてたくわえる
    } else { // 終端なので，文字列を解釈して，処理を行う
      message[nextPosition] = 0; // 終端記号を加える

      // a1234'\0'
      // 先頭は対象LED(a/b/c)
      int ledNum = message[0] - 'a'; // 0から2に変換
      // 2文字目以降は数値
      // message + 1 は，2文字目から(終端0までの)文字列
      int value = String(message + 1).toInt(); 

      // 値を送信して，正しく値を得られているかを確認
      Serial.print(ledNum);
      Serial.print(' ');
      Serial.println(value);

      if (ledNum >= 0 && value >= 0 && value <= MAX_VALUE) {
        switch(ledNum){
          case 0:
            for(int i = 0; i < NUM_LEDS; i++){
              if(i != ledNum){
                digitalWrite(ledPins[i], LOW);
              }
            }
            // value * 255 としてしまうと，乗算の段階で2バイト整数の上限を超えて値が小さくなる
            // 危険性があるためlongに変換してから計算する必要がある
            analogWrite(ledPins[ledNum], (long)(value) * 255 / MAX_VALUE);
            break;
            
          case 1:
            for(int i = 0; i < NUM_LEDS; i++){
              if(i != ledNum){
                digitalWrite(ledPins[i], LOW);
              }
            }
            analogWrite(ledPins[ledNum], (long)(value) * 255 / MAX_VALUE);
            break;
            
          case 2:
            for(int i = 0; i < NUM_LEDS; i++){
              if(i != ledNum){
                digitalWrite(ledPins[i], LOW);
              }
            }
            analogWrite(ledPins[ledNum], (long)(value) * 255 / MAX_VALUE);
            break;

          case 3:
            for(int i = 0; i < NUM_LEDS; i++){
              if(i != ledNum){
                digitalWrite(ledPins[i], LOW);
              }
            }
            analogWrite(ledPins[ledNum], (long)(value) * 255 / MAX_VALUE);
            break;
            
          default:
            for(int i = 0; i < NUM_LEDS; i++){
              digitalWrite(ledPins[i], LOW);
            }
            break;
        }
      }
      else {
        for(int i = 0; i < NUM_LEDS; i++){
          digitalWrite(ledPins[i], LOW);
        }
      }

      // バッファを先頭から使うように初期化
      nextPosition = 0;
    }
  }
}
