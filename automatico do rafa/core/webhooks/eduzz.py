import configparser

config = configparser.ConfigParser()
config.read('settings/config.ini', encoding="utf-8")

secret = config.get("webhook", "secret_token")

# https://orbita.eduzz.com/producer/config-api
API_TOKEN = secret


def get_status_payment(number):
    status = {
        1: "open",
        3: "paid",
        4: "cancelled",
        6: "waitint_refund",
        7: "refunded",
        10: "expired",
        11: "recovering",
        15: "waiting_payment"
    }
    return status.get(number)


def get_payment(response, users):
    data = {
        "user": {}
    }
    data["user"]["email"] = response.get("cus_email")
    status_payment = get_status_payment(int(response["trans_status"]))
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
