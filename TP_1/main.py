import time
from multiprocessing import Pipe, Process, Queue
from generator import generate_raw_data_block
from analyzers import frequency_process, pressure_process, oxygen_process
from verifier import verifier_process
from common import clear_blockchain


if __name__ == "__main__":
    # Limpiar blockchain al inicio
    clear_blockchain()

    # Pipes
    freq_pipe_input, freq_pipe_output = Pipe()
    pressure_pipe_input, pressure_pipe_output = Pipe()
    oxygen_pipe_input, oxygen_pipe_output = Pipe()

    # Queue
    verify_queue = Queue()

    # Procesos analizadores
    freq_proc = Process(target=frequency_process, args=(freq_pipe_output, verify_queue))
    freq_proc.start()

    pressure_proc = Process(
        target=pressure_process, args=(pressure_pipe_output, verify_queue)
    )
    pressure_proc.start()

    oxygen_proc = Process(
        target=oxygen_process, args=(oxygen_pipe_output, verify_queue)
    )
    oxygen_proc.start()

    # Proceso verificador
    data_block_verifier_proc = Process(target=verifier_process, args=(verify_queue,))
    data_block_verifier_proc.start()

    # Generador de bloques de datos
    for i in range(60):
        data_block = generate_raw_data_block()

        freq_pipe_input.send(data_block)
        pressure_pipe_input.send(data_block)
        oxygen_pipe_input.send(data_block)

        time.sleep(1)

    # Terminar procesos
    freq_pipe_input.send(None)
    pressure_pipe_input.send(None)
    oxygen_pipe_input.send(None)
    verify_queue.put(None)

    # Esperar a que terminen
    freq_proc.join()
    pressure_proc.join()
    oxygen_proc.join()
    data_block_verifier_proc.join()
