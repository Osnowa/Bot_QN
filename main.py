import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.enums import ParseMode
from infastructure.redis_inf import redis
from conf.config import Conf_Bot
from keyboards.meny import set_main_menu
from handlers.game import router as game_router
from DataBase.db import init_pool, close_pool
from DataBase.create_tables import create_tables

logger = logging.getLogger(__name__)

config = Conf_Bot()

async def main():
    
    # настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(filename)s - %(levelname)s : %(message)s' 
    )
    logger.info("Starting bot...")

    # подключение к Redis и настройка хранилища для FSM
    storage = RedisStorage(redis=redis)


    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher(storage=storage)

    # регистрируем роутеры
    dp.include_router(game_router)

    # настраиваем кнопки меню
    await set_main_menu(bot)

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await init_pool()
        await create_tables()
        await dp.start_polling(bot)
    finally:
        await close_pool()

if __name__ == "__main__":
    asyncio.run(main())