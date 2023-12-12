import os
import hashlib
from datetime import datetime, date, timedelta
from contextlib import contextmanager
from utils.messages import info_message
from models import Base, User, Settings, Variables, Strategies
from db.database import DBSession, engine

Base.metadata.create_all(bind=engine)


# Base.metadata.bind = engine
# session = DBSession()
# session.begin()


def generate_hashed_token(bot_id):
    return hashlib.md5(bot_id.encode()).hexdigest()


def check_hashed_token(bot_id, hashed_token):
    return hashed_token == generate_hashed_token(bot_id)


def set_expiration_date(user, days):
    date_string = datetime.today().strftime("%m/%d/%Y, %H:%M:%S")
    start_date = datetime.strptime(date_string, "%m/%d/%Y, %H:%M:%S")
    user.created_at = start_date
    expire_date = start_date + timedelta(days=int(days))
    user.expire_in = expire_date
    return user


@contextmanager
def session_scope():
    session = DBSession()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class UserController(object):
    model = User
    settings = Settings
    variables = Variables
    strategies = Strategies

    def create(self, data):
        with session_scope() as session:
            user = session.query(self.model).filter_by(user_bot=data["user"]["user_bot"]).first()
            if not user:
                check_email_in_use = session.query(self.model).filter_by(email=data["user"]["email"]).first()
                if check_email_in_use:
                    return {"result": False, "message": "Email já está em uso..."}
                user = self.model()
                user.user_bot = int(data["user"]["user_bot"])
                user.email = data["user"]["email"]
                user.password = data["user"]["password"]
                user.token = data["user"]["token"]
                user.wallet = data["user"]["wallet"]
                self.save(session, user, refresh=True)
                if data.get("strategies"):
                    self.create_user_strategies(session, data, user.id)
                self.create_user_variables(session, data, user.id)
                self.create_user_settings(session, data, user.id)
            else:
                self.update(session, data, user)
            return {"user": user.as_dict(),
                    "settings": user.settings[0].as_dict(),
                    "variables": user.variables[0].as_dict(),
                    "strategies": [strategy.as_dict() for strategy in user.strategies]
                    }

    def check_user_exists(self, bot_id):
        with session_scope() as session:
            user = session.query(self.model).filter_by(user_bot=bot_id).first()
            if not user:
                return False
            elif user.expire_in and datetime.now() > user.expire_in:
                self.change_token_status(user.id)
            return {"user": user.as_dict(),
                    "settings": user.settings[0].as_dict() if len(user.settings) > 0 else None,
                    "variables": user.variables[0].as_dict() if len(user.variables) > 0 else None,
                    "strategies": [strategy.as_dict() for strategy in user.strategies]
                    if len(user.strategies) > 0 else None
                    }

    def create_user_settings(self, session, data, user_id=None):
        if not user_id:
            user_id = data["settings"].get("owner_id") if data["settings"] else data["user"]["id"]
        user_settings = session.query(self.settings).filter_by(owner_id=user_id).first()
        if not user_settings:
            user_settings = self.settings(**data["settings"], owner_id=user_id)
        else:
            user_settings.account_type = data["settings"]["account_type"]
            user_settings.enter_type = data["settings"]["enter_type"]
            user_settings.enter_value = data["settings"]["enter_value"]
            user_settings.stop_type = data["settings"]["stop_type"]
            user_settings.stop_gain = data["settings"]["stop_gain"]
            user_settings.stop_loss = data["settings"]["stop_loss"]
            user_settings.protection_hand = data["settings"]["protection_hand"]
            user_settings.protection_value = data["settings"]["protection_value"]
            user_settings.martingale = data["settings"]["martingale"]
            user_settings.white_martingale = data["settings"]["white_martingale"]
            user_settings.martingale_multiplier = data["settings"]["martingale_multiplier"]
            user_settings.white_multiplier = data["settings"]["white_multiplier"]
            user_settings.white_gerenciamento_tk = data["settings"]["white_gerenciamento_tk"]
            user_settings.gerenciamento_tk_qtd = data["settings"]["gerenciamento_tk_qtd"]
            user_settings.gerenciamento_tk_qtd_win = data["settings"]["gerenciamento_tk_qtd_win"]
            user_settings.gerenciamento_tk_qtd_loss = data["settings"]["gerenciamento_tk_qtd_loss"]
        self.save(session, user_settings, refresh=True)
        return user_settings

    def create_user_variables(self, session, data, user_id=None):
        if not user_id:
            user_id = data["variables"].get("owner_id") if data["variables"] else data["user"]["id"]
        user_variables = session.query(self.variables).filter_by(owner_id=user_id).first()
        if not user_variables:
            user_variables = self.variables(**data["variables"], owner_id=user_id)
        else:
            user_variables.count_loss = data["variables"]["count_loss"]
            user_variables.count_win = data["variables"]["count_win"]
            user_variables.count_martingale = data["variables"]["count_martingale"]
            user_variables.profit = data["variables"]["profit"]
            user_variables.balance = data["variables"]["balance"]
            user_variables.first_balance = data["variables"]["first_balance"]
            user_variables.created = data["variables"]["created"]
            user_variables.is_gale = data["variables"]["is_gale"]
        self.save(session, user_variables, refresh=True)
        return user_variables

    def create_user_strategies(self, session, data, user_id=None):
        user_strategies = None
        if not user_id:
            user_id = data["user"]["id"]
        if data["strategies"] and len(data["strategies"]) > 0:
            for index, strategy in enumerate(data["strategies"]):
                if not strategy.get("id"):
                    user_strategies = self.strategies(**strategy, owner_id=user_id)
                else:
                    user_strategies = session.query(self.strategies).filter_by(id=strategy["id"],
                                                                               owner_id=user_id).first()
                    if user_strategies:
                        user_strategies.sequence = strategy["sequence"]
                        user_strategies.color = strategy["color"]
                self.save(session, user_strategies, refresh=True)
        return user_strategies

    def read(self):
        with session_scope() as session:
            users = session.query(self.model).all()
            if len(users) > 0:
                return [{"user": user.as_dict(),
                         "settings": user.settings[0].as_dict() if len(user.settings) > 0 else None,
                         "variables": user.variables[0].as_dict() if len(user.variables) > 0 else None,
                         "strategies": [strategy.as_dict() for strategy in user.strategies]
                         if len(user.strategies) > 0 else None} for index, user in enumerate(users)][::-1]

    def update(self, session, data, user):
        user.user_bot = data["user"]["user_bot"]
        user.email = data["user"]["email"]
        user.password = data["user"]["password"]
        user.token = data["user"]["token"]
        user.hashed_token = data["user"]["hashed_token"]
        user.wallet = data["user"]["wallet"]
        user.color_bet = data["user"].get("color_bet")
        user.color_before = data["user"].get("color_before")
        user.is_betting = data["user"].get("is_betting")
        self.save(session, user, refresh=True)
        if data.get("strategies"):
            self.create_user_strategies(session, data)
        self.create_user_variables(session, data)
        self.create_user_settings(session, data)

    def enable(self, data):
        with session_scope() as session:
            user = session.query(self.model).filter_by(user_bot=data["user"]["user_bot"]).first()
            if user:
                user.is_active = data["user"]["is_active"]
                user.process_pid = data["user"]["process_pid"]
                user.settings[0].first_amount = data["settings"]["enter_value"]
                user.settings[0].first_protection = data["settings"]["protection_value"]
                self.create_user_strategies(session, data, user.id)
                self.create_user_settings(session, data, user.id)
                self.create_user_variables(session, data, user.id)
                self.save(session, user, refresh=True)

    def change_bets_status(self, data):
        with session_scope() as session:
            user = session.query(self.model).filter_by(user_bot=data["user"]["user_bot"]).first()
            if user:
                user.is_betting = data["user"]["is_betting"]
                self.save(session, user)

    def change_payment_status(self, data):
        with session_scope() as session:
            user = session.query(self.model).filter_by(email=data["user"]["email"]).first()
            if user:
                user.payment_status = data["user"]["payment_status"]
                self.save(session, user)

    def change_token_status(self, uid, days=None):
        with session_scope() as session:
            user = session.query(self.model).filter_by(id=int(uid)).first()
            if user:
                hashed_token = generate_hashed_token(str(user.user_bot)) if user.payment_status != "PAID" else None
                user.payment_status = "PAID" if user.payment_status != "PAID" else "PENDING"
                if user.is_active:
                    user.is_active = False
                    user.is_betting = False
                if not hashed_token:
                    user.hashed_token = hashed_token
                    data = {"user": user.as_dict(),
                            "settings": user.settings[0].as_dict() if len(user.settings) > 0 else None,
                            "variables": user.variables[0].as_dict() if len(user.variables) > 0 else None,
                            "strategies": [strategy.as_dict() for strategy in user.strategies]
                            if len(user.strategies) > 0 else None
                            }
                    if data:
                        self.disable(data)
                if user.payment_status == "PAID" and days:
                    set_expiration_date(user, days)
                else:
                    user.created_at = None
                    user.expire_in = None
                info_message(user, hashed_token)
                self.save(session, user)

    def disable(self, data):
        with session_scope() as session:
            user = session.query(self.model).filter_by(user_bot=data["user"]["user_bot"]).first()
            if user:
                user.is_active = data["user"]["is_active"]
                user.is_betting = data["user"]["is_betting"]
                user.color_bet = data["user"]["color_bet"]
                user.color_before = data["user"]["color_before"]
                self.create_user_strategies(session, data, user.id)
                self.create_user_settings(session, data, user.id)
                self.create_user_variables(session, data, user.id)
                self.save(session, user)
                # os.system(f'kill -9 {data["user"]["process_pid"]} 2>&1')

    def delete(self, uid):
        with session_scope() as session:
            user = session.query(self.model).filter_by(id=int(uid)).first()
            if user:
                self.save(session, user, delete=True)

    def delete_strategies(self, data, index):
        with session_scope() as session:
            user_strategy = session.query(self.strategies).filter_by(id=data["strategies"][index]["id"],
                                                                     owner_id=data["user"]["id"]
                                                                     ).first()
        if user_strategy:
            self.save(session, user_strategy, delete=True)

    @staticmethod
    def save(session, object_model, delete=False, refresh=False):
        try:
            if delete:
                session.delete(object_model)
            else:
                session.add(object_model)
            session.flush()
            session.commit()
            if refresh:
                session.refresh(object_model)
        except:
            session.rollback()
            raise
