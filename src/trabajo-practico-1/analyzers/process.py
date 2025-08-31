import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multiprocessing import Queue
from multiprocessing.connection import Connection
from analyzers import frequency_analyzer, pressure_analyzer, oxygen_analyzer


def frequency_process(pipe: Connection, queue: Queue):
    while True:
        data = pipe.recv()
        if data is None:
            break
        result = frequency_analyzer(data["frequency"])
        queue.put(result)


def pressure_process(pipe: Connection, queue: Queue):
    while True:
        data = pipe.recv()
        if data is None:
            break
        result = pressure_analyzer(data["pressure"])
        queue.put(result)


def oxygen_process(pipe: Connection, queue: Queue):
    while True:
        data = pipe.recv()
        if data is None:
            break
        result = oxygen_analyzer(data["oxygen"])
        queue.put(result)