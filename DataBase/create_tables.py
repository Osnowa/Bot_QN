import logging
from DataBase.db import get_pool

logger = logging.getLogger(__name__)

async def create_tables():
    pool = get_pool()
    
    query = '''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT UNIQUE NOT NULL,
        username VARCHAR(255),
        games_played INT DEFAULT 0,
        games_won INT DEFAULT 0,
        games_lost INT DEFAULT 0
    );
    '''

    async with pool.acquire() as connection:
        await connection.execute(query)
    logger.info("Таблица users успешно создана или уже существует.")

