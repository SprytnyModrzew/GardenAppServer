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
    url = Required(str)
    max_plants = Required(int)


class Plant(db.Entity):
    id = PrimaryKey(int, auto=True)
    device = Required(Device)
    water_level = Optional(int)
    measurements = Set('Measurement')
    plant_category = Required('PlantSubDefault')
    water_time = Required(str)


class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    password = Optional(str)
    nickname = Optional(str, unique=True)
    watch_events = Set('WatchEvent')
    token = Required(str, unique=True)
    authorized = Required(bool)
    email = Required(str)


class Measurement(db.Entity):
    id = PrimaryKey(int, auto=True)
    plants = Required(Plant)
    time_of_measure = Required(datetime)
    measurement = Required(float)
    name_of_sensor = Required(str)


class PlantSubDefault(db.Entity):
    id = PrimaryKey(int, auto=True)
    plants = Set(Plant)
    subname = Required(str)
    plant_default = Required('PlantDefault')


class WatchEvent(db.Entity):
    id = PrimaryKey(int, auto=True)
    device = Optional(Device)
    user = Optional(User)
    privilege_level = Required(int)


class PlantDefault(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    plant_sub_defaults = Set(PlantSubDefault)
    default_image = Optional(int)
    default_water_level = Required(int)


@db_session
def get_plants(hour):
    plants = Plant.get(water_time=hour)
    return plants


@db_session
def define_all():
    for d in definitions.params:
        PlantDefault(name=d["name"], default_image=d["default_image"], default_water_level=d["default_water_level"])
        for plant in d["species"]:
            PlantSubDefault(subname=plant,
                            plant_default=PlantDefault.get(name=d["name"]))

    u1 = User(nickname="superszpital", password=hashlib.sha3_256(b"valerie").hexdigest(),
              token=secrets.token_urlsafe(32), authorized=True, email="20300")
    u2 = User(nickname="niesuperjarek", password=hashlib.sha3_256(b"penis").hexdigest(),
              token=secrets.token_urlsafe(32), authorized=True, email="2000")

    d1 = Device(device_name="RK9", url="https://webhook.site/026a4573-65c6-4b1e-8740-6c8a12a67a31", max_plants=3)
    d2 = Device(device_name="1337", url="https://webhook.site/026a4573-65c6-4b1e-8740-6c8a12a67a31", max_plants=1)
    d3 = Device(device_name="Choinka", url="https://webhook.site/026a4573-65c6-4b1e-8740-6c8a12a67a31", max_plants=2)
    d4 = Device(device_name="Presto", url="https://webhook.site/026a4573-65c6-4b1e-8740-6c8a12a67a31", max_plants=1)

    p1 = Plant(device=d1, water_level=0, plant_category=PlantSubDefault.get(id=3), water_time="19:30")
    p2 = Plant(device=d1, water_level=0, plant_category=PlantSubDefault.get(id=1), water_time="19:30")
    p3 = Plant(device=d2, water_level=0, plant_category=PlantSubDefault.get(id=2), water_time="19:30")
    p4 = Plant(device=d1, water_level=0, plant_category=PlantSubDefault.get(id=4), water_time="19:30")

    WatchEvent(device=d1, user=u1, privilege_level=0)
    WatchEvent(device=d2, user=u1, privilege_level=0)
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
def get_definitions():
    def_list = list(select(u for u in PlantDefault))
    def2_list = list(select(u for u in PlantSubDefault))
    ret_list = []
    for plant in def_list:
        ret_list.append(
            {
                "name": plant.name,
                "species": [i.subname for i in def2_list],
                "default_image": plant.default_image,
                "default_water_level": plant.default_water_level
            }
        )
    return ret_list


@db_session
def add_measurement(device_id, plant_id, time_of_measure, measurement):
    device = Device.get(id=device_id)
    plant = Plant.get(id=plant_id, device=device)
    if plant is None:
        return
    Measurement(plant=plant, time_of_measure=time_of_measure, measurement=measurement)


@db_session
def token_check(token):
    user = User.get(token=token)

    print(select(u.token for u in User))
    return True if user is not None else False


@db_session
def get_all_plant_defaults():
    plants = (select(u for u in PlantDefault))
    return json_pack(plants)


@db_session
def get_all_devices():
    device = list(select(u for u in Device))
    for d in device:
        yield d


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


@db_session
def get_owned_devices(token):
    devices1 = (select((u.device.id, u.device.device_name, u.privilege_level) for u in WatchEvent if
                       u.user.token == token and (u.privilege_level == 0)))
    return devices1


def json_pack(data):
    result = {'data': [p.to_dict() for p in data]}
    return result


@db_session
def show():
    # print(select(u for u in PlantType).show())
    print(select(u for u in PlantDefault).show())
    print(select(p for p in PlantDefault if p.plant_type.name == definitions.names["tomato"]).show())


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

@db_session
def get_available_plants(token):
    devices = get_owned_devices(token)
    plants = (select(u for u in Plant if Plant.device in devices))
    return plants.to_json(with_schema=False)


class Getter:
    def __init__(self, token):
        self.token = token
        self.category = {
            "plant_categories": get_all_plant_defaults(),
            "devices": get_available_devices(token),
            "plants": get_available_plants(token)
        }
