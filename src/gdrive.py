import io
import shutil
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive"]


class GDriveCredential:
    def __init__(self, scopes=SCOPES):
        self.scopes = scopes
        self.credentials = self.create_credentials()

    def create_credentials(self):
        credentials = None

        if Path("token.json").exists():
            credentials = self._parse_credentials()

        if not credentials or not credentials.valid:
            if (
                credentials
                and credentials.expired
                and credentials.refresh_token
            ):
                self._refresh_credentials(credentials)
            else:
                credentials = self._create_new_credentials()

            self._save_credentials(credentials, "token.json")

        return credentials

    def _parse_credentials(self, filename="token.json"):
        return Credentials.from_authorized_user_file(filename, self.scopes)

    def _refresh_credentials(self, credentials):
        credentials.refresh(Request())
        return credentials

    def _create_new_credentials(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", self.scopes
        )
        return flow.run_local_server(port=0)

    def _save_credentials(self, credentials, filename: str):
        with open(filename, "w") as token:
            token.write(credentials.to_json())


class GDriveDownloader:
    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        self.service = self.get_service()

    def get_service(self):
        return build("drive", "v3", credentials=self.credentials)

    def download(self, file_id, download_path, file_name):
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
            fh.seek(0)
            with open(Path(download_path, file_name), "wb") as f:
                shutil.copyfileobj(fh, f)
