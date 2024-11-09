import random

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

class Keyboard:

    @staticmethod
    def create_keyboard(answers: list, question_number: int, with_options: int):
        builder = ReplyKeyboardBuilder()
        if with_options == 1:
            for i in Keyboard.shuffle_keyboard(answers, question_number):
                builder.add(types.KeyboardButton(text=str(i)))
            builder.adjust(2)

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
