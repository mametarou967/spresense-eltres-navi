# target path
path = "c:/XXX"
url = "http://YYY:ZZZ/"


#import
import os
import csv
import urllib.request
import json

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

def postGpsData(gpsDataSet):
    method = "POST"
    headers = {"Content-Type" : "application/json"}
    # PythonオブジェクトをJSONに変換する
    print(type(gpsDataSet.latitude.minutes))
    obj = {
        "degrees" : gpsDataSet.latitude.degrees,
        "minutes" : gpsDataSet.latitude.minutes,
        "seconds" : gpsDataSet.latitude.seconds
        #"hello" : "hello"
        #"latitude" : {
        #    "degrees" : gpsDataSet.latitude.degrees,
        #    "minuts" : gpsDataSet.latitude.minutes,
        #    "seconds" : gpsDataSet.latitude.seconds
        #},
        #"longitude" : {
        #    "degrees" : gpsDataSet.longitude.degrees,
        #    "minuts" : gpsDataSet.longitude.minutes,
        #    "seconds" : gpsDataSet.longitude.seconds
        #},
        # "timeStamp" : gpsDataSet.timeStamp
        } 
    json_data = json.dumps(obj).encode("utf-8")
    request = urllib.request.Request(url, data=json_data, method=method, headers=headers)
    with urllib.request.urlopen(request) as response:
        response_body = response.read().decode("utf-8")

# test print
print("hello")
# 対象のフォルダから最新のCSVファイルを取得
latestCsvFile = getLatestCsvFile(path)
# 取得したCSVファイルの最新の緯度経度とタイムスタンプを取得
gpsDataSet = getLastestGpsData(latestCsvFile)
# 出力
print(gpsDataSet.latitude.degrees)
print(gpsDataSet.latitude.minutes)
print(gpsDataSet.latitude.seconds)
print(gpsDataSet.longitude.degrees)
print(gpsDataSet.longitude.minutes)
print(gpsDataSet.longitude.seconds)
print(gpsDataSet.timeStamp)

postGpsData(gpsDataSet)



