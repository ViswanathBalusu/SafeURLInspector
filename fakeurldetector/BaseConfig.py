import os

from dotenv import load_dotenv

load_dotenv(".env")


class Config(object):
    OPEN_PAGE_RANK_API_KEY = os.environ.get("OPEN_PAGE_RANK_API_KEY", -1)
    DB_URL = os.environ.get("DB_URL", "sqlite:///./users.sqlite")
    API_KEY = os.environ.get("API_KEY", "test")
