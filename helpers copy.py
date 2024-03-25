import aiosqlite
from sqlite3 import Error
from datetime import datetime
from psycopg2 import pool
from psycopg2.sql import SQL, Identifier
import asyncpg
import csv

hostname = 'localhost'
database = 'algo_hr_bot'
username = 'postgres'
pwd = '1111'
port_id = 5432
POOL = 0

async def init_db():
    global POOL
    POOL = await asyncpg.create_pool(min_size=10, max_size=30, host=hostname, dbname=database, user=username, password=pwd, port=port_id)
    conn = await POOL.acquire()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute('''CREATE TABLE IF NOT EXISTS replies(
                              id serial primary key,
                              status int,
                              chat_id varchar(50),
                              year int,
                              month int,
                              day int
                              )''')

cur.execute('''CREATE TABLE IF NOT EXISTS admins(
            id serial primary key,
            chat_id varchar(64)
)''')

cur.execute('''CREATE TABLE IF NOT EXISTS feedback(
            id serial primary key,
            chat_id varchar(64),
            feedback_text varchar(1024),
            date varchar(128)
)''')

cur.execute('''CREATE TABLE IF NOT EXISTS users(
            id serial primary key,
            chat_id varchar(64),
            name varchar(64),
            last_name varchar(64),
            nickname varchar(64),
            first_touch varchar(64),
            last_touch varchar(64),
            status int,
            result_sent int,
            experience varchar(32) default 0,
            crm varchar(8) default 0,
            citizenship varchar(8) default 0,
            location varchar(8) default 0,
            account varchar(8) default 0
)''')

conn.commit()
cur.close()
cpool.putconn(conn)


class Reply:
    def __init__(self, data):
        self.id = data[0]
        self.status = data[1]
        self.chat_id = data[2]
        self.year = data[3]
        self.month = data[4]
        self.day = data[5]

    def is_past(self):
        now = datetime.utcnow()
        reply_date = datetime(self.year, self.month, self.day, 9, 0, 0)
        return reply_date < now

    def __str__(self):
        return f'{self.id}, {self.status}, {self.chat_id}, {self.year}, {self.month}, {self.day}'
    

class User:
    def __init__(self, data):
        self.id = data[0]
        self.chat_id = data[1]
        self.name = data[2]
        self.last_name = data[3]
        self.nickname = data[4]
        self.first_touch = data[5]
        self.last_touch = data[6]
        self.status = data[7]
        self.result_sent = data[8]
        self.experience = data[9]
        self.crm = data[10]
        self.citizenship = data[11]
        self.location = data[12]
        self.account = data[13]


    def __str__(self):
        return f'{self.id}, {self.chat_id}, {self.name}, {self.last_name}, {self.nickname}, {self.first_touch}, {self.last_touch}, {self.status}, {self.result_sent}'
    
    def tosave(self):
        return (self.chat_id, self.name, self.last_name, self.nickname, self.first_touch, self.last_touch, self.status, self.result_sent)


def add_reply(values):
    conn = cpool.getconn()
    cur = conn.cursor()
    cur.execute('INSERT INTO replies(status, chat_id, year, month, day) VALUES (%s, %s, %s, %s, %s)', values)
    conn.commit()
    cur.close()
    cpool.putconn(conn)


def get_all_replies():
    conn = cpool.getconn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM replies')
    replies = cur.fetchall()
    for i in range(len(replies)):
        replies[i] = Reply(replies[i])
    cur.close()
    cpool.putconn(conn)
    return replies


def remove_reply(id):
    conn = cpool.getconn()
    cur = conn.cursor()
    cur.execute('DELETE FROM replies WHERE id = %s', (id, ))
    conn.commit()
    cur.close()
    cpool.putconn(conn)


def add_user(user):
    conn = cpool.getconn()
    cur = conn.cursor()
    cur.execute('INSERT INTO users(chat_id, name, last_name, nickname, first_touch, last_touch, status, result_sent) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)', user.tosave())
    conn.commit()
    cur.close()
    cpool.putconn(conn)


def get_all_users():
    conn = cpool.getconn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    conn.commit()
    cur.close()
    cpool.putconn(conn)
    return users

def get_user_by_chat_id(chat_id):
    conn = cpool.getconn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE chat_id = %s', (chat_id, ))
    user = User(cur.fetchone())
    conn.commit()
    cur.close()
    cpool.putconn(conn)
    return user

