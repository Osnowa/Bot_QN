from conf.config import Config_DB
import asyncpg

conf_db = Config_DB()
_pool: asyncpg.Pool | None = None

async def init_pool():
    '''Создаем пуул соединений при старте приложения'''
    global _pool

    _pool = await asyncpg.create_pool(
        host = conf_db.DB_HOST,
        port = conf_db.DB_PORT,
        database = conf_db.DB_NAME,
        user = conf_db.DB_USER,
        password = conf_db.DB_PASSWORD,
        min_size = 2,
        max_size = 10
    )

async def close_pool():
    '''Закрываем пул соединений при завершении приложения'''
    global _pool

    if _pool:
        await _pool.close()

def get_pool() -> asyncpg.Pool:
    '''Возвращаем пул соединений для использования в других частях приложения'''
    if _pool is None:
        raise RuntimeError("Пул соединений не инициализирован. Вызовите init_pool() перед использованием.")
    return _pool


