import os
import sys
import time
import asyncio
from threading import Thread
from core.api import BlazeAPI
from controllers import UserController
from utils.messages import gale_message, confirmed_bets, \
    opportunity_alert, awaiting_result, win_alert, loss_alert, \
    stop_win_alert, stop_loss_alert, view_config, view_sequence


__author__ = "Auto Milion"
__version__ = "0.1"

__message__ = f"""
Use com moderação, pois gerenciamento é tudo!
suporte: freitasraf311@gmail.com ou +55 (33) 9850-6085
"""


def calculate_martingale(enter, multiplier):
    return round(float(enter) * float(multiplier), 2)

def gerenciamento_50(enter, multiplier):
    return round(float(enter) * float(multiplier), 2)

def calculate_profit(user_bot):
    return round(float(user_bot["variables"]["balance"]) - float(user_bot["variables"]["first_balance"]), 2)


def strategies_parse(data):
    return [{i["color"]: ["vermelho" if char.lower().startswith("v")
                          else "preto" for char in i["sequence"].split(",")]} for i in data]


class Double(Thread):

    def __init__(self, bot, chat_id):
        super(Double).__init__()
        self.bot = bot
        self.chat_id = chat_id
        self.last_doubles = []
        self.controller = UserController()
        self.blaze = BlazeAPI()
        self.kill = False
        Thread.__init__(self)

    def run(self):
        print("Starting bot...")
        self.last_doubles = self.get_doubles()
        while True:
            if self.kill:
                break
            user_bot = self.get_user()
            if user_bot:
                if self.awaiting_status("waiting"):
                    view_sequence(user_bot, self.last_doubles)
                    if not user_bot["user"]["is_betting"]:
                        if not user_bot["variables"]["count_martingale"] > 0:
                            user_bot["user"]["color_bet"] = self.get_analise(user_bot["strategies"])
                            user_bot["user"]["color_before"] = user_bot["user"]["color_bet"]
                        elif user_bot["variables"]["count_martingale"] <= user_bot["settings"]["martingale"]:
                            user_bot["user"]["color_bet"] = user_bot["user"]["color_before"]
                            gale_message(user_bot)
                            user_bot["user"]["is_betting"] = True
                        if user_bot["user"]["color_bet"]:
                            if not user_bot["variables"]["is_gale"]:
                                opportunity_alert(user_bot)
                                view_config(user_bot)
                                user_bot["user"]["is_betting"] = True
                            if user_bot["variables"]["count_martingale"] <= user_bot["settings"]["martingale"]:
                                self.start_bets(user_bot)
                                confirmed_bets(user_bot)
                                awaiting_result(user_bot)
                                user_bot["user"]["is_betting"] = True
                        if user_bot["user"]["is_active"]:
                            self.controller.create(user_bot)

                if self.awaiting_status("rolling"):
                    double = asyncio.run(self.blaze.get_double())
                    self.last_doubles.append([double["roll"], self.get_color(double["color"])])
                    self.last_doubles = self.last_doubles[1:]
                    if user_bot["user"]["color_bet"]:
                        if user_bot["variables"]["count_martingale"] <= user_bot["settings"]["martingale"]:
                            result_data = self.wait_result(user_bot)
                            user_bot["variables"]["balance"] = result_data["object"]["balance"]
                            if result_data["object"]["win"]:
                                user_bot["variables"]["count_win"] += 1
                                user_bot["variables"]["count_martingale"] = 0
                                user_bot["variables"]["profit"] = calculate_profit(user_bot)
                                user_bot["variables"]["is_gale"] = False
                                user_bot["settings"]["enter_value"] = user_bot["settings"]["first_amount"]
                                user_bot["settings"]["protection_value"] = user_bot["settings"]["first_protection"]
                                win_alert(user_bot)
                            elif not result_data["object"]["win"]:
                                user_bot["variables"]["count_martingale"] += 1
                                user_bot["variables"]["profit"] = calculate_profit(user_bot)
                                user_bot["settings"]["enter_value"] = calculate_martingale(
                                    user_bot["settings"]["enter_value"], user_bot["settings"]["martingale_multiplier"]
                                )
                                user_bot["settings"]["protection_value"] = calculate_martingale(
                                    user_bot["settings"]["protection_value"], user_bot["settings"]["white_multiplier"]
                                )
                                user_bot["variables"]["is_gale"] = True
                        elif user_bot["variables"]["count_martingale"] >= user_bot["settings"]["martingale"]:
                            user_bot["variables"]["count_loss"] += 1
                            user_bot["variables"]["count_martingale"] = 0
                            # user_bot["variables"]["profit"] -= user_bot["settings"]["enter_value"]
                            user_bot["variables"]["profit"] = calculate_profit(user_bot)
                            user_bot["settings"]["enter_value"] = user_bot["settings"]["first_amount"]
                            user_bot["settings"]["protection_value"] = user_bot["settings"]["first_protection"]
                            user_bot["variables"]["is_gale"] = False
                            loss_alert(user_bot)
                        if user_bot["settings"]["stop_type"] == "VALOR" \
                                and user_bot["variables"]["profit"] >= float(user_bot["settings"]["stop_gain"]) \
                                or user_bot["settings"]["stop_type"] == "QUANTIDADE" \
                                and user_bot["variables"]["count_win"] >= int(user_bot["settings"]["stop_gain"]):
                            user_bot["user"]["is_active"] = False
                            user_bot["user"]["is_betting"] = False
                            user_bot["user"]["color_bet"] = None
                            user_bot["user"]["color_before"] = None
                            user_bot["variables"]["is_gale"] = False
                            user_bot["settings"]["enter_value"] = user_bot["settings"]["first_amount"]
                            user_bot["settings"]["protection_value"] = user_bot["settings"]["first_protection"]
                            user_bot["variables"]["count_martingale"] = 0
                            user_bot["variables"]["count_win"] = 0
                            user_bot["variables"]["count_loss"] = 0
                            user_bot["variables"]["profit"] = 0
                            stop_win_alert(user_bot)
                            self.controller.disable(user_bot)
                            self.quit()
                        if user_bot["settings"]["stop_type"] == "VALOR" \
                                and user_bot["variables"]["profit"] <= float('-' + str(user_bot["settings"]["stop_loss"])) \
                                or user_bot["settings"]["stop_type"] == "QUANTIDADE" \
                                and user_bot["variables"]["count_loss"] >= int(user_bot["settings"]["stop_loss"]):
                            user_bot["user"]["is_active"] = False
                            user_bot["user"]["is_betting"] = False
                            user_bot["user"]["color_bet"] = None
                            user_bot["user"]["color_before"] = None
                            user_bot["variables"]["is_gale"] = False
                            user_bot["settings"]["enter_value"] = user_bot["settings"]["first_amount"]
                            user_bot["settings"]["protection_value"] = user_bot["settings"]["first_protection"]
                            user_bot["variables"]["count_martingale"] = 0
                            user_bot["variables"]["count_win"] = 0
                            user_bot["variables"]["count_loss"] = 0
                            user_bot["variables"]["profit"] = 0
                            stop_loss_alert(user_bot)
                            self.controller.disable(user_bot)
                            self.quit()
                        if user_bot["user"]["is_active"]:
                            user_bot["user"]["is_betting"] = False
                            self.controller.create(user_bot)
            else:
                print("Nenhum usuário ativo!!!")

            time.sleep(0.5)

    def get_analise(self, strategies=None):
        color = None
        sequence = [color[1] for color in self.last_doubles] if len(self.last_doubles) > 0 else None

        user_strategies = [
            {"vermelho": ["preto", "preto"]},
            {"preto": ["vermelho", "vermelho"]},
            {"vermelho": ["preto", "preto", "preto"]},
            {"preto": ["vermelho", "vermelho", "vermelho"]},
            {"vermelho": ["preto", "preto", "preto", "preto"]},
            {"preto": ["vermelho", "vermelho", "vermelho", "vermelho"]},
            {"vermelho": ["vermelho", "vermelho", "preto", "preto"]},
            {"preto": ["preto", "preto", "vermelho", "vermelho"]},
            {"vermelho": ["vermelho", "preto", "vermelho", "preto"]},
            {"preto": ["preto", "vermelho", "preto", "vermelho"]},
        ]

        if strategies:
            user_strategies = strategies_parse(strategies)

        if not color and sequence:
            for dicts in user_strategies:
                if dicts.get("vermelho") and dicts.get("vermelho") == sequence[-len(dicts.get("vermelho")):]:
                    color = "vermelho"
                elif dicts.get("preto") and dicts.get("preto") == sequence[-len(dicts.get("preto")):]:
                    color = "preto"
                elif dicts.get("branco") and dicts.get("branco") == sequence[-len(dicts.get("branco")):]:
                    color = "branco"

        return color

    def get_user(self):
        result_user = self.controller.check_user_exists(self.chat_id)
        return result_user if result_user["user"]["is_active"] else None

    @staticmethod
    def get_color(number):
        colors = {
            0: "branco",
            1: "vermelho",
            2: "preto"
        }
        return colors.get(number, None)

    def get_doubles(self):
        doubles = self.blaze.get_last_doubles()
        if doubles:
            return [[item["value"], item["color"]] for item in doubles["items"]][::-1]
        return []

    def awaiting_status(self, status_double):
        while True:
            if self.blaze.get_status() == status_double:
                return True
            time.sleep(0.1)

    def get_result(self, color, result):
        win = self.blaze.get_ws_result()
        roll_win = win["roll"]
        result["roll"] = roll_win
        color_win = self.get_color(win["color"])
        result["color"] = color_win

        if color_win == color:
            result["win"] = True
        else:
            result["win"] = False

        return result

    def wait_result(self, user_bot):
        result_protection = {}
        result_fixed = {}
        result_bet = {
            "object": {}
        }
        user_bot["variables"]["balance"] -= user_bot["settings"]["enter_value"]
        self.get_result(user_bot["user"]["color_bet"], result_fixed)
        if user_bot["settings"]["protection_hand"] == "SIM":
            user_bot["variables"]["balance"] -= user_bot["settings"]["protection_value"]
            self.get_result("branco", result_protection)
            if result_fixed["win"] or result_protection["win"]:
                result_bet["object"]["win"] = True
                if result_fixed["win"]:
                    user_bot["variables"]["balance"] += \
                        user_bot["settings"]["enter_value"] * user_bot["settings"]["martingale_multiplier"]
                elif result_protection["win"]:
                    user_bot["variables"]["balance"] += user_bot["settings"]["protection_value"] * 14
            else:
                result_bet["object"]["win"] = False
        else:
            if result_fixed["win"]:
                result_bet["object"]["win"] = True
                user_bot["variables"]["balance"] += \
                    user_bot["settings"]["enter_value"] * user_bot["settings"]["martingale_multiplier"]
            else:
                result_bet["object"]["win"] = False

        result_bet["object"]["balance"] = round(float(user_bot["variables"]["balance"]), 2)
        result_bet["object"]["profit"] = calculate_profit(user_bot)

        return result_bet

    def start_bets(self, args):
        color = args["user"]["color_bet"]
        amount = args["settings"]["enter_value"]

        self.blaze.token = args["user"]["token"]
        self.blaze.wallet_id = args["user"]["wallet"]

        if args["settings"]["account_type"] == "REAL":
            self.blaze.double_bets(color, amount)
            if args["settings"]["protection_hand"] == "SIM":
                self.blaze.double_bets("branco", args["settings"]["protection_value"])

    def quit(self):
        self.kill = True
        print("Stoping bot...")
        del self

    def __del__(self):
        del self.blaze
