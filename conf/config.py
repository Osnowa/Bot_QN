from dataclasses import dataclass
from environs import Env
import random

env = Env()
env.read_env()


class Conf_Bot: 
    def __init__(self):
        self.bot_token = env.str("BOT_TOKEN")

class Conf_Game:
    def __init__(self):
        self.game_attempt = 5

    def attemp_number(self):
        return random.randint(1, 100)
    

@dataclass
class Config_DB:
    '''Класс для хранения конфигурации базы данных'''
    DB_HOST: str = env.str("DB_HOST")
    DB_PORT: int = env.int("DB_PORT")
    DB_USER: str = env.str("POSTGRES_USER")
    DB_PASSWORD: str = env.str("POSTGRES_PASSWORD")
    DB_NAME: str = env.str("POSTGRES_DB")

