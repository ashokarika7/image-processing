from pydantic import BaseModel
from datetime import datetime

class ImageSchema(BaseModel):
    filename: str
    s3_key: str

class ImageUploadRequest(BaseModel):
    filename: str
    content_type: str

class ImageResponse(BaseModel):
    id: int
    filename: str
    s3_key: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True