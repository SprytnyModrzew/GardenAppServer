import asyncio
import threading

import schedule
import time
import queue

import aiohttp

import db

# scheduled hours
hour_list = [i for i in range(0, 24)]
for i in range(0, len(hour_list)):
    if hour_list[i] < 10:
        hour_list[i] = "0" + str(hour_list[i])
    else:
        hour_list[i] = str(hour_list[i])

minute_list = ["30", "00"]
hours = [f"{hour}:{minute}" for hour in hour_list for minute in minute_list]
print(hours)


async def device_notifier():
    while True:
        generator = db.get_all_devices()
        for device in generator:
            async with aiohttp.ClientSession() as session:
                async with session.get(device.url) as r:
                    text = await r.text()
                    print(text)
        await asyncio.sleep(2)

#todo nie wiem co tu napisalem
async def water_notify(hour):
    generator = db.get_all_devices()
    for device in generator:
        async with aiohttp.ClientSession() as session:
            async with session.get(device.url) as r:
                text = await r.text()
                print(text)


def device_water_notifier(hour):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(water_notify(hour))


database = db.bind(True)

for i in hours:
    schedule.every().day.at(i).do(device_water_notifier, hour=i)

while 1:
    schedule.run_pending()
    time.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(device_notifier())
