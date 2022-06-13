import subprocess
import time
import threading
import queue
import json

TS_LEN = 11
BUFF_LEN = 10


class AsyncPipeReader(threading.Thread):

    def __init__(self, fd, queue, isJson=False):
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = queue
        self._isJson = isJson

    def readPipe(self):
        _ = self._fd.readline()
        while True:
            if self._isJson:
                interval = self._fd.readline()
                print(interval)    # foo
                try:
                    self._queue.put(json.loads(interval))
                except json.JSONDecodeError:
                    self._queue.put(None)
            else:
                interval = []
                while line := self._fd.readline().rstrip('\n'):
                    interval.append(line)
                if interval:
                    self._queue.put(interval)

    def run(self):
        self.exception = None
        try:
            self.readPipe()
        except BaseException as e:
            self.exception = e

    def join(self):
        threading.Thread.join(self)
        if self.exception:
            raise self.exception

    def eof(self):
        return not self.is_alive() and self._queue.empty()


def pipeWriter(pipe, data):
    with open(pipe, 'wt') as fw:
        if not data:
            print('no data')
        else:
            fw.write(data + '\n')


def parseTable(intervalData, indicies):
    headers = intervalData[0][TS_LEN:].split()
    selected = [(*[headers[i] for i in indicies],)]
    for rowData in intervalData[1:]:
        cols = rowData[TS_LEN:].split()
        selected.append((*[cols[i] for i in indicies],))
    return selected


def startPipe(command,
              pipe,
              isJson=False,
              columns=None,
              formatter=None,
              delay=0.1):
    process = subprocess.Popen(command,
                               shell=True,
                               text=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    stdout_queue = queue.Queue()
    stdout_reader = AsyncPipeReader(process.stdout, stdout_queue, isJson)
    stdout_reader.start()

    stderr_queue = queue.Queue()
    stderr_reader = AsyncPipeReader(process.stderr, stderr_queue)
    stderr_reader.start()

    try:
        dataBuffer = []
        while not stdout_reader.eof() or not stderr_reader.eof():
            while not stdout_queue.empty():
                data = stdout_queue.get()
                if not data:
                    line = formatter(None)
                else:
                    if columns:
                        data = parseTable(data, columns)
                    dataBuffer.append(data)
                    dataBuffer = dataBuffer[-BUFF_LEN:]
                    line = formatter(dataBuffer)
                if pipe:
                    pipeWriter(pipe, line)

            while not stderr_queue.empty():
                line = stderr_queue.get()
                print(f'stderr: {line}')

            # time.sleep(delay)

        stdout_reader.join()
        stderr_reader.join()
    except Exception as e:
        print('exception raised:', e)

    process.stdout.close()
    process.stderr.close()
