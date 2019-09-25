import asyncio

from config import config
from db.conn import init_db
import lifecycle


async def init():
    if config['db_user'] == 'postgres':
        await init_db()
    await lifecycle.setup(sync_db=True)
    await lifecycle.teardown()

loop = asyncio.get_event_loop()
loop.run_until_complete(init())
