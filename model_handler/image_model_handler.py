from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.image import Image
from sqlalchemy import update
from uuid import uuid4

class ImageModelHandler:

    @staticmethod
    def create_image(db: Session, filename: str, s3_key: str):
        image = Image(
            filename=filename,
            s3_key=s3_key,
            status="pending",
            created_at=datetime.utcnow()
        )

        db.add(image)
        db.commit()
        db.refresh(image)
        return image

    @staticmethod
    def claim_image(db, s3_key: str):
        token= str(uuid4())

        stmt = (
            update(Image)
            .where(
                Image.s3_key == s3_key,
                Image.status == "pending"
            )
            .values(status="processing",
                    processing_started_at=datetime.utcnow(),
                    processing_token=token
                    )
            .returning(Image)
        )

        result = db.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    def complete_image(db, image_id: int, token: str):
        stmt = (
            update(Image)
            .where(
                Image.id == image_id,
                Image.status == "processing",
                Image.processing_token == token
            )
            .values(
                status="completed",
                processed_at=datetime.utcnow(),
                processing_started_at=None,
                processing_token=None
            )
        )

        result = db.execute(stmt)

        return result.rowcount > 0

    @staticmethod
    def get_image_by_s3_key(db, s3_key: str):
        return (
            db.query(Image)
            .filter(Image.s3_key == s3_key)
            .first()
        )

    @staticmethod
    def reclaim_stuck_image(db, s3_key: str):
        cutoff_time = datetime.utcnow() - timedelta(minutes=10)
        token = str(uuid4())

        stmt = (
            update(Image)
            .where(
                Image.s3_key == s3_key,
                Image.status == "processing",
                Image.processing_started_at < cutoff_time
            )
            .values(
                processing_started_at=datetime.utcnow(),
                processing_token=token
            )
            .returning(Image)
        )

        result = db.execute(stmt)
        return result.scalar_one_or_none()