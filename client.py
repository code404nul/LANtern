import asyncio
from json import dumps
from random import choice
import threading

class Stop(Exception):
    pass

def get_input(loop, msgs):
    while True:
        loop.call_soon_threadsafe(msgs.put_nowait, input(""))


def mk_json(visibility: str = "", msg: str = "") -> str:
    return dumps({"visibility" : visibility, "content" : f"{msg} + visibility : {visibility}"})+ "\n"

async def server_response(reader):
    while True:
        
        reponse = await reader.readline()
        if not reponse: 
            raise Stop
        print(f"> Réponse : {reponse.decode()!r}")

async def send_msg(writer, msgs):
    while True:

        msg = await msgs.get()

        if msg:
            if msg == "[close]":
                raise Stop

            result = mk_json(choice(["private", "global"]), msg)
            writer.write(result.encode())
            await writer.drain()


async def main():
    reader, writer = await asyncio.open_connection("127.0.0.1", 8888)
    print("Connecté au serveur")

    msgs = asyncio.Queue()
    loop = asyncio.get_running_loop()

    input_thread = threading.Thread(target=get_input, args = (loop, msgs), daemon=True)

    try:
        input_thread.start()
        async with asyncio.TaskGroup() as tg:
        
            tg.create_task(send_msg(writer, msgs))
            tg.create_task(server_response(reader))
    except* Stop:
        print("Arret")

    finally:
        writer.close()
        await writer.wait_closed()
            


asyncio.run(main())