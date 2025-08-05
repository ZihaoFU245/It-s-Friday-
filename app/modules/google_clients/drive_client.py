from googleapiclient.discovery import build
from .google_base_client import GoogleBaseClient

class DriveClient(GoogleBaseClient):
    def __init__(self):
        scopes = ["https://www.googleapis.com/auth/drive"]
        super().__init__(scopes, service_name="Drive")
        self.service = build("drive", "v3", credentials=self.creds)

    def list_files(self, page_size: int = 10):
        resp = self.service.files().list(
            pageSize=page_size, fields="files(id, name)"
        ).execute()
        return resp.get("files", [])

    def get_file_metadata(self, file_id: str):
        return self.service.files().get(fileId=file_id).execute()
