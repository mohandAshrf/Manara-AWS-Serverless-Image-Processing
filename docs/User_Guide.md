# How to Use - Serverless Image Processing System

## Table of Contents
1. [Getting Started](#getting-started)
2. [API Authentication](#api-authentication)
3. [Uploading Images](#uploading-images)
4. [Retrieving Image Metadata](#retrieving-image-metadata)
5. [Downloading Processed Images](#downloading-processed-images)
6. [Using Different Tools](#using-different-tools)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Getting Started

### Prerequisites
- Valid API key (time-limited for security)
- HTTP client (curl, Postman, or programming language)
- Images to upload (PNG, JPG, JPEG formats supported)

### Base URL
```
https://4qynjac488.execute-api.us-east-1.amazonaws.com/dev
```

### Rate Limits
- **Requests per second:** 10,000
- **Burst capacity:** 5,000 requests
- **API key expiration:** Time-limited (contact admin for renewal)

---

## API Authentication

All API requests require an API key in the request header.

### Adding API Key to Requests

**Header Format:**
```
x-api-key: YOUR_API_KEY_HERE
```

**Example:**
```bash
curl -H "x-api-key: abcd1234efgh5678ijkl9012mnop3456"
```
**api-key** IC1iQO3s8M9ikBjSRXuQ1PoDA7hGe5q3Hnr9lrha is temporary 

### Getting Your API Key
1. Contact the system administrator
2. API keys are time-limited for security
3. Request renewal before expiration

⚠️ **Security Warning:** Never commit API keys to version control or share publicly!

---

## Uploading Images

### Endpoint
```
POST /upload
```

### Supported Formats
- PNG (.png)
- JPEG (.jpg, .jpeg)
- Maximum file size: 10 MB (recommended)

### Using curl

```bash
!base64 -w 0 replace-with-file-path > encoded.txt
!echo "{\"body\":\"$(cat encoded.txt)\"}" > payload.json

!curl -X POST "https://4qynjac488.execute-api.us-east-1.amazonaws.com/dev/upload" \
  -H "Content-Type: application/json" \
  -H "x-api-key: replace-with-api-key" \
  --data-binary "@payload.json"

```

### Using PowerShell

```powershell
$url = "https://4qynjac488.execute-api.us-east-1.amazonaws.com/dev/upload"
$apiKey = "replace-with-api-key"

$headers = @{
    "Content-Type" = "application/json"
    "x-api-key" = $apiKey
}

$imagePath = "replace-with-file-path"

if (-Not (Test-Path $imagePath)) {
    Write-Host "File not found: $imagePath"
    return
}

$imageBytes = [System.IO.File]::ReadAllBytes($imagePath)
$encoded = [Convert]::ToBase64String($imageBytes)

$payload = @{
    body = $encoded
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $payload

Write-Host "Status Code: $($response.StatusCode)"
Write-Host "Response: $($response | ConvertTo-Json -Depth 10)"
```


### Using Python

```python
import requests

url = "https://4qynjac488.execute-api.us-east-1.amazonaws.com/dev/upload"
headers = {
    "Content-Type": "image/png",
    "filename": "mohnd.png",
    "x-api-key": "replace-with-api-key"
}

with open("replace-with-file-path", "rb") as f:
    response = requests.post(url, headers=headers, data=f)

print("Status Code:", response.status_code)
print("Response:", response.text)

```

### Response Format

**Success (200 OK):**
```json
{
    "statusCode": 200,
    "body": {
        "message": "Image uploaded successfully with metadata",
        "filename": "upload-20251006_162041-edbe0d33.png",
        "s3_url": "https://mybucketmohand-ashrf.s3.amazonaws.com/upload-20251006_162041-edbe0d33.png",
        "bucket": "mybucketmohand-ashrf",
        "content_type": "image/png",
        "image_format": "PNG"
    }
}
```


## Retrieving Image Metadata

### Endpoint
```
GET /get-image-metadata/{file-name}
```

### Using curl

```bash
curl -X GET "https://4qynjac488.execute-api.us-east-1.amazonaws.com/dev/get-image-metadata/replace-with-file-name" \
  -H "x-api-key: replace-with-api-key"

```
### power shell 

```bash
$response = curl -Method GET `
  -Uri "https://4qynjac488.execute-api.us-east-1.amazonaws.com/dev/get-image-metadata/replace-with-file-name" `
  -Headers @{
    "x-api-key" = "replace-with-api-key"
  }
  $response.Content | ConvertFrom-Json | Format-List
```

### Using Python

```python
import requests

# Replace with your API endpoint and file name
image_id = "replace-with-file-name"  # Use snake_case for file name
base_url = "https://4qynjac488.execute-api.us-east-1.amazonaws.com/dev"
url = f"{base_url}/get-image-metadata/{image_id}"

headers = {
    "x-api-key": "replace-with-api-key"
}

response = requests.get(url, headers=headers)

print("Status Code:", response.status_code)
print("Response:", response.json())

```

### Response Format

**Success (200 OK):**
```json
Status Code: 200
Response:
{
    "statusCode": 200,
    "headers": {
        "Content-Type": "application/json"
    },
    "body": {
        "image_id": "upload_20251001_203145_5badb1ab.png",
        "bucket": "mybucketmohand-ashrf",
        "s3_key": "uploaded/upload_20251001_203145_5badb1ab.png",
        "size": 59279,
        "content_type": "image/png",
        "last_modified": "2025-10-01T20:31:52+00:00",
        "has_transparency": true,
        "mode": "RGBA",
        "width": 889,
        "height": 859,
        "created_date": "2025-10-01T20:31:45.373549",
        "uploaded_at": 1759350705,
        "size_bytes": 1224511,
        "image_format": "PNG",
        "download_url": "https://mybucketmohand-ashrf.s3.amazonaws.com/uploaded/upload_20251001_203145_5badb1ab.png?AWSAccessKeyId=ASIAR..."
    }
}

```


---

## Downloading Processed Images

### Endpoint
```
GET /get-processed-image/{file-name}
```

### Using curl

```bash
# Download to file
  curl -X GET "https://4qynjac488.execute-api.us-east-1.amazonaws.com/dev/get-processed-image/replace-with-file-name " \
  -H "x-api-key: replace-with-api-key"

```
### power shell 

```bash
$response = curl -Method GET `
  -Uri "https://4qynjac488.execute-api.us-east-1.amazonaws.com/dev/get-processed-image/replace-with-file-name" `
  -Headers @{
    "x-api-key" = "replace-with-api-key"
  }
  $response.Content | ConvertFrom-Json | Format-List
```
### Using Python

```python
import requests

# Replace with your API endpoint and file name
file_name = "replace-with-file-path"
url = f"https://4qynjac488.execute-api.us-east-1.amazonaws.com/dev/get-procesed-image/{file_name}"

headers = {
    "x-api-key": "replace-with-api-key"
}

response = requests.get(url, headers=headers)

print("Status Code:", response.status_code)
print("Response:", response.json())

```

### Response Format
```json
Status Code: 200
Response:
{
    "statusCode": 200,
    "headers": {
        "Content-Type": "application/json"
    },
    "body": {
        "image_id": "upload_20251001_203145_5badb1ab.png",
        "bucket": "mybucketmohand-ashrf",
        "s3_key": "FINAL-IMAGES/upload_20251001_203145_5badb1ab.png",
        "size": 59279,
        "content_type": "image/png",
        "last_modified": "2025-10-01T20:31:52+00:00",
        "has_transparency": true,
        "mode": "RGBA",
        "width": 889,
        "height": 859,
        "created_date": "2025-10-01T20:31:45.373549",
        "uploaded_at": 1759350705,
        "size_bytes": 1224511,
        "image_format": "PNG",
        "download_url": "https://mybucketmohand-ashrf.s3.amazonaws.com/FINAL-IMAGES/upload_20251001_203145_5badb1ab.png?AWSAccessKeyId=ASIAR..."
    }
}

```

---

## Using Different Tools

### 1. Using Postman

#### Setup Collection
1. Create new collection: "Serverless Image Processing"
2. Add environment variable:
   - Key: `api_key`
   - Value: `YOUR_API_KEY`
   - Key: `base_url`
   - Value: `https://4qynjac488.execute-api.us-east-1.amazonaws.com/dev`

#### Upload Image Request
- **Method:** POST
- **URL:** `{{base_url}}/upload`
- **Headers:**
  - `x-api-key`: `{{api_key}}`
  - `Content-Type`: `image/png`
- **Body:** Binary → Select file

#### Get Metadata Request
- **Method:** GET
- **URL:** `{{base_url}}/get-image-metadata/replace-with-file-name`
- **Headers:**
  - `x-api-key`: `{{api_key}}`

#### Get Processed Image Request
- **Method:** GET
- **URL:** `{{base_url}}/get-processed-image/replace-with-file-name`
- **Headers:**
  - `x-api-key`: `{{api_key}}`

---

## Troubleshooting

### Common Issues

#### 1. "Forbidden" or 401 Error
**Problem:** Invalid or expired API key

**Solution:**
- Verify your API key is correct
- Check if API key has expired
- Request new API key from administrator


#### 2. "Invalid Image Format" Error
**Problem:** Unsupported file format

**Solution:**
- Ensure image is PNG or JPEG format
- Check Content-Type header matches file type
- Verify file is not corrupted

```bash
# Check file type
file your-image.png

# Should output: PNG image data, 889 x 859, 8-bit/color RGBA
```


#### 4. Rate Limit Exceeded
**Problem:** Too many requests in short time limit is 100 per second

**Solution:**
- Implement exponential backoff
- Add delays between requests
- Check burst limit

#### 5. Large File Upload Issues
**Problem:** File too large or timeout

**Solution:**
- Compress images before upload
- Use smaller file sizes (recommended < 5 MB)
- Increase timeout settings

---
