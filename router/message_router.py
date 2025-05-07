from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException
from database import get_connection
from service.message_service import (
    upload_image_to_s3,
    save_message_to_db,
    get_all_messages,
)

router = APIRouter(prefix="/api", tags=["message"])


@router.post("/message")
async def post_message(
    text: str = Form(...), image: UploadFile = File(...), db=Depends(get_connection)
):
    try:
        image_url = await upload_image_to_s3(image)
        message_record = await save_message_to_db(text, image_url, db)
        return {"status": "ok", "data": message_record}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"發生未預期錯誤，留言失敗：{e}")
        raise HTTPException(status_code=500, detail="發生未預期錯誤，留言失敗")


@router.get("/messages")
async def get_messages(db=Depends(get_connection)):
    try:
        messages_records = await get_all_messages(db)
        return {"status": "ok", "data": messages_records}
    except Exception as e:
        print(f"發生未預期錯誤，無法取得留言: {e}")
        raise HTTPException(status_code=500, detail="發生未預期錯誤，無法取得留言")
