import requests
import os


class CloudPrime:
    def __init__(self, api_key: str, base_url: str = "https://cloudprime.onrender.com/api"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-API-Key": api_key
        }

    def upload_file(self, file_path: str) -> dict:
        """
        Upload a file to cloudprime

        Args:
            file_path (str): Path to the file to upload

        Returns:
            dict: Response data with file URL and info
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        url = f"{self.base_url}/v1/upload-image/"

        with open(file_path, 'rb') as file:
            files = {'file': (os.path.basename(file_path), file)}
            response = requests.post(url, headers=self.headers, files=files)

        if response.status_code == 201:
            return response.json()
        else:
            response.raise_for_status()

    def get_upload_info(self) -> dict:
        """
        Get API usage information

        Returns:
            dict: API usage stats
        """
        url = f"{self.base_url}/api-keys/usage"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()