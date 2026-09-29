from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from models.image import Image
from routes.images_schema import ImageSchema,ImageResponse, ImageUploadRequest
from services.s3 import generate_presigned_upload_url
from uuid import uuid4
from model_handler.image_model_handler import ImageModelHandler

router = APIRouter()

@router.post("/image/upload-url")
def create_upload_url(
    request: ImageUploadRequest,
    db: Session = Depends(get_db)
):
    try:
        file_extension = request.filename.split(".")[-1]
        object_key = f"images/{uuid4()}.{file_extension}"

        image = ImageModelHandler.create_image(
            db=db,
            filename=request.filename,
            s3_key=object_key
        )

        upload_url = generate_presigned_upload_url(
            object_key=object_key,
            content_type=request.content_type
        )

        return {
            "upload_url": upload_url,
            "object_key": object_key,
            "image_id": image.id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create upload URL: {str(e)}"
        )