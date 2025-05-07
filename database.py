import asyncpg
from dotenv import load_dotenv
import os
from fastapi import Request

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_DATABASE = os.getenv("DB_DATABASE")

#格式: postgresql://user:password@host:port/database
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

async def create_pool():
    try:
        pool = await asyncpg.create_pool(dsn=DB_URL, min_size=2, max_size=10)
        print("資料庫連線池建立成功。")
        return pool
    except Exception as e:
        print(f"無法建立連線池：{e}")
        raise

async def close_pool(pool: asyncpg.Pool):
    if pool:
        await pool.close()
    

async def get_connection(request: Request):
    if not request.app.state.db_pool:
        print("找不到連線")
        raise
    pool: asyncpg.Pool = request.app.state.db_pool
    async with pool.acquire() as connection:
        yield connection

