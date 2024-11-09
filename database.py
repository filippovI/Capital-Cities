import sqlite3 as sq


class Database:
    def __init__(self):
        self.con = sq.connect("world_capitals.db")
        self.__start()

    def __enter__(self):
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        if isinstance(exc_value, Exception):
            self.con.rollback()
        else:
            self.con.commit()
        self.con.close()
        # print('Сессия закрыта')

    def __start(self):
        self.con.execute("""CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                tg_id INTEGER NOT NULL UNIQUE,
                                name TEXT,
                                in_game INTEGER NOT NULL)""")

        self.con.execute("""CREATE TABLE IF NOT EXISTS questions (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                tg_id INTEGER NOT NULL UNIQUE,
                                questions TEXT,
                                answers TEXT,
                                start_time,
                                questions_count INTEGER,
                                question_number INTEGER,
                                correct_answers INTEGER)""")

        self.con.execute("""CREATE TABLE IF NOT EXISTS properties (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        tg_id INTEGER NOT NULL UNIQUE,
                                        name TEXT,
                                        with_options INTEGER DEFAULT 0 NOT NULL)""")

    # Получить номер вопроса
    def get_question_number(self, user_id):
        result = self.con.execute("""SELECT question_number
                                     FROM questions
                                     WHERE tg_id = ?""", (user_id,))

        return result.fetchone()[0]

    # Функция для инсерта в таблицы
    def insert(self, table, values):
        if table == "users":
            self.con.execute(f"""INSERT OR REPLACE INTO users (id, tg_id, name, in_game)
                                 VALUES ((SELECT id FROM questions WHERE tg_id = {values[0]}),?,?,?)""", values)

        if table == "questions":
            self.con.execute(f"""INSERT OR REPLACE INTO questions 
                                (id, tg_id, questions, answers, start_time, questions_count, question_number, correct_answers)
                                 VALUES ((SELECT id FROM questions WHERE tg_id = {values[0]}),?,?,?,?,?,?,?)""", values)
        if table == "properties":
            self.con.execute(f"""INSERT OR IGNORE INTO properties 
                                (tg_id, name, with_options)
                                VALUES (?,?,?)""",values)

    # Получить значение из столбца in_game (играет или нет)
    def select_in_game(self, user_id):
        result = self.con.execute("""SELECT in_game
                                     FROM users
                                     WHERE tg_id = ?""", (user_id,))

        return result.fetchone()[0]

    # Получить значение из столбца with_options (с вариантами ответов или без)
    def select_with_options(self, user_id):
        result = self.con.execute("""SELECT with_options
                                     FROM properties
                                     WHERE tg_id = ?""", (user_id,))

        return result.fetchone()[0]

    def update_with_options(self, user_id, count):
        self.con.execute("""UPDATE properties
                                SET with_options = ?
                                WHERE tg_id = ?""", (count, user_id,))

    # Получить текущий вопрос
    def select_question(self, user_id):
        result = self.con.execute("""SELECT questions
                                     FROM questions
                                     WHERE tg_id = ?""", (user_id,))

        return result.fetchone()[0].split(', ')[self.get_question_number(user_id)]

    # Получить текущий ответ
    def select_answers(self, user_id, one=True):
        result = self.con.execute("""SELECT answers
                                         FROM questions
                                         WHERE tg_id = ?""", (user_id,))

        return result.fetchone()[0].split(', ')[self.get_question_number(user_id)] \
            if one else result.fetchone()[0].split(', ')

    # Обновить номер вопроса
    def update_question_number(self, user_id, correct=False):
        if correct:
            self.con.execute("""UPDATE questions
                                SET question_number = (SELECT question_number + 1 FROM questions WHERE tg_id = ?),
                                correct_answers = (SELECT correct_answers + 1 FROM questions WHERE tg_id = ?)
                                WHERE tg_id = ?""", [user_id] * 3)
        else:
            self.con.execute("""UPDATE questions
                                SET question_number = (SELECT question_number + 1 FROM questions WHERE tg_id = ?)
                                WHERE tg_id = ?""", [user_id] * 2)

    # Функция окончания игры
    def the_end(self, user_id):
        result = self.con.execute("""SELECT 
                                     start_time, 
                                     correct_answers,
                                     questions_count
                                     FROM questions
                                     WHERE tg_id = ?""", (user_id,))

        self.con.execute("""UPDATE users
                            SET in_game = 0
                            WHERE tg_id = ?""", (user_id,))

        return result.fetchone()
