import os
import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.auth.transport.requests import Request
import time

class YouTubeChat:
    def __init__(self, db_manager, client_secrets_file, token_file, scopes, silent):
        self.client_secrets_file = client_secrets_file
        self.token_file = token_file
        self.scopes = scopes
        self.credentials = self.get_credentials()
        self.youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=self.credentials)
        self.silent = silent
        self.user_message_counts = {}

    def refresh_credentials_if_expired(self):
        if self.credentials.expired and self.credentials.refresh_token:
            print("Credentials Expired. Refreshing now...")
            try:
                self.credentials.refresh(Request())
                print("Credentials Refreshed.")
            except Exception as e:
                print("Error refreshing credentials: ", e)



    def get_credentials(self):
        credentials = None
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                credentials = pickle.load(token)
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, self.scopes)
                credentials = flow.run_local_server(port=0)
            with open(self.token_file, 'wb') as token:
                pickle.dump(credentials, token)
        return credentials

    def get_live_chat_id(self, video_id):
        request = self.youtube.videos().list(part="liveStreamingDetails", id=video_id)
        response = request.execute()

        if not response["items"]:
            print("No live stream found for the given video ID.")
            return None

        try:
            live_chat_id = response["items"][0]["liveStreamingDetails"]["activeLiveChatId"]
        except KeyError:
            print("The live stream is not active for the given video ID.")
            return None

        return live_chat_id

    def send_live_chat_message(self, live_chat_id, message):   
        if self.silent:
            print(f"Silent mode is on. Would have sent: {message}")
            return
        request = self.youtube.liveChatMessages().insert(
            part="snippet",
            body={
                "snippet": {
                    "liveChatId": live_chat_id,
                    "type": "textMessageEvent",
                    "textMessageDetails": {
                        "messageText": message
                    }
                }
            }
        )
        response = request.execute()

        return response