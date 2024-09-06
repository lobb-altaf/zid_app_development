import requests

CLIENT_ID = 3348
CLIENT_SECRET = "6CpbZVTgOZjwdp2A7IoUGpYievg2xh4iuYCbcp8k"
BASE_URL = "https://oauth.zid.sa"


def get_manager_profile(auth_token: str, access_token: str):

    url = "https://api.zid.sa/v1/managers/account/profile"

    headers = {
        "Accept-Language": "",
        "Authorization": f"Bearer {auth_token}",
        "X-Manager-Token": f"{access_token}",
        "User-Agent": "",
        "Accept": "application/json",
    }

    response = requests.get(url, headers=headers)
    # print(response.text)
    response.raise_for_status()

    return response.json()


def refresh_access_token(refresh_token):
    url = "https://oauth.zid.sa/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": "https://lm1h3n2p-8000.inc1.devtunnels.ms/callback/",
    }
    response = requests.post(url, data=data)
    # response.raise_for_status()
    return response.json()
