import random
import configparser
from python_telegram_api import send_message

config = configparser.ConfigParser()
config.read('settings/config.ini', encoding="utf-8")

bot_support = config.get("bot", "bot_support")


def info_message(user, hashed_token):
    if hashed_token:
        message = fr""" *ACESSO LIBERADO*
        Seu acesso ao sistema automático Double foi liberado!!!
        Insira o código abaixo, quando solicitado.
        
        __{hashed_token}__
        """
    else:
        message = fr""" *ACESSO BLOQUEADO*
        Seu acesso ao sistema automático Double está bloqueado!!!
        Efetue o pagamento e volte a usar o melhor automatizador de apostas da galáxia!!!
        Obs: Após efetuar o pagamento entre em contato com nosso [suporte]({bot_support}) e informe o seguinte ID:
        {user.user_bot}
        """
    send_message(message, user.user_bot, parse_mode="Markdown")


def gale_message(data):
    message = f'Aplicando martingale {data["variables"]["count_martingale"]}'
    send_message(message, data["user"]["user_bot"], parse_mode="Markdown")


def view_sequence(data, doubles):
    message = fr"""🎰 *Últimos giros* 🎰
    {" ".join([f"{str(item[0]):>2}" for item in doubles][7:])}    
    {"".join(["⚫" if item[1] == "preto" else "🔴" if item[1] == "vermelho" else "⚪" for item in doubles][7:])}
    """
    send_message(message, data["user"]["user_bot"], parse_mode="Markdown")


def view_config(data):
    message = fr"""⚙ Dados da conta ⚙️
    🚀 Tipo: {data["settings"]["account_type"]}
    💰 Saldo: R$ {round(float(data["variables"]["balance"]), 2):.2f}
    """
    send_message(message, data["user"]["user_bot"], parse_mode="Markdown")


def confirmed_bets(data):
    message = fr"""📌 Aposta realizada
    🎲 Cor: {"⚫" if data["user"]["color_bet"] == "preto" else "🔴"}
    💰 Valor: R$ {round(float(data["settings"]["enter_value"]), 2):.2f}
    {fr"🛡️ Proteção de: {data['settings']['protection_value']:.2f}" 
    if data["settings"]["protection_hand"] == "SIM" else ""}
    """
    send_message(message, data["user"]["user_bot"], parse_mode="Markdown")


def opportunity_alert(data):
    message = fr"🚨 *Nova oportunidade de encontrada* 🚨"
    send_message(message, data["user"]["user_bot"], parse_mode="Markdown")


def awaiting_result(data):
    message = fr"🕐 *Aguardando resultado* 🕐"
    send_message(message, data["user"]["user_bot"], parse_mode="Markdown")


def win_alert(data):
    message = fr"""Resultado: ✅ *Win!!!*
    💰 Lucro: R$ {round(float(data["variables"]["profit"]), 2):.2f}
    💰 Saldo: R$ {round(float(data["variables"]["balance"]), 2):.2f}
    🎯 Placar: ✅ {data["variables"]["count_win"]} X {data["variables"]["count_loss"]} ❌
    """
    send_message(message, data["user"]["user_bot"], parse_mode="Markdown")


def loss_alert(data):
    message = fr"""*Resultado:* ❌ *Loss!!!*
    💰 Lucro: R$ {round(float(data["variables"]["profit"]), 2)}
    💰 Saldo: R$ {round(float(data["variables"]["balance"]), 2)}
    🎯 Placar: ✅ {data["variables"]["count_win"]} X {data["variables"]["count_loss"]} ❌
    """
    send_message(message, data["user"]["user_bot"], parse_mode="Markdown")


def stop_win_alert(data):
    message = fr"""✅ Stop *Win* atingido!!!
    💰 Saldo: R$ {round(float(data["variables"]["balance"]), 2):.2f}
    """
    send_message(message, data["user"]["user_bot"], parse_mode="Markdown")


def stop_loss_alert(data):
    message = fr"""❌ Stop *Loss* atingido!!!
    💰 Saldo: R$ {round(float(data["variables"]["balance"]), 2):.2f}
    """
    send_message(message, data["user"]["user_bot"], parse_mode="Markdown")


def random_messages(data):
    messages = [
        fr"""teste1""",
        fr"""teste2""",
        fr"""teste3"""
    ]
    send_message(random.choice(messages), data["user"]["user_bot"], parse_mode="Markdown")
