class Plant:
    def __init__(self):
        pass


def get_tomatoes():
    tomatoes = ["Grape", "Red Beefsteak", "Green Beefsteak", "Cherry", "Cocktail", "Roma", "Heirloom", "Vine"]
    tomatoes = ["Ree", "Woo"]
    for i in tomatoes:
        yield i


def get_potatoes():
    potatoes = ["Russet", "Jewel Yam", "Japanese Sweet", "Hannah Sweet", "Rose Finn Apple", "Russian Banana",
                "Red Thumb",
                "French Fingerling", "LaRette", "Austrian Crescent", "Red Gold", "Purple Majesty", "Norland Red",
                "Yukon Gold", "Kennebec", "All Blue"]
    potatoes = ["Woo", "Goo"]
    for i in potatoes:
        yield i


names = {
    "tomato": "Tomato",
    "potato": "Potato"
}
functions = {
    "tomato": get_tomatoes(),
    "potato": get_potatoes()
}
params = [

    {
        "name": "Tomato",
        "species": ["Grape", "Red Beefsteak", "Green Beefsteak", "Cherry", "Cocktail", "Roma", "Heirloom", "Vine"],
        "default_image": 2,
        "default_water_level": 0
    }, {
        "name": "Potato",
        "species": ["Russet", "Jewel Yam", "Japanese Sweet", "Hannah Sweet", "Rose Finn Apple", "Russian Banana",
                    "Red Thumb",
                    "French Fingerling", "LaRette", "Austrian Crescent", "Red Gold", "Purple Majesty", "Norland Red",
                    "Yukon Gold", "Kennebec", "All Blue"],
        "default_image": 1,
        "default_water_level": 0
    }
]
