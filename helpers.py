from datetime import datetime
import asyncpg
import csv
from configparser import ConfigParser


POOL = 0
config = ConfigParser()
config.read('config.ini')

async def init_db():
    global POOL
    POOL = await asyncpg.create_pool(
        max_size=20,
        host=config['database']['host'],
        database=config['database']['database'],
        user=config['database']['username'],
        password=config['database']['password'],
        port=config['database']['port_id'])
    conn = await POOL.acquire()
    async with POOL.acquire() as conn:
        async with conn.transaction():
            await conn.execute('DROP TABLE replies')
            await conn.execute('''CREATE TABLE IF NOT EXISTS replies(
                            id serial primary key,
                            status int,
                            chat_id varchar(50),
                            year int,
                            month int,
                            day int
                            )''')

            await conn.execute('''CREATE TABLE IF NOT EXISTS admins(
                            id serial primary key,
                            chat_id varchar(64)
                            )''')

            await conn.execute('''CREATE TABLE IF NOT EXISTS feedback(
                            id serial primary key,
                            chat_id varchar(64),
                            feedback_text varchar(1024),
                            date varchar(128)
                            )''')
            
            await conn.execute('''CREATE TABLE IF NOT EXISTS users(
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
            
            await conn.execute('''ALTER TABLE users ADD ready varchar(8) default -2''')
            await conn.execute('''ALTER TABLE users ADD first_okay varchar(16) default -2''')
            await conn.execute('''ALTER TABLE users ADD second_okay varchar(16) default -2''')
        




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


# works
async def add_reply(values):
    async with POOL.acquire() as conn:
        async with conn.transaction():
            await conn.executemany('INSERT INTO replies (status, chat_id, year, month, day) VALUES ($1, $2, $3, $4, $5)', [values, ])
    
# works
async def get_all_replies():
    async with POOL.acquire() as conn:
        async with conn.transaction():
            replies = await conn.fetch('SELECT * FROM replies')
            for i in range(len(replies)):
                replies[i] = Reply(tuple(replies[i]))
    return replies

# works
async def remove_reply(id):
    async with POOL.acquire() as conn:
        async with conn.transaction():
            await conn.execute('DELETE FROM replies WHERE id = $1', id)

# works
async def add_user(user: User):
    async with POOL.acquire() as conn:
        async with conn.transaction():
            await conn.executemany('INSERT INTO users(chat_id, name, last_name, nickname, first_touch, last_touch, status, result_sent) VALUES($1, $2, $3, $4, $5, $6, $7, $8)', [user.tosave(), ])

# -----
async def get_all_users():
    users = []
    async with POOL.acquire() as conn:
        async with conn.transaction():
            users = await conn.fetch('SELECT * FROM users')
    
    result = list(map(tuple, users))
    return result

# works
async def update_user(key, value, chat_id):
    async with POOL.acquire() as conn:
        async with conn.transaction():
            query = f'UPDATE users set {key} = $1 WHERE chat_id = $2 AND id = (SELECT MAX(id) FROM users WHERE chat_id = $3)'
            await conn.execute(query, value, chat_id, chat_id)

# works
async def update_user_final_touch(account, last_touch, status, result_sent, chat_id):
    async with POOL.acquire() as conn:
        async with conn.transaction():
            await conn.execute('UPDATE users set account = $1, last_touch = $2, status = $3, result_sent = $4 WHERE chat_id = $5 AND id = (SELECT MAX(id) FROM users WHERE chat_id = $6)', account, last_touch, status, result_sent, chat_id, chat_id)

# works
async def add_feedback(chat_id, text):
    async with POOL.acquire() as conn:
        async with conn.transaction():
            await conn.executemany('INSERT INTO feedback(chat_id, feedback_text, date) VALUES ($1, $2, $3)', [(chat_id, text, str(datetime.utcnow())), ])

# -----
async def get_all_feedback():
    feedback = []
    async with POOL.acquire() as conn:
        async with conn.transaction():
            feedback = await conn.fetch('SELECT * FROM feedback')
    
    result = list(map(lambda x: tuple(x)[1:], feedback))
    return result


async def get_csv_users():
    users = await get_all_users()
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
    with open("users.csv", 'w') as csv_file:
        writer = csv.writer(csv_file, dialect = 'excel')
        writer.writerows(users)


async def get_csv_feedback():
    feedback = await get_all_feedback()
    feedback.insert(0, (
        'ID чата',
        'Текст ОС',
        'Дата и время ОС'
        ))
    with open("feedback.csv",'w') as csv_file:
        writer = csv.writer(csv_file, dialect = 'excel')
        writer.writerows(feedback)


async def add_admin(chat_id):
    async with POOL.acquire() as conn:
        async with conn.transaction():
            await conn.execute('INSERT INTO admins(chat_id) VALUES ($1)', chat_id)


async def get_admin_by_id(chat_id):
    async with POOL.acquire() as conn:
        async with conn.transaction():
            result = await conn.fetch('SELECT * FROM admins WHERE chat_id = $1', chat_id)

    return result
    