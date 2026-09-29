
import boto3
import json
import os
import logging
from urllib.parse import unquote_plus
from dotenv import load_dotenv

from services.s3 import download_image
from model_handler.image_model_handler import ImageModelHandler
from database.db import SessionLocal

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

QUEUE_URL = os.getenv("QUEUE_URL")
REGION = os.getenv("AWS_DEFAULT_REGION")

sqs_client = boto3.client("sqs", region_name=REGION)


def delete_message(receipt_handle):
    sqs_client.delete_message(
        QueueUrl=QUEUE_URL,
        ReceiptHandle=receipt_handle
    )



def process_message(message):
    message_id = message.get("MessageId")

    # Validate the message body
    try:
        body = json.loads(message["Body"])
        logger.info(
            "Number of S3 records: %d",
            len(body.get("Records", []))
        )
    except (json.JSONDecodeError, TypeError, KeyError):
        logger.exception(
            "Invalid JSON or missing body. Message ID: %s",
            message_id
        )
        return False

    if not isinstance(body, dict):
        logger.error(
            "Unexpected message format. Message ID: %s",
            message_id
        )
        return False

    # Validate S3 event structure
    if "Records" not in body:
        logger.warning(
            "Ignoring non-S3 event. Message ID: %s",
            message_id
        )
        return True

    if not isinstance(body["Records"], list) or not body["Records"]:
        logger.error(
            "Invalid S3 Records. Message ID: %s",
            message_id
        )
        return False

    try:
        record = body["Records"][0]
        bucket_name = record["s3"]["bucket"]["name"]
        object_key = unquote_plus(
            record["s3"]["object"]["key"]
        )
    except (KeyError, TypeError, IndexError):
        logger.exception(
            "Invalid S3 event structure. Message ID: %s",
            message_id
        )
        return False

    db = SessionLocal()

    try:
        with db.begin():
            existing_image = (
                ImageModelHandler.get_image_by_s3_key(
                    db, object_key
                )
            )

            if not existing_image:
                raise ValueError(
                    f"Image not found: {object_key}"
                )

            if existing_image.status == "completed":
                logger.info(
                    "Image already completed: %s",
                    existing_image.id
                )
            else:
                image = ImageModelHandler.claim_image(
                    db, object_key
                )

                if not image:
                    image = ImageModelHandler.reclaim_stuck_image(
                        db, object_key
                    )

                if not image:
                    logger.info(
                        "Image already being processed: %s",
                        object_key
                    )
                    return False

                token = image.processing_token

                logger.info("Claimed image: %s", image.id)

                file_path = download_image(
                    bucket_name, object_key
                )

                logger.info(
                    "Image downloaded: %s",
                    image.id
                )

                completed = ImageModelHandler.complete_image(
                    db=db,
                    image_id=image.id,
                    token=token
                )

                if not completed:
                    raise RuntimeError(
                        "Failed to mark image as completed"
                    )

                logger.info(
                    "Image completed: %s",
                    image.id
                )

        return True

    finally:
        db.close()

def process_batch():
    response = sqs_client.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=5,
        WaitTimeSeconds=20
    )

    messages = response.get("Messages", [])

    if not messages:
        logger.info("No messages available")
        return

    logger.info("Received %d messages", len(messages))

    for message in messages:
        try:
            success = process_message(message)

            if success:
                delete_message(message["ReceiptHandle"])
                logger.info(
                    "Deleted SQS message: %s",
                    message["MessageId"]
                )
            else:
                logger.info(
                    "Message left for retry: %s",
                    message["MessageId"]
                )

        except Exception:
            logger.exception(
                "Processing failed for message: %s",
                message.get("MessageId")
            )


if __name__ == "__main__":
    while True:
        try:
            process_batch()
        except Exception:
            logger.exception("Batch polling failed")