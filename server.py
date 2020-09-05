import base64

from cryptography import fernet

import db
import hashlib
import emails
from aiohttp import web
import json
from aiohttp_tokenauth import token_auth_middleware
from aiohttp_session import setup, get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_session.redis_storage import RedisStorage

routes = web.RouteTableDef()


@routes.post('/add/user')
async def add_user(request):
    # todo informacja zwrotna (mail w użyciu, użytkownik zajerestrowany, takie bzdety)
    data = await request.post()
    try:
        password = hashlib.sha3_256(data["password"].encode()).hexdigest()
        token = db.add_user_unauthorized(login=data['login'], password=password, email=data['email'])
        if token:
            emails.send_mail(address_to=data['email'], token=token, nick=data['login'])
            return web.Response(text="ok")
        else:
            return web.Response(text="not ok")
    except KeyError:
        return web.Response(text="not ok")
    pass


@routes.post('/add/watch_event')
async def add_event(request):
    token = request.get("user")
    data = await request.post()

    if db.add_watch_event(token=token, id=data["id"]):
        return web.Response(text="ok")
    else:
        return web.Response(text="not ok")


@routes.post('/delete/watch_event')
async def delete_event(request):
    token = request.get("user")
    data = await request.post()

    if db.delete_watch_event(token=token, id=data['id']):
        return web.Response(text="ok")
    else:
        return web.Response(text="not ok")


@routes.get('/confirm/{token}')
async def confirm_mail(request):
    token = request.match_info.get('token', 'bonbon')
    if db.confirm_mail(token):
        return web.Response(text="ok")
    else:
        return web.Response(text="not ok")


@routes.get('/get/{get_relation}')
async def get_category(request):
    # handling of new users - get all categories
    category = request.match_info.get('get_relation', "Anonymous")
    token = request.get("user")
    get = db.Getter(token)

    text = get.category[category]
    return web.Response(text=text)


@routes.post('/debug/delete_watch_events')
async def delete_watch_events(request):
    data = request.get("user")
    print(data)
    db.debug_delete_watch_events(data)
    return web.Response(text="done")


@routes.post('/login')
async def login(request):
    # logging of the user
    data = await request.post()
    try:
        x = db.login_check(data["login"], hashlib.sha3_256(data["password"].encode()).hexdigest())
        dic = {"token": x}
        print(data['login'])
        print(data['password'])
    except KeyError:
        dic = {"token": "not authorized"}
    return web.json_response(dic)


@routes.get('/modify/water_level/{water_level}')
async def handle_modify_water_level(request):
    # modifications by users for devices - water level
    dev_id = request.match_info.get('id', "Anonymous")
    water_level = request.match_info.get('water_level', "")
    txt = "Id:{}, Water level{}".format(dev_id, water_level)
    return web.json_response(txt)


@routes.post('/exclude/{token}')
async def doopa(request):
    # todo nie działa, poprawić
    data = await request.post()
    print(data)
    dic = {"token": "not authorized"}
    return web.json_response(dic)


async def user_verify(token: str):
    user = None
    if db.token_check(token):
        user = token
    return user


database = db.bind(True)
# comment line below after creating database
#db.define_all()

# x = db.json_pack()

# db.show()
# app = web.Application()
excluded = ('/add/user', '/login', r'/confirm/.+')

app = web.Application(middlewares=[
    token_auth_middleware(user_loader=user_verify, auth_scheme='Token', exclude_routes=excluded)])
app.add_routes(routes)
web.run_app(app)
