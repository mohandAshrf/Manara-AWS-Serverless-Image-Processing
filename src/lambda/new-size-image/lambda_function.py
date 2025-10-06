import boto3
import os
import io
import base64
from PIL import Image

s3 = boto3.client("s3")
RESIZE_SIZE = int(os.environ.get("RESIZE_SIZE", "512"))

def lambda_handler(event, context):
    try:
        
        if "bucket" in event and "filename" in event:
            bucket = event["bucket"]
            key = event["filename"]
            
        elif "detail" in event and "bucket" in event["detail"]:
            bucket = event["detail"]["bucket"]["name"]
            key = event["detail"]["object"]["key"]

        else:
            raise ValueError("Invalid event format")

        tmp_path = f"/tmp/{os.path.basename(key)}"
        s3.download_file(bucket, key, tmp_path)

        with Image.open(tmp_path) as img:
            img = img.convert("RGB")
            img = img.resize((RESIZE_SIZE, RESIZE_SIZE), Image.LANCZOS)
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=90)
            buffer.seek(0)

        img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return {
             "bucket": bucket,
            "filename": key,
            "resized_image": img_b64
        }

    except Exception as e:
        print(f"Error in Lambda: {str(e)}")
        raise
