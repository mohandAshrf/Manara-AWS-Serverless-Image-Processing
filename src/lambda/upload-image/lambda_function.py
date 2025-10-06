import json
import boto3
import time
import base64
from PIL import Image
import io
import uuid
from datetime import datetime

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

BUCKET = "mybucketmohand-ashrf"
TABLE = "metadata-images"  # DynamoDB table name

def lambda_handler(event, context):
    try:
        print(f"Event received: {json.dumps(event, default=str)}")
        
        # Get headers (case-insensitive)
        headers = event.get("headers", {}) or {}
        headers_lower = {k.lower(): v for k, v in headers.items()}
        
        # Get raw body
        raw_body = event.get("body")
        is_base64_encoded = event.get("isBase64Encoded", False)

        if not raw_body:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Empty file upload"})
            }

        # Handle different request formats
        file_content = None
        
        # Method 1: Check if Content-Type indicates JSON
        content_type_header = headers_lower.get("content-type", "")
        
        if content_type_header.startswith("application/json"):
            # Handle JSON payload with nested base64 body
            try:
                if is_base64_encoded:
                    raw_body = base64.b64decode(raw_body).decode('utf-8')
                
                parsed = json.loads(raw_body)
                if isinstance(parsed, dict) and "body" in parsed:
                    # Format: {"body": "base64-encoded-image"}
                    base64_data = parsed["body"]
                elif isinstance(parsed, dict) and "image" in parsed:
                    # Format: {"image": "base64-encoded-image", "filename": "..."}
                    base64_data = parsed["image"]
                else:
                    return {
                        "statusCode": 400,
                        "body": json.dumps({"error": "Invalid JSON structure. Expected 'body' or 'image' field"})
                    }
                
                file_content = base64.b64decode(base64_data)
                
            except json.JSONDecodeError as e:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": f"Invalid JSON: {str(e)}"})
                }
            except Exception as e:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": f"JSON processing error: {str(e)}"})
                }
        
        else:
            # Method 2: Direct base64 string in body (text/plain or other)
            try:
                if is_base64_encoded:
                    # API Gateway already decoded it, so raw_body should be the base64 string
                    file_content = base64.b64decode(raw_body)
                else:
                    # Raw body is the base64 string
                    file_content = base64.b64decode(raw_body)
                    
            except Exception as e:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": f"Invalid base64 encoding: {str(e)}"})
                }

        if not file_content:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No valid image data found"})
            }

        # Validate and extract metadata with Pillow
        try:
            image = Image.open(io.BytesIO(file_content))
            image_format = image.format  # e.g., "PNG", "JPEG"
            width, height = image.size
            
            # Additional image info
            mode = image.mode  # e.g., "RGB", "RGBA"
            has_transparency = mode in ("RGBA", "LA") or "transparency" in image.info
            
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Invalid image file: {str(e)}"})
            }

        # Extract filename and content type from headers
        filename = headers_lower.get("filename")
        header_content_type = headers_lower.get("content-type")
        
        # Generate filename if not provided
        if not filename:
            extension = image_format.lower() if image_format else "jpg"
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"upload-{timestamp}-{uuid.uuid4().hex[:8]}.{extension}"
        
        # Ensure filename has correct extension
        if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            extension = image_format.lower() if image_format else "jpg"
            filename = f"{filename}.{extension}"
        
        # Set content type based on image format
        format_to_mime = {
            "JPEG": "image/jpeg",
            "PNG": "image/png", 
            "GIF": "image/gif",
            "WEBP": "image/webp"
        }
        content_type = format_to_mime.get(image_format, "image/jpeg")
        
        # Override with header if provided
        if header_content_type and header_content_type.startswith("image/"):
            content_type = header_content_type

        # Upload to S3
        try:
            s3.put_object(
                Bucket=BUCKET,
                Key='uploaded/'+filename,
                Body=file_content,
                ContentType=content_type,
                ServerSideEncryption='AES256',
                Metadata={
                    'width': str(width),
                    'height': str(height),
                    'format': image_format or 'UNKNOWN',
                    'mode': mode,
                    'has_transparency': str(has_transparency)
                }
            )
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": f"S3 upload failed: {str(e)}"})
            }

        # Extract additional metadata
        file_size = len(file_content)  # in bytes
        timestamp = int(time.time())
        
        # Generate S3 URL
        s3_url = f"https://{BUCKET}.s3.amazonaws.com/{filename}"

        # Save metadata in DynamoDB
        try:
            table = dynamodb.Table(TABLE)
            table.put_item(
                Item={
                    "image-id": filename,   # <-- REQUIRED partition key
                    "bucket": BUCKET,
                    "s3_url": s3_url,
                    "content_type": content_type,
                    "image_format": image_format or "UNKNOWN",
                    "mode": mode,
                    "has_transparency": has_transparency,
                    "size_bytes": file_size,
                    "width": width,
                    "height": height,
                    "uploaded_at": timestamp,
                    "created_date": datetime.now().isoformat()
                }
            )

        except Exception as e:
            print(f"DynamoDB error (non-fatal): {str(e)}")
            # Continue execution - S3 upload was successful

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Image uploaded successfully with metadata",
                "filename": filename,
                "s3_url": s3_url,
                "bucket": BUCKET,
                "content_type": content_type,
                "image_format": image_format
            })
        }

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Upload failed: {str(e)}"})
        }
