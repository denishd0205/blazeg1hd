import time
import requests
from threading import Thread
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
#from requests.packages.urllib3.util.retry import Retry
from core.ws import connect_websocket, \
    get_ws_result, set_ws_closed

URL_BASE = "https://blaze.com"
VERSION_API = "0.0.1-professional"

retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504, 104],
    allowed_methods=["HEAD", "POST", "PUT", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)


class Browser(object):

    def __init__(self):
        self.response = None
        self.headers = None
        self.session = requests.Session()

    def set_headers(self, headers=None):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/87.0.4280.88 Safari/537.36"
        }
        if headers:
            for key, value in headers.items():
                self.headers[key] = value

    def get_headers(self):
        return self.headers

    def send_request(self, method, url, **kwargs):
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        print(url, kwargs)
        return self.session.request(method, url, **kwargs)


class BlazeAPI(Browser):

    def __init__(self, username=None, password=None):
        super().__init__()
        self.proxies = None
        self.token = None
        self.is_logged = False
        self.wallet_id = None
        self.username = username
        self.password = password
        self.set_headers()
        self.headers = self.get_headers()
        self.start_websocket()
        if self.username and self.password:
            self.auth()

    def get_code(self):
            try:
                try:
                    url = requests.get(
                        f"http://127.0.0.1:8867/hcaptcha/token")
                    print("localhost")
                except:
                    url = requests.get(
                        f"http://181.223.148.23:8867/hcaptcha/token")
                    print("Cloud")
                    pass
                if url.status_code == 500:
                    return False
                elif url.status_code == 200:
                    return json.loads(url.content)
            except:
                print("Erro ao conectar!")
                return False
                
    def auth(self):

        a = self.get_code()

        data = {
            "username": self.username,
            "password": self.password
        }
        self.headers["x-captcha-response"] = f"{a}"
        self.headers["referer"] = f"{URL_BASE}/pt/?modal=auth&tab=login"
        self.response = self.send_request("PUT",
                                          f"{URL_BASE}/api/auth/password",
                                          json=data,
                                          headers=self.headers)

        if not self.response.json().get("error"):
            self.token = self.response.json()["access_token"]
            self.is_logged = True

        return self.response.json()

    def reconnect(self):
        return self.auth()

    def get_profile(self):
        self.headers["authorization"] = f"Bearer {self.token}"
        self.response = self.send_request("GET",
                                          f"{URL_BASE}/api/users/me",
                                          headers=self.headers)
        return self.response.json()

    def get_balance(self):
        self.headers["referer"] = f"{URL_BASE}/pt/games/double"
        self.headers["authorization"] = f"Bearer {self.token}"
        self.response = self.send_request("GET",
                                          f"{URL_BASE}/api/wallets",
                                          headers=self.headers)
        if self.response.status_code == 502:
            self.reconnect()
            return self.get_balance()
        elif self.response:
            self.wallet_id = self.response.json()[0]["id"]
        return self.response.json()

    def get_ws_result(self):
        self.response = get_ws_result()
        return self.response

    def get_status(self):
        self.response = get_ws_result()
        if self.response:
            return self.response["status"]
        return None

    def get_ranking(self, **params):
        list_best_users = []
        while True:
            self.response = self.get_roulettes()
            if self.response:
                if self.response.json()["status"] == 'waiting':
                    for user_rank in self.response.json()["bets"]:
                        if user_rank["user"]["rank"] in params["ranks"]:
                            list_best_users.append(user_rank)
                    return list_best_users
            time.sleep(2)

    def get_trends(self):
        while True:
            self.response = self.get_roulettes()
            if self.response:
                if self.response.json()["status"] == 'waiting':
                    return self.response.json()
            time.sleep(2)

    def double_bets(self, color, amount):
        result_dict = {
            "result": False,
        }
        data = {
            "amount": str(f"{float(amount):.2f}"),
            "currency_type": "BRL",
            "color": 1 if color == "vermelho" else 2 if color == "preto" else 0,
            "free_bet": False,
            "wallet_id": self.wallet_id
        }

        self.headers["authorization"] = f"Bearer {self.token}"
        self.response = self.send_request("POST",
                                          f"{URL_BASE}/api/roulette_bets",
                                          json=data,
                                          headers=self.headers)
        if self.response:
            result_dict = {
                "result": True,
                "object": self.response,
                "message": "Operação realizada com sucesso!!!"
            }

        return result_dict

    async def awaiting_double(self, verbose=True):
        while True:
            try:
                self.response = get_ws_result()
                if verbose:
                    print(f'\rSTATUS: {self.response["status"]}', end="")
                if self.response["color"] is not None and self.response["roll"] is not None:
                    return self.response
            except:
                pass
            time.sleep(0.1)

    async def get_double(self):
        result_dict = None
        data = await self.awaiting_double(verbose=False)
        if data:
            result_dict = {
                "roll": data["roll"],
                "color": data["color"]
            }
        return result_dict

    def get_last_doubles(self):
        self.headers["referer"] = f"{URL_BASE}/pt/games/double"
        self.response = self.send_request("GET",
                                          f"{URL_BASE}/api/roulette_games/recent",
                                          proxies=self.proxies,
                                          headers=self.headers)
        if self.response:
            result = {
                "items": [
                    {"color": "branco" if i["color"] == 0 else "vermelho" if i["color"] == 1 else "preto",
                     "value": i["roll"], "created_date": datetime.strptime(
                        i["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S")
                     } for i in self.response.json()]}
            return result
        return False

    def get_last_crashs(self):
        self.headers["referer"] = f"{URL_BASE}/pt/games/crash"
        self.response = self.send_request("GET",
                                          f"{URL_BASE}/api/crash_games/recent",
                                          proxies=self.proxies,
                                          headers=self.headers)
        if self.response:
            result = {
                "items": [{"color": "preto" if float(i["crash_point"]) < 2 else "verde", "value": i["crash_point"]}
                          for i in self.response.json()]}
            return result
        return False

    def get_roulettes(self):
        self.response = self.send_request("GET",
                                          f"{URL_BASE}/api/roulette_games/current",
                                          proxies=self.proxies,
                                          headers=self.headers)
        return self.response

    @staticmethod
    def start_websocket():
        thread_ws = Thread(target=connect_websocket, args=[])
        thread_ws.daemon = True
        thread_ws.start()

    @staticmethod
    def stop_websocket():
        set_ws_closed(True)
