from sqlalchemy import Boolean, Column,\
    ForeignKey, Integer, BigInteger, Float,\
    String, inspect, DateTime
from sqlalchemy.orm import relationship
from db.database import Base


def object_as_dict(obj):
    if isinstance(obj, list):
        return [{c.key: getattr(item, c.key)
                 for c in inspect(item).mapper.column_attrs} for item in obj]
    else:
        return {c.key: getattr(obj, c.key)
                for c in inspect(obj).mapper.column_attrs}


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_bot = Column(BigInteger, index=True, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    hashed_token = Column(String(200), index=True, nullable=True)
    token = Column(String(200), index=True, nullable=True)
    process_pid = Column(BigInteger, index=True, nullable=True)
    wallet = Column(String(20), index=True, nullable=True)
    is_active = Column(Boolean, default=False)
    payment_status = Column(String, index=True, default="PENDING")  # PENDING,PAID,OVERDUE,PAYABLE,CANCELLED,IN_PROCESS
    is_betting = Column(Boolean, default=False)
    color_bet = Column(String(20), index=True, nullable=True)
    color_before = Column(String(20), index=True, nullable=True)
    created_at = Column(DateTime, nullable=True)
    expire_in = Column(DateTime, nullable=True)

    settings = relationship("Settings", back_populates="owner", cascade="all, delete")
    variables = relationship("Variables", back_populates="owner", cascade="all, delete")
    strategies = relationship("Strategies", back_populates="owner", cascade="all, delete")

    def as_dict(self):
        return object_as_dict(self)


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    account_type = Column(String, index=True, default="DEMO")
    enter_type = Column(String, index=True, default="VALOR")
    first_amount = Column(Float, index=True, default=2.0)
    first_protection = Column(Float, index=True, default=1.8)
    enter_value = Column(Float, index=True, default=2.0)
    stop_type = Column(String, index=True, default="VALOR")
    stop_gain = Column(String, index=True, default="100")
    stop_loss = Column(String, index=True, default="30")
    protection_hand = Column(String, index=True, default="NÃO")
    protection_value = Column(Float, index=True, default=1.8)
    martingale = Column(Integer, index=True, default=2)
    white_martingale = Column(String, index=True, default="NÃO")
    martingale_multiplier = Column(Float, index=True)
    white_multiplier = Column(Float, index=True)

    white_gerenciamento_tk = Column(String, index=True, default="NÃO")
    gerenciamento_tk_qtd = Column(Integer, index=True, default=3)
    gerenciamento_tk_qtd_win = Column(Integer, index=True, default=4)
    gerenciamento_tk_qtd_loss = Column(Integer, index=True, default=0)

    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="settings")

    def as_dict(self):
        return object_as_dict(self)


class Variables(Base):
    __tablename__ = "variables"

    id = Column(Integer, primary_key=True, index=True)
    count_loss = Column(Integer, index=True, default=0)
    count_win = Column(Integer, index=True, default=0)
    count_martingale = Column(Integer, index=True, default=0)
    profit = Column(Float, index=True, default=0)
    balance = Column(Float, index=True, default=0)
    first_balance = Column(Float, index=True, default=0)
    created = Column(Integer, index=True, default=0)
    is_gale = Column(Boolean, index=True, default=0)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="variables")

    def as_dict(self):
        return object_as_dict(self)


class Strategies(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    sequence = Column(String, index=True)
    color = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="strategies")

    def as_dict(self):
        return object_as_dict(self)
