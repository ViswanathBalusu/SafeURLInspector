import sqlalchemy
from fakeurldetector import Config, LOGGER
metadata = sqlalchemy.MetaData()


users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("uuid", sqlalchemy.String(40), primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(30)),
    sqlalchemy.Column("client", sqlalchemy.String(10)),
    sqlalchemy.Column("bot_token", sqlalchemy.String(40)),
    sqlalchemy.Column("telegram_user_id", sqlalchemy.String(20))
)

engine = sqlalchemy.create_engine(Config.DB_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)

LOGGER.info("Created Tables and ORM Engine")
