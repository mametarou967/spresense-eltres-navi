# target path
path = "c:/XXX"
url = "YYY.com"


#import
import os
import csv
import json
import paho.mqtt.client as mqtt     # MQTTのライブラリをインポート
from time import sleep              # 3秒間のウェイトのために使う

class TudeValue:
    def __init__( self,degrees,minutes,seconds):
        self.degrees = degrees
        self.minutes = minutes
        self.seconds = seconds

class GpsDataSet:
    def __init__( self, latDegrees , latMinutesSeconds, longDegrees,longMinutesSeconds, timeStamp) :
        latMinuts,latSeconds = latMinutesSeconds.split('.')
        self.latitude = TudeValue(latDegrees,latMinuts,latSeconds)
        longMinuts,longSeconds = longMinutesSeconds.split('.')
        self.longitude = TudeValue(longDegrees,longMinuts,longSeconds)
        self.timeStamp = timeStamp


# 与えられたフォルダから最新のCSVファイルのフルパスを取得
def getLatestCsvFile(folderPath):
    filePath = None
    files = os.listdir(folderPath)
    for item in files:
        itemFilePath = path + "/" + item            # 該当のファイルのフルパスを取得
        root, ext = os.path.splitext(itemFilePath)  # extに拡張子の取出
        if ext != ".csv":                           # .csvファイル以外は対象から除外
            continue

        ts = os.path.getmtime(itemFilePath)
        if filePath is None:
            filePath = itemFilePath
        else :
            latestFileTs = os.path.getmtime(filePath)
            fileTs = os.path.getmtime(itemFilePath)
            if(latestFileTs - fileTs > 0):
                filePath = itemFilePath
    return filePath

def getLastestGpsData(csvFilePath):
    with open(csvFilePath, "r", encoding="UTF-8", errors="", newline="" ) as csvFile:
        reader = csv.reader(csvFile)
        csvList = [row for row in reader]
    
    latDegrees,latMinutesSeconds,longDegrees,longMinutesSeconds = csvList[1][8].split(' ')
    return GpsDataSet(latDegrees,latMinutesSeconds,longDegrees,longMinutesSeconds,csvList[1][9])

def getGpsDataJson(gpsDataSet):
    latitude = round(
        float(gpsDataSet.latitude.degrees) + 
        ((float(gpsDataSet.latitude.minutes) + float(gpsDataSet.latitude.seconds) / 6000) / 60)
        ,6)
    longtiude = round(
        float(gpsDataSet.longitude.degrees) + 
        ((float(gpsDataSet.longitude.minutes) + float(gpsDataSet.longitude.seconds) / 6000) / 60)
        ,6)
    
    print(latitude)
    print(longtiude)
    obj = {
        "latitude" : latitude,
        "longtiude" : longtiude,
        "timeStamp" : gpsDataSet.timeStamp
        } 
    json_data = json.dumps(obj).encode("utf-8")
    return json_data

# ブローカーに接続できたときの処理
def on_connect(client, userdata, flag, rc):
  print("Connected with result code " + str(rc))

# ブローカーが切断したときの処理
def on_disconnect(client, userdata, rc):
  if rc != 0:
     print("Unexpected disconnection.")

# publishが完了したときの処理
def on_publish(client, userdata, mid):
  print("publish: {0}".format(mid))


# test print
print("hello")
# 対象のフォルダから最新のCSVファイルを取得
latestCsvFile = getLatestCsvFile(path)
# 取得したCSVファイルの最新の緯度経度とタイムスタンプを取得
gpsDataSet = getLastestGpsData(latestCsvFile)
gpsDataSetJson = getGpsDataJson(gpsDataSet)
# mqtt各種設定
client = mqtt.Client()                 # クラスのインスタンス(実体)の作成
client.on_connect = on_connect         # 接続時のコールバック関数を登録
client.on_disconnect = on_disconnect   # 切断時のコールバックを登録
client.on_publish = on_publish         # メッセージ送信時のコールバック

client.connect(url, 1883, 60)  # 接続先は自分自身
# 通信処理スタート
client.loop_start()    # subはloop_forever()だが，pubはloop_start()で起動だけさせる
print("publish")
print(gpsDataSetJson)
client.publish("eltres",gpsDataSetJson) 

# 出力
print(gpsDataSet.latitude.degrees)
print(gpsDataSet.latitude.minutes)
print(gpsDataSet.latitude.seconds)
print(gpsDataSet.longitude.degrees)
print(gpsDataSet.longitude.minutes)
print(gpsDataSet.longitude.seconds)
print(gpsDataSet.timeStamp)




