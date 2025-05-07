from fastapi import FastAPI
from fastapi.responses import FileResponse
from router import message_router
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from database import create_pool, close_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_pool = None
    try: 
        db_pool = await create_pool()
        app.state.db_pool = db_pool
    except Exception as e:
        print(f"資料庫啟動失敗，請重新嘗試連線：{e}")
        app.state.db_pool = None
    yield
    if app.state.db_pool:
        await close_pool(app.state.db_pool)
        app.state.db_pool = None

app = FastAPI(lifespan=lifespan)
app.include_router(message_router.router)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get_message_board():
	    return FileResponse("./static/index.html", media_type="text/html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host= "0.0.0.0", port= 8000)