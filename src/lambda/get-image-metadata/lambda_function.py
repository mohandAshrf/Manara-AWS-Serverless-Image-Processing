import boto3
import json
import os
from urllib.parse import urlparse
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

TABLE_NAME = os.environ.get("TABLE_NAME", "metadata-images")
BUCKET = os.environ.get("BUCKET", "mybucketmohand-ashrf")


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
        image_id = event["pathParameters"]["file-name"]

        # 1. Get object record from DynamoDB
        table = dynamodb.Table(TABLE_NAME)
        db_response = table.get_item(Key={"image-id": image_id})

        if "Item" not in db_response:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": f"Image {image_id} not found"})
            }

        item = db_response["Item"]

        # Extract key from s3_url
        s3_url = item.get("s3_url")
        if not s3_url:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "s3_url missing from DynamoDB item"})
            }

        if s3_url.startswith("s3://"):
            s3_key = s3_url.replace(f"s3://{BUCKET}/", "")
        elif s3_url.startswith("http"):
            parsed = urlparse(s3_url)
            s3_key = parsed.path.lstrip("/")
        else:
            s3_key = s3_url
            
        print(s3_key)
        
        s3_key='uploaded/'+s3_key
        # 2. Get metadata from S3
        s3_response = s3.head_object(Bucket=BUCKET, Key=s3_key)

        metadata = {
            "image-id": image_id,
            "bucket": BUCKET,
            "s3_key": s3_key,
            "size": s3_response["ContentLength"],
            "content_type": s3_response["ContentType"],
            "last_modified": s3_response["LastModified"].isoformat()
        }

        # Merge DynamoDB metadata
        metadata.update({k: v for k, v in item.items() if k not in ["image-id", "s3_url"]})

        # 3. Generate pre-signed download URL (valid 1h)
        presigned_url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": s3_key},
            ExpiresIn=3600
        )
        metadata["download_url"] = presigned_url

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(metadata, cls=DecimalEncoder)
        }

