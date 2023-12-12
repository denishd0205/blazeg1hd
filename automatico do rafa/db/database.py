import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

database_name = "autobets"

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://postgres:123@localhost:5432"

# logging.basicConfig(filename='app.log', format='%(asctime)s-%(levelname)s-%(message)s', level=logging.DEBUG)
engine = create_engine(SQLALCHEMY_DATABASE_URL, isolation_level="AUTOCOMMIT")
try:
    engine.execute("CREATE DATABASE " + database_name)
except Exception as db_exc:
    pass
    # logging.exception("Exception creating database: " + str(db_exc))

#engine = create_engine(f"{SQLALCHEMY_DATABASE_URL}/{database_name}")

engine = create_engine(f"sqlite:///db/{database_name}.db")

DBSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
