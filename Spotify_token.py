import requests
import base64
import json
import time

class Spotify_token:
    def __init__(self, client_id, client_secret, cache_file=".cache"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.cache_file = cache_file
        self.OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"
        self.token_info = self.load_token_from_cache()


    def load_token_from_cache(self):
        try:
            with open(self.cache_file, 'r') as file:
                token_info = json.load(file)
                return token_info
        except FileNotFoundError:
            print(f"can't find file {self.cache_file}")
            return None
        except json.JSONDecodeError:
            print(f"file {self.cache_file} format error")
            return None


    def get_token(self):
        current_time = int(time.time())
        if current_time >= self.token_info.get("expires_at", 0):
            print("Token expired refeshing token！")
            return self.refresh_access_token()
        else:
            return self.token_info.get("access_token", 0)


    def refresh_access_token(self):
        print("refreshing Access token...")

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.token_info.get("refresh_token")
        }

        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        try:
            response = requests.post(self.OAUTH_TOKEN_URL, data=payload, headers=headers)
            response.raise_for_status()

            current_time = int(time.time())

            new_token_info = response.json()
            new_token_info["expires_at"] = current_time + new_token_info["expires_in"]
            new_token_info["refresh_token"] = self.token_info.get("refresh_token")

            with open(self.cache_file, 'w') as file:
                json.dump(new_token_info, file, indent=4)

            print("Access token refresh success！")
            return new_token_info["access_token"]

        except requests.exceptions.HTTPError as http_error:
            print(f"HTTP error: {http_error}")
        except Exception as error:
            print(f"error: {error}")

if __name__ == "__main__":
    spotify_api = Spotify_token("d60554d0a7184e77b6fe1ef381f8d261", "04f28a8bc40c483dbb5f916c8a2fdd96", ".cache")
    access_token = spotify_api.get_token()
    if access_token:
        print(f"Access Token {access_token}")