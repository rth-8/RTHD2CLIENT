from requests_oauthlib import OAuth2Session
import pickle
from my_secrets import MySecrets

OAUTH_URL = "https://www.bungie.net/en/OAuth/Authorize"
REDIRECT_URL = "https://localhost:8000"
TOKEN_URL = "https://www.bungie.net/platform/app/oauth/token/"

class MyOAuth():
    def __init__(self, secrets: MySecrets) -> None:
        self.secrets = secrets
        self.session = None
        self.token = None
        self._init()


    def _load_token(self):
        try:
            with open('token/token.pkl', 'rb') as f:
                self.token = pickle.load(f)
                # print(f"LOADED TOKEN: {self.token}")
        except FileNotFoundError:
            print("Token not saved yet.")
            self.token = None
    

    def _save_token(self):
        with open('token/token.pkl', 'wb') as f:
            pickle.dump(self.token, f)
    

    def _update_token(self, token):
        print("Updating token...")
        self.token = token
        self.session.token = self.token
        self._save_token()


    def _init(self):
        self._load_token()
        if self.token:
            self.session = OAuth2Session(
                client_id=self.secrets.client_id,
                token=self.token,
                auto_refresh_kwargs={'client_id': self.secrets.client_id, 'client_secret': self.secrets.client_secret,},
                auto_refresh_url=TOKEN_URL,
                token_updater=self._update_token)
        else:
            self.session = OAuth2Session(client_id=self.secrets.client_id, redirect_uri=REDIRECT_URL)


    def start_oauth(self):
        print("Start oauth...")
        oauth_link = self.session.authorization_url(OAUTH_URL)
        print(f"OAuth link: {oauth_link}")
        return oauth_link[0]

    
    def get_and_store_token(self, resp_url):
        # if new url is redirect url and contains "code", then try extract auth token and store it in session
        if REDIRECT_URL in resp_url and "code" in resp_url:
            self.token = self.session.fetch_token(
                                include_client_id=self.secrets.client_id, 
                                client_secret=self.secrets.client_secret, 
                                token_url=TOKEN_URL, 
                                authorization_response=resp_url)
            print(f"RECEIVED TOKEN: {self.token}")
            self._save_token()
