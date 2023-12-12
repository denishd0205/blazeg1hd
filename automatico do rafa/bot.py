import json
import os
import subprocess
import configparser
from datetime import datetime
from roulette import Double
from enum import Enum, auto
from core.api import BlazeAPI
from utils.helpers import Buttons
from controllers import check_hashed_token, UserController
from telethon.sync import TelegramClient, events, Button

__author__ = "TK Global Technology"
__version__ = "0.1"

__message__ = f"""
Use com moderação, pois gerenciamento é tudo!
suporte: (47)999673382
"""

config = configparser.ConfigParser()
config.read('settings/config.ini', encoding="utf-8")

controller = UserController()

phone = config.get("bot", "phone")
api_id = config.getint("bot", "api_id")
api_hash = config.get("bot", "api_hash")
session_name = config.get("bot", "session_name")
bot_token = config.get("bot", "bot_token")
bot_support = config.get("bot", "bot_support")

fake_user = {
    "user": {
        "user_bot": 1969084565,
        "email": f"teste123@gmail.com",
        "password": "teste123",
        "token": None,
        "wallet": None,
    },
    "settings": {
        "account_type": "DEMO",
        "enter_type": "VALOR",
        "first_amount": 2,
        "enter_value": 2,
        "stop_gain": 100,
        "stop_loss": 30,
        "protection_hand": "NÃO",
        "protection_value": 2,
        "martingale": 2,
        "white_martingale": "NÃO",
        "martingale_multiplier": 2,
        "white_multiplier": 1.5,
        "stop_type": "VALOR",
        "white_gerenciamento_tk": "NÃO",
        "gerenciamento_tk_qtd": 3,
        "gerenciamento_tk_qtd_win": 4,
        "gerenciamento_tk_qtd_loss": 0
    },
    "variables": {
        "count_loss": 0,
        "count_win": 0,
        "count_martingale": 0,
        "profit": 0,
        "balance": 0,
        "created": 0,
        "is_gale": False
    },
    "strategies": [
        {"color": "preto", "sequence": "v,v,v"},
        {"color": "vermelho", "sequence": "p,p,p"}
    ]
}
user_dict = {}
items_list = []
strategies_list = []


def init_variables(data):
    data["variables"]["count_loss"] = 0
    data["variables"]["count_win"] = 0
    data["variables"]["count_martingale"] = 0
    data["variables"]["profit"] = 0
    data["variables"]["balance"] = data["variables"]["balance"]
    data["variables"]["created"] = 0
    data["variables"]["is_gale"] = False
    return data


def check_user(param):
    result_user = controller.check_user_exists(param)
    return result_user


def get_user(sender):
    result = check_user(sender)
    if not result:
        fake_user["user"]["user_bot"] = sender
        fake_user["user"]["email"] = f"teste{sender}@gmail.com"
        result = controller.create(fake_user)
    elif not result["settings"]:
        controller.delete(result["user"]["id"])
        fake_user["user"]["user_bot"] = sender
        fake_user["user"]["email"] = f"teste{sender}@gmail.com"
        result = controller.create(fake_user)
    return result


class State(Enum):
    WAIT_ENABLE = auto()
    WAIT_DISABLE = auto()
    WAIT_START = auto()
    WAIT_MENU = auto()
    WAIT_CONFIG = auto()
    WAIT_USERNAME = auto()
    WAIT_PASSWORD = auto()
    WAIT_TOKEN = auto()
    WAIT_CONFIRM = auto()
    WAIT_ENTER_VALUE = auto()
    WAIT_STOP_GAIN = auto()
    WAIT_STOP_LOSS = auto()
    WAIT_PROTECTION_VALUE = auto()
    WAIT_MARTINGALE = auto()
    WAIT_MARTINGALE_MULTIPLIER = auto()
    WAIT_WHITE_MULTIPLIER = auto()
    WAIT_MORE_CONFIRM = auto()
    WAIT_NEW_CONFIRM = auto()
    WAIT_ADD_ITEM = auto()
    WAIT_SEQUENCE = auto()
    WAIT_COLOR = auto()
    WAIT_BLACK = auto()
    WAIT_RED = auto()
    WAIT_GERENCIAMENTO_TK = auto()
    WAIT_GERENCIAMENTO_SEQUENCIA = auto()
    WAIT_GERENCIAMENTO_QTD_WIN = auto()
    WAIT_GERENCIAMENTO_QTD_LOSS = auto()



