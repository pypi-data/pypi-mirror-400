import requests
import os

class FileServerClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.login(username, password)

    def login(self, username, password):
        """Authenticates and stores the JWT token."""
        url = f"{self.base_url}/api/token"
        data = {
            "username": username,
            "password": password
        }
        response = self.session.post(url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data["access_token"]
            # Add token to all future requests
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
        else:
            raise Exception(f"Login failed: {response.text}")

    def list_files(self, path=""):
        """Lists files in a specific directory (relative to your root)."""
        url = f"{self.base_url}/api/files/{path}"
        response = self.session.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            # Depending on use case, might want to raise exception or return empty list
            # For client library, raising exception on error is often better, or returning None
            # Sticking to valid JSON return or raising for now.
            response.raise_for_status()
            return []

    def upload_file(self, local_path, remote_path=""):
        """Uploads a local file to the server."""
        url = f"{self.base_url}/api/upload/"
        if remote_path:
             url += f"?path={remote_path}"
             
        file_name = os.path.basename(local_path)
        with open(local_path, "rb") as f:
            files = {"files": (file_name, f)}
            response = self.session.post(url, files=files)
            
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def download_file(self, remote_path, local_path):
        """Downloads a file from the server."""
        url = f"{self.base_url}/api/files/{remote_path}"
        
        # Use stream=True for large files
        with self.session.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
