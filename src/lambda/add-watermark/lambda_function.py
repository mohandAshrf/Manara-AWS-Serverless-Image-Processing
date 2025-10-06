import os
import io
import base64
from PIL import Image, ImageDraw, ImageFont
import boto3 

WATERMARK_TEXT = os.environ.get("WATERMARK_TEXT", "mohand 😎")
s3 = boto3.client("s3")

def lambda_handler(event, context):
    try:
        if "resized_image" not in event:
            raise ValueError("Missing resized_image in event")

        img_bytes = base64.b64decode(event["resized_image"])
        buffer = io.BytesIO(img_bytes)

        with Image.open(buffer) as img:
            img = img.convert("RGB")
            draw = ImageDraw.Draw(img)

            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
            except:
                font = ImageFont.load_default()

            text = WATERMARK_TEXT
            width, height = img.size

            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            for y in range(0, height, text_height * 4):
                for x in range(0, width, text_width * 4):
                    draw.text((x, y), text, font=font, fill=(255, 255, 255, 50))

            out_buffer = io.BytesIO()
            img.save(out_buffer, format="JPEG", quality=90)
            out_buffer.seek(0)

  
            filename = os.path.basename(event['filename'])


            final_key = f"FINAL-IMAGES/{filename}"
            s3.put_object(
                Bucket=event["bucket"],
                Key=final_key,
                Body=out_buffer.getvalue(),
                ContentType="image/jpeg"
            )
    
        return {
            "bucket": event["bucket"],
            "key": final_key
        }

    

    except Exception as e:
        raise
