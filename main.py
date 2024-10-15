from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from datetime import datetime
from typing import List

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# DB接続
def connect_db():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="Kameria503",
        host="localhost",
        port="5432"
    )

class Memo(BaseModel):
    year: int
    month: int
    day: int
    memo: List[str]  # memoは文字列の配列

# データを保存するAPI
@app.post("/dialy")
def save_memo(memo: Memo):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # 既存のレコードを削除
        cursor.execute(
            """
            DELETE FROM dialy WHERE year = %s AND month = %s AND day = %s
            """,
            (memo.year, memo.month, memo.day)
        )
        
        # 新しいレコードを挿入
        cursor.execute(
            """
            INSERT INTO dialy (year, month, day, memo, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (memo.year, memo.month, memo.day, memo.memo, datetime.now())
        )
        conn.commit()
        return {"message": "Memo saved successfully"}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        cursor.close()
        conn.close()


# メモを取得するAPI
@app.get("/getMemo")
def get_memo(year: int = Query(...), month: int = Query(...), day: int = Query(...)):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # データ取得クエリ
        cursor.execute(
            """
            SELECT memo FROM dialy
            WHERE year = %s AND month = %s AND day = %s
            """,
            (year, month, day)
        )
        result = cursor.fetchone()
        if result:
            return {"memo": result[0]}
        else:
            return {"memo": "No Nikki found"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cursor.close()
        conn.close()
