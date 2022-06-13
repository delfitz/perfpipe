import logging
import json
import asyncio

from utils.asyncUtils import createTask


async def readProc(q, procPipe):
    header = await procPipe.readline()
    del header
    async for line in procPipe:
        await q.put(line.decode('utf-8').rstrip('\n'))


async def writePipe(q, sysPipe, formatter):
    dataBuffer = []
    error = ''
    while True:
        try:
            dataBuffer.append(json.loads(await q.get()))
            dataBuffer, formatted = formatter(dataBuffer)
            with open(sysPipe, 'wt') as p:
                p.write(formatted + '\n')
            q.task_done()
        except json.JSONDecodeError:
            error = 'vnstat exited'
        except asyncio.CancelledError:
            error = 'monitor cancelled'
            logging.info('raising cancellation')
            raise asyncio.CancelledError
        finally:
            if error:
                logging.info(f'flushing pipe: {error}')
                with open(sysPipe, 'wt') as p:
                    p.write(f'{error}\n')


async def startPipe(command, pipe, formatter):
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT)

    q = asyncio.Queue()
    readerTask = createTask(readProc(q, proc.stdout), 'reader')
    writerTask = createTask(writePipe(q, pipe, formatter), 'writer')

    await asyncio.gather(readerTask)
    await q.join()
    writerTask.cancel()
    logging.error('pipe closed')


if __name__ == '__main__':
    pass
