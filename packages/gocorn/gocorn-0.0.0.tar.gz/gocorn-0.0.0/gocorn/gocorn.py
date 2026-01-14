import asyncio
import json
import struct
import socket


class IPCHelper:

    async def read_message(self, reader):
        raw_len = await reader.readexactly(4)
        length = struct.unpack(">I", raw_len)[0]
        payload = await reader.readexactly(length)
        return json.loads(payload)

    async def write_message(self, writer, message):
        data = json.dumps(message).encode()
        writer.write(struct.pack(">I", len(data)) + data)
        await writer.drain()


class WorkerHandler:

    def __init__(self, ipc_helper: IPCHelper, app):
        self.ipc_helper = ipc_helper
        self.app = app

    async def handle_client(self, reader, writer):
        request = await self.ipc_helper.read_message(reader)
        scope = request["scope"]

        async def receive():
            return {
                "type": "http.request",
                "body": b"",
                "more_body": False,
            }

        async def send(message):
            if "body" in message and isinstance(message["body"], (bytes, bytearray)):
                message["body"] = message["body"].decode("latin1")
                message["_binary"] = True
            await self.ipc_helper.write_message(writer, message)

        await self.app(scope, receive, send)
        writer.close()


async def volk2(app):
    ipc_helper = IPCHelper()
    worker_handler = WorkerHandler(ipc_helper=ipc_helper, app=app)

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind("/tmp/asgi.sock")
    sock.listen()
    sock.setblocking(False)

    server = await asyncio.start_unix_server(worker_handler.handle_client, sock=sock)

    async with server:
        await server.serve_forever()
