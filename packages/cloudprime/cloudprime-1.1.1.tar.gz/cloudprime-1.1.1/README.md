# CloudPrime Documentation

The **CloudPrime** enables users to securely upload and retrieve files of any type with ease. To use this API, you need to register on the CloudPrime platform and obtain an API key. This API is designed for seamless integration into your applications, ensuring reliable and efficient file management.

## Features
- **Universal File Support**: Upload images (JPG, PNG, GIF, BMP, WEBP, SVG, TIFF), videos (MP4, AVI, MOV, MKV, WMV), documents (PDF, DOC, DOCX, PPT, PPTX, TXT), spreadsheets (CSV, XLS, XLSX), and any other file type.
- **Secure File Uploads**: Upload your files securely using API key authentication.
- **Simple Integration**: Integrate the API into your Python application effortlessly.
- **File Retrieval**: Retrieve uploaded files quickly and reliably.
- **API Usage Tracking**: Monitor your API usage, limits, and statistics.

## Getting Started

### Step 1: Register and Obtain an API Key
1. Visit the [CloudPrime Platform](https://cloudprime.netlify.app) to create an account.
2. After registering, log in to your account and navigate to the **Dashboard**.
3. Go to the **API Keys** section and generate your unique API key.
4. This API key will be used to authenticate all your API requests.

### Step 2: Access the Documentation
For detailed information on API endpoints and usage, refer to the [CloudPrime Documentation](https://cloudprime.netlify.app/documentation/).

## Installation
To use the CloudPrime in your Python application, install the required package:

```bash
pip install cloudprime
```

## Usage Example
## Basic File Upload
Here is a simple example demonstrating how to upload any type of file using the CloudPrime:

```python
from cloudprime import CloudPrime

# Replace with your actual API key from CloudPrime dashboard
API_KEY = "your_actual_api_key_here"

# Initialize the CloudPrime client
client = CloudPrime(API_KEY)

# Get API usage statistics
print("Getting API usage stats...")
stats = client.get_upload_info()
print(f"Stats: {stats}")

# Upload any type of file (image, video, document, etc.)
file_to_upload = "path/to/your/file.pdf"  # Can be PDF, DOC, PNG, MP4, CSV, etc.

try:
    print(f"\nUploading file: {file_to_upload}")
    result = client.upload_file(file_to_upload)
    
    print("Upload successful!")
    print(f"File URL: {result['data']['publicUrl']}")
    print(f"File ID: {result['data']['id']}")
    print(f"File Size: {result['data']['fileSize']}")
    
except FileNotFoundError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Upload failed: {e}")
```

## Example Response
## API Usage Statistics Response:

```python
{
    "success": True,
    "data": {
        "keyName": "Production Key",
        "isActive": True,
        "lastUsed": "2026-01-05T15:29:07.817Z",
        "usageCount": 6,
        "totalUploads": 3,
        "uploadsThisMonth": 6,
        "uploadLimit": "50",
        "usagePercentage": 12,
        "createdAt": "2026-01-05T12:24:10.432Z",
        "expiresAt": "2027-01-05T12:24:10.432Z"
    }
}
```

## File Upload Success Response:

```python
{
    "success": True,
    "data": {
        "id": "695bd8c4f91c7ee047d11bf8",
        "publicUrl": "https://imageserve.pythonanywhere.com/media/uploads/your_uploaded_image.pdf",
        "fileSize": "2.15 MB",
        "fileName": "document.pdf",
        "fileType": "application/pdf",
        "uploadedAt": "2026-01-05T15:30:45.123Z"
    }
}
```

## Example Output in Terminal:

```text
Getting API usage stats...
Stats: {'success': True, 'data': {'keyName': 'Production Key', 'isActive': True, 'lastUsed': '2026-01-05T15:29:07.817Z', 'usageCount': 6, 'totalUploads': 3, 'uploadsThisMonth': 6, 'uploadLimit': '50', 'usagePercentage': 12, 'createdAt': '2026-01-05T12:24:10.432Z', 'expiresAt': '2027-01-05T12:24:10.432Z'}}

Uploading file: document.pdf
Upload successful!
File URL: https://imageserve.pythonanywhere.com/media/uploads/your_uploaded_image.pdf
File ID: 695bd8c4f91c7ee047d11bf8
File Size: 2.15 MB
```

## Supported File Types

- **Images:** .jpg, .jpeg, .png, .gif, .bmp, .webp, .svg, .tiff, .ico
- **Videos:** .mp4, .avi, .mov, .mkv, .wmv, .flv, .webm
- **Documents:** .pdf, .doc, .docx, .ppt, .pptx, .txt, .rtf
- **Spreadsheets:** .csv, .xls, .xlsx, .ods
- **Archives:** .zip, .rar, .7z, .tar.gz
- **Code Files:** .py, .js, .html, .css, .json, .xml
- **Audio:** .mp3, .wav, .ogg, .m4a
- **And many more...**

## Key Points
- Always keep your API key confidential and never expose it in client-side code.
- Ensure your API key is included in the header (X-API-Key) of every request for authentication.
- The API supports files up to your plan's limit (check your dashboard for details).
- All uploaded files are securely stored and accessible via unique URLs.
- Follow the official [documentation](https://cloudprime.netlify.app/documentation/) for detailed endpoint specifications and advanced features.

## Support
If you encounter any issues or have questions:

- Visit our [Documentation](https://cloudprime.netlify.app/documentation/)
- Check our [Dashboard](https://cloudprime.netlify.app/dashboard/) for API usage

## License
This package is licensed under the MIT License.

Thank you for choosing CloudPrime for your file management needs!

