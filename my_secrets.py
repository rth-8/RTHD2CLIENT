from dotenv import load_dotenv
import os

class MySecrets:
    def __init__(self) -> None:
        load_dotenv()
        self.client_id = os.getenv("CLIENT_ID")
        # print(f"MyOAuth: CLIENT_ID = {self.client_id}")
        self.client_secret = os.getenv("CLIENT_SECRET")
        # print(f"MyOAuth: CLIENT_SECRET = {self.client_secret}")
        self.api_key = os.getenv("API_KEY")
        # print(f"MyOAuth: CLIENT_ID = {self.api_key}")
