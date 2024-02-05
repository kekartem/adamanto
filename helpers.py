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
            await conn.execute('''CREATE TABLE IF NOT EXISTS queries(
                               if serial primary key,
                               name varchar(64),
                               contact varchar(64),
                               message varchar(256),
                               option varchar(64)
            )''')
    
    
async def add_query(name, contact, message, option):
    async with POOL.acquire() as conn:
        async with conn.transaction():
            await conn.execute('INSERT INTO queries(name, contact, message, option) VALUES ($1, $2, $3, $4)', name, contact, message, option)


async def get_all_queries():
    result = []
    async with POOL.acquire() as conn:
        async with conn.transaction():
            result = await conn.fetch('SELECT * FROM queries')

    return list(map(tuple, result))