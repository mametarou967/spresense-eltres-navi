from fastapi import FastAPI
from pydantic import BaseModel  # リクエストbodyを定義するために必要
from typing import List  # ネストされたBodyを定義するために必要
from typing import Union,Set

app = FastAPI()

# リクエストbodyを定義
class GpsDataSet(BaseModel):
  latDegrees: str
  latMinutes: str
  latSeconds: str
  longDegrees: str
  longMinutes: str
  longSeconds: str

# シンプルなJSON Bodyの受け取り
@app.post("/")
# 上で定義したUserモデルのリクエストbodyをuserで受け取る
# user = {"user_id": 1, "name": "太郎"}
def create_user(item: GpsDataSet):
  print(item.latDegrees)
  return "hello"
