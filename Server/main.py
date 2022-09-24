from fastapi import FastAPI
from pydantic import BaseModel  # リクエストbodyを定義するために必要
from typing import List  # ネストされたBodyを定義するために必要
from typing import Union,Set

app = FastAPI()

class TudeValue(BaseModel):
  degrees: str
  minutes: str
  seconds: str

# リクエストbodyを定義
class GpsDataSet(BaseModel):
  latitude: Union[TudeValue, None] = None
  longitude: Union[TudeValue, None] = None
#  timeStamp: str

class Hello(BaseModel):
  hello: str

# シンプルなJSON Bodyの受け取り
@app.post("/")
# 上で定義したUserモデルのリクエストbodyをuserで受け取る
# user = {"user_id": 1, "name": "太郎"}
def create_user(item: TudeValue):
  print(item.degrees)
  # レスポンスbody
  return "hello"
