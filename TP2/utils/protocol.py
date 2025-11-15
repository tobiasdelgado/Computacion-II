import json


async def async_send_message(writer, data):
    message = json.dumps(data).encode('utf-8')
    length = len(message)
    writer.write(length.to_bytes(4, byteorder='big'))
    writer.write(message)
    await writer.drain()


async def async_receive_message(reader):
    length_bytes = await reader.read(4)
    if not length_bytes:
        return None

    length = int.from_bytes(length_bytes, byteorder='big')

    chunks = []
    bytes_received = 0
    while bytes_received < length:
        chunk = await reader.read(min(length - bytes_received, 4096))
        if not chunk:
            break
        chunks.append(chunk)
        bytes_received += len(chunk)

    message = b''.join(chunks)
    return json.loads(message.decode('utf-8'))
