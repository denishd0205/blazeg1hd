import configparser

config = configparser.ConfigParser()
config.read('settings/config.ini', encoding="utf-8")

secret = config.get("webhook", "secret_token")

# https://ajuda.kiwify.com.br/pt-br/article/como-funcionam-os-webhooks-2ydtgl/?1607864862382
# https://www.notion.so/Webhooks-pt-br-c77eb84be10c42e6bb97cd391bca9dce
API_TOKEN = secret


def get_payment(response, users):
    data = {
        "user": {}
    }
    try:
        data["user"]["email"] = response["Customer"].get("email")
    except:
        data["user"]["email"] = "teste123@gmail.com"
    status_payment = response["order_status"]
    if status_payment == "paid":
        data["user"]["payment_status"] = "PAID"
        users.change_payment_status(data)
    elif status_payment == "expired":
        data["user"]["payment_status"] = "EXPIRED"
        users.change_payment_status(data)
    elif status_payment == "refunded":
        data["user"]["payment_status"] = "REFUNDED"
        users.change_payment_status(data)
    elif status_payment == "cancelled":
        data["user"]["payment_status"] = "CANCELLED"
        users.change_payment_status(data)
    else:
        data["user"]["payment_status"] = status_payment
        users.change_payment_status(data)
