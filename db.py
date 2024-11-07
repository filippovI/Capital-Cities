import sqlite3 as sq

db = sq.connect("world_capitals.db")
cur = db.cursor()


async def start():
    cur.execute("CREATE TABLE IF NOT EXISTS users ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "tg_id INTEGER NOT NULL UNIQUE,"
                "name TEXT,"
                "in_game INTEGER NOT NULL)")

    cur.execute("CREATE TABLE IF NOT EXISTS questions ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "tg_id INTEGER NOT NULL UNIQUE,"
                "questions TEXT,"
                "answers TEXT,"
                "question_number INTEGER)")
    db.commit()


async def insert(table, values):
    if table == "users":
        cur.execute("INSERT OR REPLACE INTO users (id, tg_id, name, in_game) "
                    f"VALUES ((SELECT id FROM questions WHERE tg_id = {values[0]}), ?,?,?)", values)
        db.commit()

    if table == "questions":
        cur.execute("INSERT OR REPLACE INTO questions (id, tg_id, questions, answers, question_number)"
                    f"VALUES ((SELECT id FROM questions WHERE tg_id = {values[0]}),?,?,?,?)", values)
        db.commit()


async def select_in_game(user_id):
    cur.execute("SELECT in_game "
                "FROM users "
                "WHERE tg_id = ?", (user_id,))
    return cur.fetchone()[0]


async def select_question(user_id):
    cur.execute("SELECT questions "
                "FROM questions "
                "WHERE tg_id = ?", (user_id,))
    return cur.fetchone()[0].split(', ')[cur.execute("SELECT question_number "
                                                     "FROM questions "
                                                     "WHERE tg_id = ?",
                                                     (user_id,)).fetchone()[0]]


async def select_answer(user_id):
    cur.execute("SELECT answers "
                "FROM questions "
                "WHERE tg_id = ?", (user_id,))
    return cur.fetchone()[0].split(', ')[cur.execute("SELECT question_number FROM questions WHERE tg_id = ?",
                                                     (user_id,)).fetchone()[0]]


async def update_question_number(user_id):
    cur.execute("UPDATE questions "
                "SET question_number = (SELECT question_number + 1 FROM questions WHERE tg_id = ?)"
                "WHERE tg_id = ?", (user_id, user_id))
    db.commit()


async def the_end(user_id):
    cur.execute("UPDATE questions "
                "SET questions = NULL, "
                "answers = NULL, "
                "question_number = 0 "
                "WHERE tg_id = ?", (user_id, ))
    cur.execute("UPDATE users "
                "SET in_game = 0 "
                "WHERE tg_id = ?", (user_id, ))
    db.commit()
