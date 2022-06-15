import logging
import asyncio

from utils.logger import logConfig
from utils.asyncUtils import createTask, asyncInit


async def reader(q):
    for x in range(10):
        await q.put(x)
        await asyncio.sleep(1)


async def monitor(q):
    try:
        while True:
            data = await q.get()
            logging.info(data)
            q.task_done()
    except asyncio.CancelledError:
        logging.info('monitor cancelling...')
        await q.join()
        logging.info('monitor cancelled')


async def runner():
    q = asyncio.Queue()
    readerTask = createTask(reader(q), 'reader')
    monitorTask = createTask(monitor(q), 'monitor')

    try:
        await asyncio.gather(*{readerTask, monitorTask})
    except asyncio.CancelledError:
        logging.info('runner cancelled')
    except Exception as e:
        logging.info(f'uncaught: {e}')


if __name__ == '__main__':
    logConfig()
    asyncio.run(asyncInit(runner))
