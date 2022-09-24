#define TINY_GSM_MODEM_SIM7080
#define TINY_GSM_RX_BUFFER 650  // なくても動いたけど、あったほうが安定する気がする
#define TINY_GSM_YIELD() { delay(2); } // なくても動いたけど、あったほうが安定する気がする
#include <TinyGsmClient.h>
#include <PubSubClient.h>

#include <M5Stack.h>
#include "mqtt-config.h"

const char apn[]      = "povo.jp";
const char* broker = MY_BROKER;

const char* topicTest       = "eltres";
#define GSM_AUTOBAUD_MIN 9600
#define GSM_AUTOBAUD_MAX 115200

// TinyGsmClient
TinyGsm        modem(Serial1);
TinyGsmClient  client(modem);
PubSubClient  mqtt(client);

uint32_t lastReconnectAttempt = 0;

void mqttCallback(char* topic, byte* payload, unsigned int len) {
  M5.Lcd.clear(BLACK);
  M5.Lcd.setCursor(0, 0);
  M5.Lcd.print("Message arrived [");
  M5.Lcd.print(topic);
  M5.Lcd.println("]: ");
  M5.Lcd.print("bin:");
  for(int i = 0;i < len;i++){
    M5.Lcd.print(payload[i]);
  }
  M5.Lcd.println();

  char payloadBuf[256] = {0};
  strncpy(payloadBuf,(const char *)payload,len);
  
  String str = String(payloadBuf);
  M5.Lcd.print("str:");
  M5.Lcd.println(str);

  M5.Lcd.print("Message send to ");
  M5.Lcd.println(str);

  char buf[256];
  str.toCharArray(buf, 256);
}

boolean mqttConnect() {
  M5.Lcd.print("Connecting to ");
  M5.Lcd.println(broker);

  // Connect to MQTT Broker
  boolean status = mqtt.connect("GsmClientTest");

  // Or, if you want to authenticate MQTT:
  // boolean status = mqtt.connect("GsmClientName", "mqtt_user", "mqtt_pass");

  if (status == false) {
    M5.Lcd.println(" fail");
    return false;
  }
  M5.Lcd.println(" success");
  mqtt.subscribe(topicTest);
  return mqtt.connected();
}

/* After M5Core is started or reset
the program in the setUp () function will be run, and this part will only be run once.
在 M5Core 启动或者复位后，即会开始执行setup()函数中的程序，该部分只会执行一次。 */
void setup(){
  M5.begin();  //Init M5Core.  初始化 M5Core
  M5.Lcd.setTextSize(2);
  M5.Power.begin(); //Init Power module.  初始化电源模块
                    /* Power chip connected to gpio21, gpio22, I2C device
                      Set battery charging voltage and current
                      If used battery, please call this function in your project */
  Serial1.begin(9600, SERIAL_8N1, 16, 17);

  M5.Lcd.println("Wait...");  // Print text on the screen (string) 在屏幕上打印文本(字符串)
  // Set GSM module baud rate

  // モデムのリスタート
  M5.Lcd.println("Initializing modem...");  // Print text on the screen (string) 在屏幕上打印文本(字符串)
  modem.restart();

  // モデムの情報の取得
  String modemInfo = modem.getModemInfo();
  M5.Lcd.print("Modem Info: ");
  M5.Lcd.println(modemInfo);


  // GPRS connection parameters are usually set after network registration
  M5.Lcd.print(F("Connecting to "));
  M5.Lcd.print(apn);
  if (!modem.gprsConnect(apn, "", "")) {
    M5.Lcd.println("-> fail");
    delay(10000);
    return;
  }
  M5.Lcd.println("-> success");

  if (modem.isGprsConnected()) { M5.Lcd.println("GPRS connected"); }

  // ★参考ページ:https://github.com/vshymanskyy/TinyGSM/blob/master/examples/MqttClient/MqttClient.ino
  mqtt.setServer(broker, 1883);
  mqtt.setCallback(mqttCallback);

}

/* After the program in setup() runs, it runs the program in loop()
The loop() function is an infinite loop in which the program runs repeatedly
在setup()函数中的程序执行完后，会接着执行loop()函数中的程序
loop()函数是一个死循环，其中的程序会不断的重复运行 */
void loop() {
  // Make sure we're still registered on the network
  if (!modem.isNetworkConnected()) {
      M5.Lcd.println("Network disconnected");
      
      if (!modem.waitForNetwork(180000L, true)) {
        M5.Lcd.println(" fail");
        delay(10000);
        return;
      }
      
      if (modem.isNetworkConnected()) {
        M5.Lcd.println("Network re-connected");
      }
      
      // and make sure GPRS/EPS is still connected
      if (!modem.isGprsConnected()) {
        M5.Lcd.println("GPRS disconnected!");
        M5.Lcd.print(F("Connecting to "));
        M5.Lcd.print(apn);
        if (!modem.gprsConnect(apn, "", "")) {
          M5.Lcd.println(" fail");
          delay(10000);
          return;
        }
        if (modem.isGprsConnected()) { M5.Lcd.println("GPRS reconnected"); }
      }
  }
      
  if (!mqtt.connected()) {
    M5.Lcd.println("=== MQTT NOT CONNECTED ===");
    // Reconnect every 10 seconds
    uint32_t t = millis();
    if (t - lastReconnectAttempt > 10000L) {
      lastReconnectAttempt = t;
      if (mqttConnect()) { lastReconnectAttempt = 0; }
    }
    delay(100);
    return;
  }
  
  mqtt.loop();
}
