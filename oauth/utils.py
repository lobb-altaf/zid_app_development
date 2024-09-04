import requests

CLIENT_ID = 3348
CLIENT_SECRET = "6CpbZVTgOZjwdp2A7IoUGpYievg2xh4iuYCbcp8k"
BASE_URL = "https://oauth.zid.sa"

test = {
    "access_token": "eyJpdiI6IlZIOTRnQm5mWGphLzA1Wkw4MmRySVE9PSIsInZhbHVlIjoia0lDc3hUdmlOSU5qbWNOM2tPYStLRitzalVqT0VrVkJGUHJ0Qm52Rll0Z3RVUWdhc2pVYnZCL051Z3ZVWll4UThOQ0diZ1B6cUtiUWdpMFI2NzZDSFJnZHVpcFBXV1RXSFhWNXU1cFpoUEI1R0VwdjduQ2cxR0RuZnRiYnFXaFFJT04wcUZGZk0xQkZPZ0VaS1djSlJPU0x3bmpCb21GTktGU0JBQ2FmSmZhSGFmU3BXdUQ2Z2lwMFgzbmxHbDRIbDBBODUwVGZianczS1crbmRIZlVSTXE2TjVac0IyUkg4aXlrb0U1UTVZaz0iLCJtYWMiOiI1MmQ0NmYzMDNkNDdlYjUxMWIzMzBhMTkxZjI3MDAxNGRhZDJkNTQxZDgyNTIyNjQzODg3NGI5NTlmMjlmMzcwIiwidGFnIjoiIn0=",
    "token_type": "Bearer",
    "expires_in": 31535999,
    "authorization": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzMzQ4IiwianRpIjoiZDdlMzIzMDU3ZWVkMDM4OGI1OTc4MTY2OTBjYWViZDViOTg3N2U0ZTBkMmJiYjIxMDBhNTNmY2NhMTFiYzFjOWNhYTA0NjI0Nzk3Y2E2MGMiLCJpYXQiOjE3MjU0NzMwNTIuMDQ5MDEsIm5iZiI6MTcyNTQ3MzA1Mi4wNDkwMTMsImV4cCI6MTc1NzAwOTA1MS45OTk4MTgsInN1YiI6IjY4MDc4MSIsInNjb3BlcyI6WyJ0aGlyZF9hY2NvdW50X3JlYWQiLCJ0aGlyZF9jYXRlZ29yaWVzX3dyaXRlIiwidGhpcmRfY3VzdG9tZXJzX3dyaXRlIiwidGhpcmRfb3JkZXJfd3JpdGUiLCJ0aGlyZF9jb3Vwb25zX3dyaXRlIiwidGhpcmRfZGVsaXZlcnlfb3B0aW9uc193cml0ZSIsInRoaXJkX3dlYmhvb2tfd3JpdGUiLCJ0aGlyZF9wcm9kdWN0X3dyaXRlIiwidGhpcmRfY2F0YWxvZ193cml0ZSIsInRoaXJkX2pzX3dyaXRlIiwidGhpcmRfY3JlYXRlX29yZGVyIiwidGhpcmRfcHJvZHVjdF9zdG9ja193cml0ZSIsInRoaXJkX2ludmVudG9yeV93cml0ZSIsImVtYmVkZGVkX2FwcHNfdG9rZW5zX3dyaXRlIl19.LAmRp83II5yz9SE2O-Vx90Mx8rSl8TYugNDrP2tF5WtUeFqPcXQSjJ2f0giwdKWZEnNb1Ss5Xd7-iG-U8v_N4S6T5oEr9cE5JyXizvCPrj1hAIv_RO1N1btxS5I1gEBbexjhHSEcb54WdK4FJYCDOsPk8fCfpYPYOehGAQbDaHlxSvjsLgdw-0MGdx8paLGKvj-SWnTuneHcNE2zUl4Oud3SoH36BJSjGn17UeAu2QEPDVraAC0RKTZk6wqZeEm7Yc0oED9Y6Ezr03f01-c8Uu4fG_eARhKVGkoi6Xb0aBTxGzATCtg7Bn2Rb0UZEkRA_OnebMe-21GktVAb0tT9OGdctX8FOJTWFOdUsWTIZczpv1oWhnJnZ8odVvb4oOnFT9-IXZE6t8pT8bAc8UEqXGFi2XabpQg_FfEPT7aj-AmTL0ukoU87tvWlXJET3k77UVsrTioezmzQoZww99VYr2opfYAQngm25rJ70ua5qrK9OuXkuO0MosB9hFKEesDIwySc-7-TahPAkgM429mrWiJjNcPvIHrTjJGHwUXZobBUFkE2cvZl0qqcAoGhiU3m8Gr3vR1blE01FO1lqnlqTCZVOcFWPOoRKepU-rmHO5bRg7bCrkjb5pslXSgKTaONUKqgaXq_ntx_i6Jvt5D27dZdeuYuQQakUOyKHaNeyq4",
    "refresh_token": "def502004a687c35fb46089019f3080f3017742d012026301bbc3ebfba0f8db09ffffd33aecff8bbbebf39db936d7b6115f88e97c39b50ab664216a6bf089a7e45fbe14e5956de9ddac397ad6ae7db75fbd75ae69985ae2756d4bfaa0d0de6bcba35defb59ef92068d01979384e1d9161de47afa01742704a38bee64bc415d1a96a0630bd57604ed34f6b24fed8c9d47b009dd42c3b3889c414e6c2fc166a5f18e5f1146560439224e77571a5c0a9e490c6b3379de1a4f2a82321790fa895817f823ef066e6407367fe2cf28493dc54ea6aeb9e1b051fcf9e60ea73136ce26978b490d4f31e1bfbc155383a556b1e1b7008cc2734006e1950c6fedcbe5a1f5e72fb14ff5b4cc25edad6362af6ab3b8491f3c71522ba049c4741b0894cd4e50cd812b95b773610ef6462b5b51938f18c198bf73961cee34f70930983f93cc88e3bb34f3f6b6709376d89928393995c6b17079bd61bc146649b97e3e2a95cc37520a6c472474c6e4daea2337d13debb298d038bf88832562e909cb47737c0c5f76a5e933a5c4494d40dba0bd6b1449f38f7954b6e71a122e4a1e9e457f76ede26f60e01b11eb07c6c01cb42b469fa7aedee6e648ab5d243b282a06cd3c9fae4877216847ae69371dffb27ed72fa426e0ce3c9f6beffa87108600ecff39eb53e8a6ff0f85709a8a971c25c5a5e0599d4626e3d41465599495a9900f6d90b74b850a92f0be2160ae9de555219f3929da2552130ec93a97a72a66ed492ec637d4ad1036a1f88f11969c53fe89990f9fc4365f017d1edf270f9d6c497cd3c6734d326a3bfb31b832fd44ea337ca11499d8d643d084fe35e5ddb1a8c4a9252b49af01358ebe81f2da399c322597f6e0759df8a7d97fe0373acf2ba3a09639af7352aa8ab65236d3b2ada8bcc5afff2427585da119d9fb5161136c0f8d59f2b547704b9fac6dc469a46b3bb25accf0516326ca35",
}


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
    print(response.text)
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


# response = refresh_access_token(test["refresh_token"])
# print("sda", response)
# get_manager_profile(test["authorization"], test["access_token"])
#
