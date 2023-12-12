import requests
import configparser
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
#from requests.packages.urllib3.util.retry import Retry

config = configparser.ConfigParser()
config.read('settings/config.ini', encoding="utf-8")
bot_token = config.get("bot", "bot_token")

TELEGRAM_TOKEN = bot_token
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"

retry_strategy = Retry(
    connect=3,
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504, 104, 403],
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
        return self.session.request(method, url, **kwargs)


def escape_telegrambot_underscore(txt):
    return txt.replace(" " * 4, "") \
        .replace("_", f"_") \
        .replace("-", f"-") \
        .replace("~", f"~") \
        .replace("`", f"`") \
        .replace(".", f".")


def send_message(text, chat_id, parse_mode=None, notify=True):
    browser = Browser()
    payload = {
        'text': escape_telegrambot_underscore(text),
        'chat_id': chat_id,
        'parse_mode': parse_mode,
        'disable_notification': not notify
    }
    return browser.send_request("POST",
                                url=f"{TELEGRAM_API_URL}sendMessage",
                                json=payload
                                )
