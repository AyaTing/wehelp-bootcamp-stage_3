from dotenv import load_dotenv
import os
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException
from datetime import datetime
import mimetypes

load_dotenv()


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")
CLOUDFRONT_DOMAIN = os.getenv("CLOUDFRONT_DOMAIN")

if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)
else:
    s3_client = boto3.client(
        "s3",
        region_name=AWS_REGION,
    )

async def upload_image_to_s3(image: UploadFile):
    if not image.content_type:
        raise HTTPException(status_code=400, detail="檔案類型錯誤")
    filename_prefix = datetime.now().strftime("%Y%m%d%H%M%S%f")
    _ , ext_from_filename = os.path.splitext(image.filename)
    if ext_from_filename:
        ext = ext_from_filename
    else:
        ext = mimetypes.guess_extension(image.content_type, strict=False)
    if not ext:
        ext = ".jpg"
    s3_object_name = f"images/{filename_prefix}{ext}"
    try:
        s3_client.upload_fileobj(
            image.file,
            S3_BUCKET_NAME,
            s3_object_name,
            ExtraArgs={"ContentType": image.content_type},
        )
        image_url = f"https://{CLOUDFRONT_DOMAIN}/{s3_object_name}"
        return image_url
    except ClientError as err:
        print(f"S3返回錯誤回應：{err}")
        raise HTTPException(status_code=500, detail="S3返回錯誤回應，檔案上傳失敗")
    except Exception as e:
        print(f"發生未預期錯誤：{e}")
        raise HTTPException(status_code=500, detail="發生未預期錯誤，檔案上傳失敗")


async def save_message_to_db(text: str, image_url: str, db):
    try:
        insert_query = "INSERT INTO messages (text, image_url) VALUES ($1, $2) RETURNING text, image_url"
        message_record = await db.fetchrow(insert_query, text, image_url)
        return {
            "text": message_record["text"],
            "imageUrl": message_record["image_url"],
        }
    except Exception as e:
        print(f"資料庫寫入失敗: {e}")
        raise HTTPException(status_code=500, detail="資料庫寫入失敗")


async def get_all_messages(db):
    try:
        select_query = 'SELECT text, image_url AS "imageUrl" FROM messages ORDER BY created_at DESC'
        messages_records = await db.fetch(select_query)
        return [dict(record) for record in messages_records]
    except Exception as e:
        print(f"資料庫讀取失敗: {e}")
        raise HTTPException(status_code=500, detail="資料庫讀取失敗")
