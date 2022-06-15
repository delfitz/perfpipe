import logging
import asyncio

from utils.asyncUtils import createTask

TIMESTAMP_LEN = 11
BUFFER_LEN = 10


async def pipeWriter(pipe, data):
    with open(pipe, 'wt') as p:
        p.write(f'{data}\n')


def parseTable(table, cols):
    headers = table[0][TIMESTAMP_LEN:].split()
    selected = [(*[headers[i] for i in cols],)]
    for row in table[1:]:
        rowData = row[TIMESTAMP_LEN:].split()
        selected.append((*[rowData[i] for i in cols],))
    return selected


async def tableReader(q, stream, cols):
    _ = await stream.readline()
    while True:
        table = []
        while (line := await stream.readline()) != b'\n':
            table.append(line.decode('utf-8').rstrip('\n'))
        if table:
            await q.put(parseTable(table, cols))


async def processMonitor(q, pipe, formatter):
    while True:
        data = await q.get()
        line = await formatter(data)
        await pipeWriter(pipe, line)
        q.task_done()


async def processRunner(pipe, cmd, cols, formatter):
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
    q = asyncio.Queue()
    readerTask = createTask(tableReader(q, proc.stdout, cols), 'reader')
    monitorTask = createTask(processMonitor(q, pipe, formatter), 'monitor')
    await asyncio.gather(*{readerTask, monitorTask})    # propagates