class TelegramBot(object):

    def __init__(self):
        super(TelegramBot).__init__()
        self.bot = TelegramClient(session_name, api_id, api_hash)
        self.conversation_state = {}
        self.state = State
        self.double = None

        @self.bot.on(events.NewMessage())
        async def handler(event):
            global user_dict, items_list, strategies_list
            sender = await event.get_sender()
            sender_id = sender.id
            msg_id = event.id
            if sender_id != 5444523281:
                user_dict = get_user(sender_id)
                buttons = Buttons.get_account_buttons(user_dict)
                more_buttons = Buttons.get_more_buttons(user_dict)

                if event.text == "🆘 Menu Inicial" or event.text == "/start":
                    self.conversation_state[sender_id] = self.state.WAIT_START
                elif event.text == "⚙️ Configurar":
                    await event.respond("__**Em que posso te ajudar???**__", buttons=Button.clear())
                    self.conversation_state[sender_id] = self.state.WAIT_CONFIG
                elif event.text == "🚀 Iniciar":
                    self.conversation_state[sender_id] = self.state.WAIT_ENABLE
                elif event.text == "⏹ Parar":
                    self.conversation_state[sender_id] = self.state.WAIT_DISABLE

                state = self.conversation_state.get(sender_id)

                if state == self.state.WAIT_START:
                    sender = await event.get_sender()
                    markup = event.client.build_reply_markup(Buttons.get_start_button())
                    await event.respond(f"Olá {'**Visitante**' if not sender.username else sender.username} .\n"
                                        f"Sou o __**RafABotDouble**__, bem vindo!!!",
                                        buttons=markup)
                    self.conversation_state[sender_id] = self.state.WAIT_MENU
                elif state == self.state.WAIT_MENU:
                    markup = event.client.build_reply_markup(Buttons.get_menu_buttons())
                    await event.respond("__**Em que posso te ajudar???**__", buttons=markup)
                elif state == self.state.WAIT_CONFIG:
                    await event.respond("__**Configurações da Conta**__", buttons=buttons)
                    self.conversation_state[sender_id] = self.state.WAIT_MENU
                elif state == self.state.WAIT_USERNAME:
                    user_dict["user"]["email"] = event.text
                    buttons[0][0].text = f"Usuário = {event.text}"
                    await event.respond("__**Usuário alterado com sucesso!!!**__", buttons=buttons)
                elif state == self.state.WAIT_PASSWORD:
                    user_dict["user"]["password"] = event.text
                    buttons[1][0].text = f"Senha = {event.text}"
                    await event.respond("__**Senha alterada com sucesso!!!**__", buttons=buttons)
                elif state == self.state.WAIT_TOKEN:
                    await self.bot.delete_messages(event.sender_id, [msg_id])
                    if not check_hashed_token(str(user_dict["user"]["user_bot"]), event.text):
                        await self.bot.delete_messages(event.sender_id, [msg_id])
                        await event.reply("🚫 __**Token inválido!!!**__")
                        await event.reply(f"__Entre em contato com nosso suporte [suporte]({bot_support})"
                                          f" e informe o código {sender_id} para adquirir um token de acesso.__")
                        await event.respond("__**Insira um token válido.**__")
                        await self.bot.delete_messages(sender_id, [msg_id])
                    else:
                        await self.bot.delete_messages(event.sender_id, [msg_id])
                        user_dict["user"]["hashed_token"] = event.text
                        self.conversation_state[sender_id] = self.state.WAIT_ENABLE
                        await self.bot.delete_messages(event.sender_id, [msg_id])
                        await event.reply(f'✅ __**Token válido!!!**__\n'
                                          f'__**Validade:**__ {user_dict["user"]["expire_in"].strftime("%d/%m/%Y")}')
                elif state == self.state.WAIT_SEQUENCE:
                    input_text = ",".join(event.text.lower().replace(",", ""))
                    items_list.append(input_text)
                    expected_color_buttons = Buttons.get_expected_colors_buttons()
                    await event.respond("__**Qual a cor esperada para essa sequência ???**__",
                                        buttons=expected_color_buttons)
                elif state == self.state.WAIT_CONFIRM:
                    del self.conversation_state[sender_id]
                elif state == self.state.WAIT_ENTER_VALUE:
                    user_dict["settings"]["enter_value"] = event.text
                    more_buttons[2][0].text = f"Valor Entrada = {event.text}"
                    await event.respond("__**Configurações Gerais**__", buttons=more_buttons)
                elif state == self.state.WAIT_STOP_GAIN:
                    user_dict["settings"]["stop_gain"] = event.text
                    more_buttons[4][0].text = f"Stop Gain = {event.text}"
                    await event.respond("__**Configurações Gerais**__", buttons=more_buttons)
                elif state == self.state.WAIT_STOP_LOSS:
                    user_dict["settings"]["stop_loss"] = event.text
                    more_buttons[5][0].text = f"Stop Loss = {event.text}"
                    await event.respond("__**Configurações Gerais**__", buttons=more_buttons)
                elif state == self.state.WAIT_PROTECTION_VALUE:
                    user_dict["settings"]["protection_value"] = event.text
                    more_buttons[7][0].text = f"Valor da Proteção = {event.text}"
                    await event.respond("__**Configurações Gerais**__", buttons=more_buttons)
                elif state == self.state.WAIT_MARTINGALE:
                    user_dict["settings"]["martingale"] = event.text
                    more_buttons[8][0].text = f"Martingale = {event.text}"
                    await event.respond("__**Configurações Gerais**__", buttons=more_buttons)
                elif state == self.state.WAIT_MARTINGALE_MULTIPLIER:
                    user_dict["settings"]["martingale_multiplier"] = event.text
                    more_buttons[10][0].text = f"Multiplicador Martingale = {event.text}"
                    await event.respond("__**Configurações Gerais**__", buttons=more_buttons)
                elif state == self.state.WAIT_WHITE_MULTIPLIER:
                    user_dict["settings"]["white_multiplier"] = event.text
                    more_buttons[11][0].text = f"Multiplicador Branco = {event.text}"
                    await event.respond("__**Configurações Gerais**__", buttons=more_buttons)
                
                elif state == self.state.WAIT_GERENCIAMENTO_TK:
                    user_dict["settings"]["white_gerenciament_tk"] = event.text
                    more_buttons[12][0].text = f"Gerenciamento TK Space = {event.text}"
                    await event.respond("__**Configurações Gerais**__", buttons=more_buttons)
                elif state == self.state.WAIT_GERENCIAMENTO_SEQUENCIA:
                    user_dict["settings"]["gerenciament_tk_qtd"] = event.text
                    more_buttons[13][0].text = f"Quantidade de entradas = {event.text}"
                    await event.respond("__**Configurações Gerais**__", buttons=more_buttons)
                elif state == self.state.WAIT_GERENCIAMENTO_QTD_WIN:
                    user_dict["settings"]["gerenciament_tk_qtd_win"] = event.text
                    more_buttons[14][0].text = f"Reiniciar após win = {event.text}"
                    await event.respond("__**Configurações Gerais**__", buttons=more_buttons)
                elif state == self.state.WAIT_GERENCIAMENTO_QTD_LOSS:
                    user_dict["settings"]["gerenciament_tk_qtd_loss"] = event.text
                    more_buttons[15][0].text = f"Reiniciar após loss = {event.text}"
                    await event.respond("__**Configurações Gerais**__", buttons=more_buttons)

                elif state == self.state.WAIT_MORE_CONFIRM:
                    markup = event.client.build_reply_markup(Buttons.get_menu_buttons())
                    await event.respond("__**Vamos apostar???**__", buttons=markup)
                elif state == self.state.WAIT_NEW_CONFIRM:
                    await self.bot.delete_messages(event.sender_id, [msg_id])
                    del self.conversation_state[sender_id]
                elif state == self.state.WAIT_ENABLE:
                    hashed_token = user_dict["user"]["hashed_token"]
                    user_dict = check_user(sender_id)
                    if not hashed_token:
                        await event.respond("__**Insira um token válido.**__")
                        await self.bot.delete_messages(sender_id, [msg_id])
                        self.conversation_state[sender_id] = self.state.WAIT_TOKEN
                        return
                    email = user_dict["user"]["email"]
                    password = user_dict["user"]["password"]
                    ba = BlazeAPI(email, password)
                    if user_dict and ba.is_logged or not hashed_token:
                        balance = ba.get_balance()[0]["balance"]
                        user_dict["user"]["token"] = ba.token
                        user_dict["variables"]["balance"] = balance
                        user_dict["variables"]["first_balance"] = balance
                        user_dict["user"]["wallet"] = ba.wallet_id
                        user_dict["settings"]["first_amount"] = user_dict["settings"]["enter_value"]
                        user_dict["settings"]["first_protection"] = user_dict["settings"]["protection_value"]
                        if not user_dict["user"]["is_active"] or not self.double:
                            user_dict["user"]["is_active"] = True

                            # DESATIVADO, TALVEZ SIRVA EM OUTRO MOMENTO
                            """process_thread = Thread(target=run_task,
                            args=(f"python3 app.py {sender_id}", os.getcwd()), daemon=True)
                            process_thread.start()
                            user_dict["user"]["process_pid"] = process_thread.native_id + 1"""

                            controller.enable(user_dict)
                            del self.conversation_state[sender_id]
                            await event.respond("__**Bot Ativado!**__")
                            self.double = Double(self, sender_id)
                            self.double.start()
                        else:
                            await event.respond("__**RafABot já está ativado!**__")
                    else:
                        await event.respond("__**Você não possui as permissões necessárias!!!**__")
                elif state == self.state.WAIT_DISABLE:
                    user_dict = check_user(sender_id)
                    if user_dict:
                        if user_dict["user"]["is_active"]:
                            user_dict["user"]["is_active"] = False
                            user_dict["user"]["is_betting"] = False
                            user_dict["user"]["color_bet"] = None
                            user_dict["user"]["color_before"] = None
                            if self.double:
                                self.double.quit()
                            user_dict = init_variables(user_dict)
                            controller.disable(user_dict)
                            del self.conversation_state[sender_id]
                            await event.respond("__**Bot Desativado!**__")
                        else:
                            await event.respond("__**Nenhum Bot ativado!**__")
                    else:
                        await event.respond("__**Você não possui as permissões necessárias!!!**__")

                controller.create(user_dict)

        @self.bot.on(events.CallbackQuery())
        async def call_handler(event):
            global user_dict, items_list, strategies_list
            selected = event.data.decode('utf-8')
            msg_id = event.query.msg_id
            sender = await event.get_sender()
            sender_id = sender.id
            user_dict = get_user(sender_id)
            buttons_name = [button_name for button_name in user_dict["settings"]]
            buttons = Buttons.get_account_buttons(user_dict)
            more_buttons = Buttons.get_more_buttons(user_dict)
            strategy_buttons = Buttons.get_strategy_buttons(user_dict)

            account_type = user_dict["settings"]["account_type"]
            enter_type = user_dict["settings"]["enter_type"]
            stop_type = user_dict["settings"]["stop_type"]
            white_martingale = user_dict["settings"]["white_martingale"]
            protection_hand = user_dict["settings"]["protection_hand"]

            gerenciamento_tk = user_dict["settings"]["white_gerenciamento_tk"]
            
            if selected.upper() == "MORE":
                await event.respond("__**Configurações Gerais**__", buttons=more_buttons)
                await self.bot.delete_messages(event.sender_id, [msg_id])
            elif selected.upper() == "NEXT":
                await event.respond("__**Configurações de estratégias**__", buttons=strategy_buttons)
                await self.bot.delete_messages(event.sender_id, [msg_id])
            elif selected.upper() == "CONFIRM":
                await event.respond("__**Configurações da conta salvas com sucesso!!!**__")
                await self.bot.delete_messages(event.sender_id, [msg_id])
                markup = event.client.build_reply_markup(Buttons.get_menu_buttons())
                await event.respond("__**Vamos apostar???**__", buttons=markup)
                self.conversation_state[sender_id] = self.state.WAIT_CONFIRM
            elif selected.upper() == "MORE_CONFIRM":
                await event.respond("__**Configurações da conta salvas com sucesso!!!**__")
                await self.bot.delete_messages(event.sender_id, [msg_id])
                markup = event.client.build_reply_markup(Buttons.get_menu_buttons())
                await event.respond("__**Vamos apostar???**__", buttons=markup)
                self.conversation_state[sender_id] = self.state.WAIT_MORE_CONFIRM
            elif selected.upper() == "NEW_CONFIRM":
                await event.respond("__**Estratégias salvas com sucesso!!!**__", buttons=strategy_buttons)
                await self.bot.delete_messages(event.sender_id, [msg_id])
                self.conversation_state[sender_id] = self.state.WAIT_NEW_CONFIRM
            elif selected.upper() == "USERNAME":
                await event.respond("__**Entre com o e-mail da sua conta blaze**__")
                await self.bot.delete_messages(sender_id, [msg_id])
                self.conversation_state[sender_id] = self.state.WAIT_USERNAME
            elif selected.upper() == "PASSWORD":
                await event.respond(f"__**Entre com a senha da sua conta blaze**__")
                await self.bot.delete_messages(sender_id, [msg_id])
                self.conversation_state[sender_id] = self.state.WAIT_PASSWORD
            elif selected.upper() == "PREVIOUS":
                await self.bot.delete_messages(event.sender_id, [msg_id])
                await event.respond("__**Configurações da Conta**__", buttons=buttons)
                await self.bot.delete_messages(event.sender_id, [msg_id])
                self.conversation_state[sender_id] = self.state.WAIT_CONFIG
            elif selected.upper() == "BACK":
                await self.bot.delete_messages(event.sender_id, [msg_id])
                await event.respond("__**Configurações Gerais**__", buttons=more_buttons)
                await self.bot.delete_messages(event.sender_id, [msg_id])
                self.conversation_state[sender_id] = self.state.WAIT_CONFIG
            elif selected.upper() == "NEW_ITEM":
                await self.bot.delete_messages(event.sender_id, [msg_id])
                await event.respond(f"__**Digite uma sequência onde v = 🔴 e p = ⚫**__")
                await self.bot.delete_messages(event.sender_id, [msg_id])
                self.conversation_state[sender_id] = self.state.WAIT_SEQUENCE
            elif selected in ["red_button", "black_button", "white_button"]:
                expected_color = None
                if selected.upper() == "RED_BUTTON":
                    expected_color = "vermelho"
                elif selected.upper() == "BLACK_BUTTON":
                    expected_color = "preto"
                elif selected.upper() == "WHITE_BUTTON":
                    expected_color = "branco"
                items_list.append(expected_color)
                strategies_list.append(items_list)
                if user_dict.get("strategies"):
                    user_dict["strategies"] += [{"sequence": item[0], "color": item[1]} for item in strategies_list]
                else:
                    user_dict["strategies"] = [{"sequence": item[0], "color": item[1]} for item in strategies_list]
                strategy_buttons = Buttons.get_strategy_buttons(user_dict)
                await event.respond("__**Sequência adicionada com sucesso!!!**__", buttons=strategy_buttons)
                items_list = []
                strategies_list = []
                await self.bot.delete_messages(sender_id, [msg_id])
                self.conversation_state[sender_id] = self.state.WAIT_NEW_CONFIRM
            elif selected.upper().startswith("DELETE_SEQUENCE"):
                button_key = int(selected.upper().split("_")[-1])
                await self.bot.delete_messages(event.sender_id, [msg_id])
                controller.delete_strategies(user_dict, button_key)
                user_dict = get_user(sender_id)
                strategy_buttons = Buttons.get_strategy_buttons(user_dict)
                await event.respond("__**Sequência deletada com sucesso!!!**__", buttons=strategy_buttons)
            elif selected in buttons_name:
                if selected == "account_type":
                    await self.bot.delete_messages(event.sender_id, [msg_id])
                    account_type = "REAL" if account_type != "REAL" else "DEMO"
                    user_dict["settings"]["account_type"] = account_type
                    more_buttons[0][0].text = f"Tipo de Conta = {account_type}"
                    await event.respond("__**Configurações Gerais**__", buttons=more_buttons)
                elif selected == "enter_type":
                    await self.bot.delete_messages(event.sender_id, [msg_id])
                    enter_type = "PORCENTAGEM" if enter_type != "PORCENTAGEM" else "VALOR"
                    user_dict["settings"]["enter_type"] = enter_type
                    more_buttons[1][0].text = f"Tipo de Entrada = {enter_type}"
                    await event.respond("__**Configurações Gerais**__", buttons=more_buttons)
                elif selected == "enter_value":
                    await self.bot.delete_messages(event.sender_id, [msg_id])
                    text = f"{'a porcentagem' if user_dict['settings']['enter_type'].lower() == 'porcentagem' else 'o valor'}"
                    await event.respond(f"__**Digite {text} da entrada inicial**__")
                    self.conversation_state[sender_id] = self.state.WAIT_ENTER_VALUE
                elif selected == "stop_type":
                    await self.bot.delete_messages(event.sender_id, [msg_id])
                    stop_type = "QUANTIDADE" if stop_type != "QUANTIDADE" else "VALOR"
                    user_dict["settings"]["stop_type"] = stop_type
                    more_buttons[3][0].text = f"Tipo de Stop = {stop_type}"
                    await event.respond("__**Configurações Gerais**__", buttons=more_buttons)
                elif selected == "stop_gain":
                    await self.bot.delete_messages(event.sender_id, [msg_id])
                    text = f"{'a quantidade' if user_dict['settings']['stop_type'].lower() == 'quantidade' else 'o valor'}"
                    await event.respond(f"__**Digite {text} do seu StopGain**__")
                    self.conversation_state[sender_id] = self.state.WAIT_STOP_GAIN
                elif selected == "stop_loss":
                    await self.bot.delete_messages(event.sender_id, [msg_id])
                    text = f"{'a quantidade' if user_dict['settings']['stop_type'].lower() == 'quantidade' else 'o valor'}"
                    await event.respond(f"__**Digite {text} do seu StopLoss**__")
                    self.conversation_state[sender_id] = self.state.WAIT_STOP_LOSS
                elif selected == "protection_hand":
                    await self.bot.delete_messages(event.sender_id, [msg_id])
                    protection_hand = "NÃO" if protection_hand != "NÃO" else "SIM"
                    user_dict["settings"]["protection_hand"] = protection_hand
                    more_buttons[6][0].text = f"Proteção no Branco = {protection_hand}"
                    await event.respond("__**Configurações Gerais**__", buttons=more_buttons)
                elif selected == "protection_value":
                    await self.bot.delete_messages(event.sender_id, [msg_id])
                    await event.respond("__**Digite o valor que deseja usar na proteção**__")
                    self.conversation_state[sender_id] = self.state.WAIT_PROTECTION_VALUE
                elif selected == "martingale":
                    await self.bot.delete_messages(event.sender_id, [msg_id])
                    await event.respond("__**Digite a quantidade de martingale quer que o bot faça**__")
                    self.conversation_state[sender_id] = self.state.WAIT_MARTINGALE
                elif selected == "white_martingale":
                    await self.bot.delete_messages(event.sender_id, [msg_id])
                    white_martingale = "NÃO" if white_martingale != "NÃO" else "SIM"
                    user_dict["settings"]["white_martingale"] = white_martingale
                    more_buttons[9][0].text = f"Martingale Branco = {white_martingale}"
                    await event.respond("__**Configurações Gerais**__", buttons=more_buttons)
                elif selected == "martingale_multiplier":
                    await self.bot.delete_messages(event.sender_id, [msg_id])
                    await event.respond("__**Digite o fator de multiplicação "
                                        "de martingale que quer que o bot faça**__")
                    self.conversation_state[sender_id] = self.state.WAIT_MARTINGALE_MULTIPLIER
                elif selected == "white_multiplier":
                    await self.bot.delete_messages(event.sender_id, [msg_id])
                    await event.respond("__**Digite o fator de multiplicação "
                                        "de martingale do branco que quer que o bot faça**__")
                    self.conversation_state[sender_id] = self.state.WAIT_WHITE_MULTIPLIER
                
                elif selected == "white_gerenciamento_tk":
                    await self.bot.delete_messages(event.sender_id, [msg_id])
                    gerenciamento_tk = "NÃO" if gerenciamento_tk != "NÃO" else "SIM"
                    user_dict["settings"]["white_gerenciamento_tk"] = gerenciamento_tk
                    more_buttons[12][0].text = f"Gerenciamento = {gerenciamento_tk}"
                    await event.respond("__**Configurações Gerais**__", buttons=more_buttons)
                elif selected == "gerenciamento_tk_qtd":
                        await self.bot.delete_messages(event.sender_id, [msg_id])
                        await event.respond("__**Digite a sequência de entradas que deseja no gerenciamento Milion**__")
                        self.conversation_state[sender_id] = self.state.WAIT_GERENCIAMENTO_SEQUENCIA
                elif selected == "gerenciamento_tk_qtd_win":
                        await self.bot.delete_messages(event.sender_id, [msg_id])
                        await event.respond("__**Digite a quantidade de WIN para reinciar**__")
                        self.conversation_state[sender_id] = self.state.WAIT_GERENCIAMENTO_QTD_WIN
                elif selected == "gerenciamento_tk_qtd_loss":
                        await self.bot.delete_messages(event.sender_id, [msg_id])
                        await event.respond("__**Digite a quantidade de LOSS para reinciar**__")
                        self.conversation_state[sender_id] = self.state.WAIT_GERENCIAMENTO_QTD_LOSS

            controller.create(user_dict)

    def start_service(self):
        self.bot.start(bot_token=bot_token)
        print("Starting telegram bot!!!")
        self.bot.run_until_disconnected()


if __name__ == "__main__":
    bot = TelegramBot()
    bot.start_service()
