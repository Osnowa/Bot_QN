from DataBase.db import get_pool

async def create_user(telegram_id: int, username: str):
    pool = get_pool()
    
    query = '''
    INSERT INTO users (telegram_id, username)
    VALUES ($1, $2),
    ON CONFLICT (telegram_id) DO NOTHING;
    ;
    '''

    async with pool.acquire() as connection:
        await connection.execute(query, telegram_id, username)


async def update_user_stats(telegram_id: int, won: bool):
    pool = get_pool()

    if won:
        query = '''
        UPDATE users
        SET games_played = games_played + 1, games_won = games_won + 1
        WHERE telegram_id = $1;
        '''
    else:
        query = '''
        UPDATE users
        SET games_played = games_played + 1, games_lost = games_lost + 1
        WHERE telegram_id = $1;
        '''

    async with pool.acquire() as connection:
        await connection.execute(query, telegram_id)

async def get_user_stats(telegram_id: int):
    pool = get_pool()

    query = '''
    SELECT games_played, games_won, games_lost
    FROM users
    WHERE telegram_id = $1;
    '''

    async with pool.acquire() as connection:
        row = await connection.fetchrow(query, telegram_id)
        return dict(row) if row else None
    
