import asyncio
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove
from utils import shuffle_dict
from database import Database
from datetime import datetime as dt
from keyboard import Keyboard

load_dotenv()
API_TOKEN = os.getenv("bot_api")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


class Continents(StatesGroup):
    count = State()


@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.set_state(Continents.count)
    await bot.send_message(message.from_user.id,
                           text='Можно выбрать один материк или перечислить несколько через пробел:\n'
                                '1 - Европа\n'
                                '2 - Азия\n'
                                '3 - Африка\n'
                                '4 - Северная Америка\n'
                                '5 - Южная Америка\n'
                                '6 - Австралия\n')


@dp.message(Continents.count)
async def preparation(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    # Записываем словари ответов и вопросов
    questions_list, answers_list = shuffle_dict(await state.get_data())

    # Записываем в БД (создаем нового юзера, если нет. Создаем под него вопросы и ответы, если нет. Иначе обновляем)
    with Database() as db:
        db.insert('users', [message.from_user.id, message.from_user.username, 1])
        db.insert('questions', [message.from_user.id,
                                ', '.join(questions_list),
                                ', '.join(answers_list),
                                dt.now().replace(microsecond=0),
                                len(questions_list),
                                0,
                                0])
        # Отправляем первый вопрос. Завершаем стейт
        kb = Keyboard.create_keyboard(db.select_answers(message.from_user.id, False),
                                      db.get_question_number(message.from_user.id))
        await bot.send_message(message.from_user.id, db.select_question(message.from_user.id),
                               reply_markup=kb.as_markup(resize_keyboard=True))
    await state.clear()


@dp.message()
async def quiz(message: types.Message):
    try:
        with Database() as db:
            # Проверяем, что пользователь играет
            if db.select_in_game(message.from_user.id) == 1:

                # Если ответ верный пишем следующий вопрос и обновляем счетчик
                if message.text == db.select_answers(message.from_user.id):
                    db.update_question_number(message.from_user.id, correct=True)
                    kb = Keyboard.create_keyboard(db.select_answers(message.from_user.id, False),
                                                  db.get_question_number(message.from_user.id))
                    await bot.send_message(message.from_user.id, db.select_question(message.from_user.id),
                                           reply_markup=kb.as_markup(resize_keyboard=True))

                # Если пользователь написал 1 выводим верный ответ, обновляем счетчик и пишем следующий вопрос
                if message.text == 'Подсказка':
                    await bot.send_message(message.from_user.id, db.select_answers(message.from_user.id))
                    db.update_question_number(message.from_user.id)
                    kb = Keyboard.create_keyboard(db.select_answers(message.from_user.id, False),
                                                  db.get_question_number(message.from_user.id))
                    await bot.send_message(message.from_user.id, db.select_question(message.from_user.id),
                                           reply_markup=kb.as_markup(resize_keyboard=True))

                # Если пользователь нажал "Завершить"
                if message.text == 'Завершить':
                    await the_end(message)

    except IndexError:
        with Database() as db:
            db.update_question_number(message.from_user.id, correct=True)
        await the_end(message)


async def the_end(message):
    with Database() as db:
        if db.select_in_game(message.from_user.id) == 1:
            result = db.the_end(message.from_user.id)
            start_time = dt.now().replace(microsecond=0) - dt.strptime(result[0], "%Y-%m-%d %H:%M:%S")
            await bot.send_message(message.from_user.id, f'Завершено!\nВремя прохождения: {start_time}\n'
                                                         f'Количество верных ответов: {result[1]} из {result[2]}',
                                   reply_markup=ReplyKeyboardRemove())


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
