import boto3
import json
import os
import logging
from botocore.exceptions import BotoCoreError, ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

sqs = boto3.client(
    "sqs",
    endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
    region_name=os.getenv("AWS_DEFAULT_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
)

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
    region_name=os.getenv("AWS_DEFAULT_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
)

QUEUE_URL = os.getenv("SQS_ENROLLMENT_QUEUE_URL")
TABLE_NAME = os.getenv("DB_ENROLLMENTS_TABLE_NAME")

if not TABLE_NAME:
    logger.error("Environment variable DB_ENROLLMENTS_TABLE_NAME not defined!")
    raise ValueError("TABLE_NAME not configured")

table = dynamodb.Table(TABLE_NAME)

MAX_RETRIES = 3

def process_batch(messages):
    items = []
    message_entries = []

    for message in messages:
        try:
            body = json.loads(message["body"])
            item = {
                "id": body["id"],
                "name": body["name"],
                "cpf": body["cpf"],
                "age": body["age"],
                "status": body["status"],
                "age_group_id": body["age_group_id"]
            }

            if body["status"] in ["pending", "rejected"] and body.get("age_group_id"):
                item["status"] = "approved"

            items.append(item)
            message_entries.append({
                "Id": message["messageId"],
                "ReceiptHandle": message["receiptHandle"]
            })
        except KeyError as e:
            logger.error(f"Error in message fields {message.get('messageId', 'unknown')}: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON in message {message.get('messageId', 'unknown')}: {str(e)}")

    if not items:
        logger.warning("No valid items to process.")
        return False

    try:
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
        logger.info(f"{len(items)} enrollments processed successfully!")
    except (BotoCoreError, ClientError) as e:
        logger.error(f"Error inserting batch into DynamoDB: {str(e)}")
        raise

    if QUEUE_URL and message_entries:
        try:
            sqs.delete_message_batch(QueueUrl=QUEUE_URL, Entries=message_entries)
            logger.info(f"{len(message_entries)} messages deleted from SQS.")
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error deleting messages from SQS: {str(e)}")
            raise

    return True

def lambda_handler(event, context):
    logger.info(f"Receiving {len(event['Records'])} messages from SQS")

    retries = 0
    while retries < MAX_RETRIES:
        try:
            success = process_batch(event["Records"])
            if success:
                return {"statusCode": 200, "body": "Messages processed successfully!"}
            else:
                logger.warning("No valid messages processed, but no critical error.")
                return {"statusCode": 200, "body": "No valid messages processed."}
        except Exception as e:
            retries += 1
            logger.warning(f"Attempt {retries}/{MAX_RETRIES} failed: {str(e)}")
            if retries == MAX_RETRIES:
                logger.error("Failed to process messages after multiple attempts.")
                raise

    return {"statusCode": 500, "body": "Error processing messages."}