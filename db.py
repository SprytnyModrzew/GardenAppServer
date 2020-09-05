from datetime import datetime, date
from pony.orm import *

import definitions
import json
import hashlib
import secrets

db = Database()


class Device(db.Entity):
    id = PrimaryKey(int, auto=True)
    device_name = Required(str)
    plants = Set('Plant')
    watch_events = Set('WatchEvent')


class Plant(db.Entity):
    id = PrimaryKey(int, auto=True)
    device = Required(Device)
    water_level = Optional(int)
    water_time = Optional(datetime)
    measurements = Set('Measurements')
    plant_category = Required('PlantCategory')
    plant_time = Required(date)


class PlantType(db.Entity):
    id = PrimaryKey(int, auto=True)
    plant_categories = Set('PlantCategory')
    name = Required(str)
    default_water = Required(int)


class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    password = Optional(str)
    nickname = Optional(str, unique=True)
    watch_events = Set('WatchEvent')
    token = Required(str, unique=True)
    authorized = Required(bool)
    email = Required(str)


class Measurements(db.Entity):
    id = PrimaryKey(int, auto=True)
    plants = Required(Plant)
    humidity = Required(float)
    temperature = Required(float)
    water_level = Required(float)
    time_of_measure = Required(datetime)


class PlantCategory(db.Entity):
    id = PrimaryKey(int, auto=True)
    plant_type = Required(PlantType)
    plants = Set(Plant)
    subname = Required(str)
    fertilize_time_days = Required(int)
    sprout_time_days = Required(int)
    fruit_time_days = Required(int)


class WatchEvent(db.Entity):
    id = PrimaryKey(int, auto=True)
    device = Optional(Device)
    user = Optional(User)
    privilege_level = Required(int)


@db_session
def define_all():
    for i in definitions.names:
        print(i)
        category = PlantType(name=definitions.names[i], default_water=definitions.params[i]["default_water"])
        veg_generator = definitions.functions[i]
        try:
            while True:
                PlantCategory(subname=veg_generator.__next__(), plant_type=category,
                              fertilize_time_days=definitions.params[i]["fertilize"],
                              sprout_time_days=definitions.params[i]["sprout"],
                              fruit_time_days=definitions.params[i]["fruit"])
        except StopIteration:
            pass

    u1 = User(nickname="superszpital", password=hashlib.sha3_256(b"valerie").hexdigest(),
              token=secrets.token_urlsafe(32), authorized=True, email="20300")
    u2 = User(nickname="niesuperjarek", password=hashlib.sha3_256(b"penis").hexdigest(),
              token=secrets.token_urlsafe(32), authorized=True, email="2000")

    d1 = Device(device_name="RK9")
    d2 = Device(device_name="1337")
    d3 = Device(device_name="Choinka")
    d4 = Device(device_name="Presto")

    WatchEvent(device=d1, user=u1, privilege_level=0)
    WatchEvent(device=d2, user=u2, privilege_level=0)
    WatchEvent(device=d3, user=u2, privilege_level=0)
    WatchEvent(device=d4, user=u2, privilege_level=0)
    print("woop")


@db_session
def login_check(login, password):
    try:
        user = User.get(nickname=login, password=password)
        if user.authorized:
            return user.token
        else:
            return None
    except AttributeError:
        return None


@db_session
def token_check(token):
    user = User.get(token=token)

    print(select(u.token for u in User))
    return True if user is not None else False


@db_session
def get_all_plant_categories():
    plants = (select(u for u in PlantCategory))
    return json_pack(plants)


@db_session
def confirm_mail(token):
    user = User.get(token=token)
    if user is not None:
        user.set(authorized=True)
        return True
    else:
        return False


@db_session
def add_watch_event(token, id):
    # todo add watch events
    user = User.get(token=token)
    device = Device.get(id=id)
    x = WatchEvent.get(user=user, device=device)
    select(u for u in WatchEvent).show()
    if x is not None:
        return False
    WatchEvent(device=device, user=user, privilege_level=1)
    return True


@db_session
def delete_watch_event(token, event_id):
    user = User.get(token=token)
    device = Device.get(id=event_id)
    x = WatchEvent.get(user=user, device=device, privilege_level=1)
    select(u for u in WatchEvent).show()
    if x is None:
        return False
    print(x.id)
    WatchEvent[x.id].delete()
    select(u for u in WatchEvent).show()
    return True


@db_session
def rename_device(token, event_id, new_name):
    user = User.get(token=token)
    device = Device.get(id=event_id)
    x = WatchEvent.get(user=user, device=device, privilege_level=0)
    if x is None:
        return False
    device.device_name = new_name
    return True


@db_session
def add_user_unauthorized(login, password, email):
    user = User.get(nickname=login)
    if user is not None:
        return False
    user = User.get(email=email)
    if user is not None:
        return False
    x = secrets.token_urlsafe(32)
    User(nickname=login, password=password, email=email, authorized=False, token=x)
    select(u for u in User).show()
    return x


@db_session
def get_available_devices(token):
    # todo this
    devices1 = (select((u.device.id, u.device.device_name, u.privilege_level) for u in WatchEvent if
                       u.user.token == token and (u.privilege_level == 0 or u.privilege_level == 1)))
    devices1.show()

    return devices1.to_json(with_schema=False)


def json_pack(data):
    result = {'data': [p.to_dict() for p in data]}
    return result


@db_session
def show():
    # print(select(u for u in PlantType).show())
    print(select(u for u in PlantCategory).show())
    print(select(p for p in PlantCategory if p.plant_type.name == definitions.names["tomato"]).show())


@db_session
def debug_delete_watch_events(token):
    delete(p for p in WatchEvent if p.user.token == token and p.privilege_level == 1)


def bind(create_db=False):
    if create_db:
        db.bind(provider='sqlite', filename='database.db', create_db=True)
        db.generate_mapping(create_tables=True)
    else:
        db.bind(provider='sqlite', filename='database.db', create_db=False)
        db.generate_mapping()
    return db


class Getter:
    def __init__(self, token):
        self.token = token
        self.category = {
            "plant_categories": get_all_plant_categories(),
            "devices": get_available_devices(token)
        }
