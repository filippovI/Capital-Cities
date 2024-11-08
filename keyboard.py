import random

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types


class Keyboard:

    @staticmethod
    def create_keyboard(answers: list, question_number: int):
        builder = ReplyKeyboardBuilder()
        for i in Keyboard.shuffle_keyboard(answers, question_number):
            builder.add(types.KeyboardButton(text=str(i)))
        builder.adjust(2)
        builder.row(types.KeyboardButton(text="Подсказка"))
        builder.row(types.KeyboardButton(text="Завершить"))

        return builder

    @staticmethod
    def shuffle_keyboard(answers: list, question_number: int):
        correct_answer: str = answers[question_number]
        answers.pop(question_number)
        random.shuffle(answers)
        result: list = answers[:3]
        result.append(correct_answer)
        random.shuffle(result)

        return result
