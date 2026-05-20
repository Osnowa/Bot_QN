from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.context import FSMContext
from infastructure.redis_inf import redis
from conf.config import Conf_Game
import logging
from DataBase.queries import create_user, update_user_stats, get_user_stats

router = Router()
config_game = Conf_Game()
logger = logging.getLogger(__name__)


class FSMGame(StatesGroup):
    in_game = State()


@router.message(Command("start"), StateFilter(default_state))
async def start_message(message: Message):
    t_id = message.from_user.id # получаем Telegram ID пользователя
    username = message.from_user.username or "Unknown" # получаем имя пользователя или устанавливаем "Unknown", если имя отсутствует

    user = await get_user_stats(t_id)
    if user is None:
        await create_user(t_id, username)
        logger.info(f"Создан новый пользователь с Telegram ID: {t_id} и username: {username}.")
    else:
        logger.info(f"Пользователь с Telegram ID: {t_id} уже существует в базе данных.")

    await message.answer(f"<b>Привет, {username}!</b> Я бот для игры в угадай число 🎰. \n" 
                        "Напиши /play, чтобы начать игру."
                        )


@router.message(Command("cancel"), ~StateFilter(default_state))
async def cancel_message(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы вышли из игры. Напишите /play, чтобы начать заново.")


@router.message(Command("cancel"), StateFilter(default_state))
async def cancel_message_not_in_game(message: Message):
    await message.answer("Вы не в игре. Напишите /play, чтобы начать игру.")


@router.message(Command("play"), StateFilter(default_state))
async def play_message(message: Message, state: FSMContext):
    '''Начинаем игру, устанавливаем состояние FSM и сохраняем данные в Redis'''
    t_id = message.from_user.id

    await state.set_state(FSMGame.in_game)
    logger.info(f"Пользователь {t_id} вошел в игру.")

    await redis.hset(f"user:{t_id}", mapping={
        "attempts": config_game.game_attempt,
        "number": config_game.attemp_number()
    }
    )
    await redis.expire(f"user:{t_id}", 3600) # устанавливаем время жизни данных в Redis (например, 1 час)

    await message.answer(f"Вы начали игру ! 🎮\n"
                         f"Угадайте число от 1 до 100. У вас есть {config_game.game_attempt} попыток. \n"
                         f"Напишите /cancel, чтобы выйти из игры.")



@router.message(StateFilter(FSMGame.in_game), lambda message: message.text and message.text.isdigit())
async def game_message(message: Message, state: FSMContext):
    '''Обрабатываем попытку пользователя, сравниваем с загаданным числом и 
    обновляем количество оставшихся попыток в Redis, сохраняем статистику в БД'''
    t_id = message.from_user.id
    user_data = await redis.hgetall(f"user:{t_id}") 
    # проверяем, есть ли данные о пользователе в Redis (на случай, если время жизни данных истекло)
    if not user_data:
        await message.answer(f"Извините, Ваше время игры вышло," 
                             f"нажмите /play для начала новой игры")
        await state.clear()
        await redis.delete(f"user:{t_id}")
        return
    
    attempts = int(user_data['attempts'])
    secret_number = int(user_data['number'])
    quess = int(message.text)
    logger.info(f"Пользователь {t_id} сделал попытку: {message.text}. Осталось попыток: {attempts}. Загаданное число: {secret_number}.")
    
    if quess == secret_number:
        await message.answer(f"Поздравляем! Вы угадали число! 🎉"
                             f"Напишите /play, чтобы начать новую игру.")
        await state.clear()
        await redis.delete(f"user:{t_id}")
        await update_user_stats(t_id, won=True)
        return

    elif quess > secret_number:
        await message.answer(f"Загаданное число меньше. Попробуйте снова.")
        logger.info(f"Пользователь {t_id} ввел число {message.text}, которое больше загаданного.")
        await redis.hset(f"user:{t_id}", mapping={"attempts": attempts - 1})
        attempts -= 1


    elif quess < secret_number:
        await message.answer(f"Загаданное число больше. Попробуйте снова.")
        logger.info(f"Пользователь {t_id} ввел число {message.text}, которое меньше загаданного.")
        await redis.hset(f"user:{t_id}", mapping={"attempts": attempts - 1})
        attempts -= 1


    if attempts <= 0:
        await message.answer(f"К сожалению, у вас закончились попытки. 😞 \n"
                             f"Загаданное число было: <u>{int(user_data['number'])}</u>.\n"
                             f"Напишите /play, чтобы начать новую игру.")
        await state.clear()
        await redis.delete(f"user:{t_id}")
        await update_user_stats(t_id, won=False)
        return 
    
@router.message(StateFilter(FSMGame.in_game))
async def game_message_not_digit(message: Message):
    await message.answer(f"Пожалуйста, введите число от 1 до 100.")

    
    

