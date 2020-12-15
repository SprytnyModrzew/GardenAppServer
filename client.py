import aiohttp
import asyncio
import json


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def main():
    async with aiohttp.ClientSession() as session:
        login = {"login": "superszpital", "password": "valerie"}
        async with session.post('http://192.168.1.151:8080/login', data=login) as r:
            text = await r.text()
            print(text)
            header = {'Authorization': 'Token ' + text}
    async with aiohttp.ClientSession(headers=header) as session:
        async with session.post("http://192.168.1.151:8080/send/measures") as r:
            pass

    '''async with aiohttp.ClientSession(headers=header) as session:
        datas = {"login": "Wojciecssh", "password": "penis", "email": "@gmail.com"}
        async with session.post('http://192.168.1.151:8080/add/user', data=datas) as r:
            html = await r.text()
            print(html)
            device_id = "RK9"
            datata = {"device_name": device_id}
    async with aiohttp.ClientSession(headers=header) as session:
        device_id = "RK9"
        datata = {"device_name": device_id}
        async with session.post('http://192.168.1.151:8080/add/watch_event', data=datata) as r:
            html = await r.text()
            print(html)'''


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
