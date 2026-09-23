import asyncio
from json import dumps
from random import choice

async def ainput(prompt: str = "") -> str:
    return await asyncio.to_thread(input, prompt)

async def mk_json(visibility: str = "", msg: str = "") -> str:
    return dumps({"visibility" : visibility, "content" : f"{msg} + visibility : {visibility}"})+ "\n"

async def server_response(reader):
    while True:
        
        reponse = await reader.readline()
        print(f"Réponse : {reponse.decode()!r}")

async def send_msg(writer):
    while True:

        msg = await ainput("Ton nom : ")

        if msg == "[close]":
            raise SystemError

        result = await mk_json(choice(["private", "global"]), msg)
        writer.write(result.encode())
        await writer.drain()


async def main():
    reader, writer = await asyncio.open_connection("127.0.0.1", 8888)
    print("Connecté au serveur")


    async with asyncio.TaskGroup() as tg:
        tg.create_task(server_response(reader))
        tg.create_task(send_msg(writer))

        except

    
    writer.close()
    await writer.wait_closed()
            


asyncio.run(main())