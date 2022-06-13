import logging
import signal
import asyncio
from functools import partial


def taskHandler(task):
    try:
        task.result()
    except asyncio.CancelledError:
        logging.info(f'cancelled: {task.get_name()}')
    except Exception as e:
        logging.error(f'uncaught exception ({task.get_name()}): {e}')


def createTask(coro, name):
    task = asyncio.create_task(coro, name=name)
    task.add_done_callback(partial(taskHandler))
    return task


def shutdown():
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        logging.info(f'cancelling task: {task.get_name()}')
        task.cancel()


def exceptionHandler(loop, context):
    msg = context.get('exception', context['message'])
    logging.error(f'caught exception: {msg}')


def asyncRunner(runner):
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(exceptionHandler)
    loop.add_signal_handler(signal.SIGINT, shutdown)

    try:
        loop.run_until_complete(runner())
    except asyncio.CancelledError:
        logging.info('cancelled runner')
    finally:
        logging.info('closing event loop')
        loop.close()
