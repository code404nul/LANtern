import asyncio
from json import loads, dumps


writers = set()

async def gerer_client(reader, writer):

    adresse = writer.get_extra_info("peername")
    print(f"Nouveau client : {adresse}")

    writers.add(writer)

    try:
        while True:

            try:
                async with asyncio.timeout(10):
                    donnees = await reader.readline()
            except TimeoutError:
                print("client not responding")
                break

            if not donnees: break
            message = loads(donnees.decode() )
            print(f"Reçu : {message!r}")

            if message["visibility"] == "private":
                reponse = {"Status": "ok", "message": ""}
                writer.write((dumps(reponse) + "\n").encode())
                await writer.drain()


            elif message["visibility"] == "global":

                writers_cp = writers.copy()
                reponse = {"Status": "ok", "message": message["content"]}
                for dest_writer in writers_cp:
                    try:
                        dest_writer.write((dumps(reponse) + "\n").encode())
                        await  dest_writer.drain()
                        
                    except ConnectionError:
                        print("A new client that can't be serve !!! How bad are you in waitress. grrr")

    finally:

        writers.remove(writer)
        writer.close()
        await writer.wait_closed()
        print(f"Client {adresse} parti")

async def main():
    
    serveur = await asyncio.start_server(gerer_client, "127.0.0.1", 8888)
    print("Serveur prêt sur le port 8888")
    async with serveur:
        await serveur.serve_forever()

asyncio.run(main())