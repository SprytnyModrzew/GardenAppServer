import asyncio
import json

from json import JSONDecodeError

import schedule
import time

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
    generator = db.get_all_devices()
    print("woop")
    for device in generator:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(device.url + "/info") as r:
                    try:
                        text = await r.text()
                        plant = db.get_plants_of_device(device.id)["data"]
                        print("plant")
                        print(plant[0])

                        print("na dole to tekst")
                        print(text)
                        json_text = json.loads(text)
                        counter = 0
                        for i in json_text:
                            for x in i:
                                print(i)
                                db.add_measure(device_id=device.id, plant_id=plant[counter]["id"],value_of_measure=i[x], sensor_name=x)
                            counter = counter + 1

                        print(json_text)
                    except JSONDecodeError:
                        print(r)
                    except IndexError:
                        print("nope")
        except Exception:
            print("somethin wrong with")
            print(device.url)

    await asyncio.sleep(2)


async def water_notify(hour, day):
    generator = db.get_devices_to_water(hour, day)
    print("wooe")
    for device in generator:
        counter = 0
        plant = db.get_plants_of_device(device.id)
        print(device.id)
        print(device.device_name)
        print(plant["data"][counter]["water_level"])

        for p in plant["data"]:
            if p["water_time"] == hour and day in p["water_days"]:
                print("podlalo")
                async with aiohttp.ClientSession() as session:
                    async with session.get(device.url + "/pump/on/" + str(counter) + "/" + str(plant["data"][counter]["water_level"])) as r:
                        pass
            counter = counter + 1


def device_water_notifier(hour, day):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(water_notify(hour, day))


def send_measure():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(device_notifier())
    # db.add_measure(1, 1, random.uniform(0, 30), "temperature")
    print("measure!")


database = db.bind(True)

for i in hours:
    schedule.every().monday.at(i).do(device_water_notifier, hour=i, day="1")
    schedule.every().tuesday.at(i).do(device_water_notifier, hour=i, day="2")
    schedule.every().wednesday.at(i).do(device_water_notifier, hour=i, day="3")
    schedule.every().thursday.at(i).do(device_water_notifier, hour=i, day="4")
    schedule.every().friday.at(i).do(device_water_notifier, hour=i, day="5")
    schedule.every().saturday.at(i).do(device_water_notifier, hour=i, day="6")
    schedule.every().sunday.at(i).do(device_water_notifier, hour=i, day="7")
schedule.every().minute.do(send_measure)
device_water_notifier("21:30", "1")

while 1:
    schedule.run_pending()
    time.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(device_notifier())
