import asyncio
from time import time


shared_ressource = 0
lock = asyncio.Lock()


async def fetch_data(delay):
    print("Fetching data...")
    await asyncio.sleep(delay)
    print("Data fetched")
    return {"Data": "some data"}


async def modifed_ressources(data):
    global shared_ressource

    test = shared_ressource
    print(test)
    await asyncio.sleep(3)
    shared_ressource = test + data
    print("ressources modified")


async def modifed_correctly_ressources(data):
    global shared_ressource

    async with lock:
        print(f"ressources before modification {shared_ressource}")
        shared_ressource += 1
        await asyncio.sleep(3)
        print(f"Ressource after modification: {shared_ressource}")


async def main1():
    print("Start main coroutine")
    task = fetch_data(2)
    result = await task
    print(f"Received result {result}")
    print("end coroutine")


async def main2():
    task1 = asyncio.create_task(fetch_data(3))
    task2 = asyncio.create_task(fetch_data(3))
    task3 = asyncio.create_task(fetch_data(3))

    result1 = await task1
    reuslt2 = await task2
    reuslt3 = await task3

    print(result1, reuslt2, reuslt3)


async def main3():
    results = await asyncio.gather(fetch_data(3), fetch_data(3), fetch_data(3))

    for result in results:
        print(result)


async def main4():
    tasks = []

    async with asyncio.TaskGroup() as tg:
        for i in range(3):
            task = tg.create_task(fetch_data(3))
            tasks.append(task)

    print([task.result() for task in tasks])


async def main5():
    await asyncio.gather(*(modifed_ressources(3) for _ in range(3)))


async def main6():
    await asyncio.gather(*(modifed_correctly_ressources(3) for _ in range(3)))


def test_modification_ressources():
    global shared_ressource

    start = time()
    asyncio.run(main5())
    print(f"Elapsed time : {time() - start}")

    print(shared_ressource)
    shared_ressource = 0

    start = time()
    asyncio.run(main6())
    print(f"Elapsed time : {time() - start}")

    print(shared_ressource)