def update_user(key, value, chat_id):
    conn = cpool.getconn()
    cur = conn.cursor()
    cur.execute(SQL('UPDATE users set {} = %s WHERE chat_id = %s AND id = (SELECT MAX(id) FROM users WHERE chat_id = %s)').format(Identifier(key)), (value, chat_id, chat_id))
    conn.commit()
    cur.close()
    cpool.putconn(conn)


def update_user_final_touch(account, last_touch, status, result_sent, chat_id):
    conn = cpool.getconn()
    cur = conn.cursor()
    cur.execute('UPDATE users set account = %s, last_touch = %s, status = %s, result_sent = %s WHERE chat_id = %s AND id = (SELECT MAX(id) FROM users WHERE chat_id = %s)', (account, last_touch, status, result_sent, chat_id, chat_id))
    conn.commit()
    cur.close()
    cpool.putconn(conn)


def add_feedback(chat_id, text):
    conn = cpool.getconn()
    cur = conn.cursor()
    cur.execute('INSERT INTO feedback(chat_id, feedback_text, date) VALUES (%s, %s, %s)', (chat_id, text, str(datetime.utcnow())))
    conn.commit()
    cur.close()
    cpool.putconn(conn)


def get_all_feedback():
    conn = cpool.getconn()
    cur = conn.cursor()
    cur.execute('SELECT (chat_id, feedback_text, date) FROM feedback')
    feedback = cur.fetchall()
    cur.close()
    cpool.putconn(conn)
    return feedback


def get_csv_users():
    users = get_all_users()
    users.insert(0, (
        'ID цепочки',
        'ID чата',
        'Имя',
        'Фамилия',
        'Ник',
        'Когда нажал /start',
        'Когда заполнил анкету до конца',
        'Получил (получит) согласие или отказ',
        'Было отправлено согласие или отказ?',
        'Опыт работы',
        'Опыт в crm',
        'Есть гражданство РФ?',
        'Находится в РФ?',
        'Есть аккаунт в российском банке?'
        ))
    with open("users.csv",'w') as csv_file:
        writer = csv.writer(csv_file, dialect = 'excel')
        writer.writerows(users)

def get_csv_feedback():
    feedback = get_all_feedback()
    feedback.insert(0, (
        'ID чата',
        'Текст ОС',
        'Дата и время ОС'
        ))
    with open("feedback.csv",'w') as csv_file:
        writer = csv.writer(csv_file, dialect = 'excel')
        writer.writerows(feedback)


def add_admin(chat_id):
    conn = cpool.getconn()
    cur = conn.cursor()
    cur.execute('INSERT INTO admins(chat_id) VALUES (%s)', (chat_id, ))
    conn.commit()
    cur.close()
    cpool.putconn(conn)


def get_admin_by_id(chat_id):
    conn = cpool.getconn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM admins WHERE chat_id = %s', (chat_id, ))
    result = cur.fetchone()
    cur.close()
    cpool.putconn(conn)
    return result


#     async def RemoveReply(self, id):
#         async with self.pool.acquire() as conn:
#             await conn.execute('DELETE FROM replies WHERE id = :id', {'id': id})


#     async def UpdateStats(db, qn):
#         qn_to_id = {
#             1: 'started',
#             2: 'q1',
#             3: 'q2',
#             4: 'q3',
#             5: 'q4',
#             6: 'q5',
#             7: 'q6',
#             8: 'q7',
#             9: 'q8',
#             10: 'q9',
#             11: 'left_feedback',
#         }
#         cur = await db.cursor()
#         await cur.execute('SELECT * FROM STATS')
#         stats = await cur.fetchone()
#         stats = list(stats)
#         stats[qn] += 1
#         await cur.execute(f'UPDATE stats SET {qn_to_id[qn]} = {stats[qn]} WHERE id = {stats[0]}')
#         await db.commit()
#         print(stats)


#     async def AddFeddback(db, feedback_text):
#         cur = await db.cursor()
#         now = datetime.today()
#         await cur.execute('INSERT INTO feedback(feedback_text, date) VALUES (?, ?)', [feedback_text, f'{now.year}{now.month}{now.day}'])
#         await db.commit()
#         await cur.execute('SELECT * FROM feedback')
#         print(await cur.fetchall())

    
#     async def GetStats(db):
#         cur = await db.cursor()
#         await cur.execute('SELECT * FROM stats')
#         return await cur.fetchone()