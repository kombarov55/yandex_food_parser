import requests

from model.food import FoodVO
from model.restaurant import RestaurantVO


def load_restaurant_food(slug: str, restaurant_id) -> list[FoodVO]:
    print("loading food for /r slug={}".format(slug))

    url = "https://eda.yandex.ru/api/v2/menu/retrieve/{}".format(slug)
    res = requests.get(url)
    json = res.json()
    categories = json["payload"]["categories"]
    result = []
    for category in categories:
        name = category["name"]
        items = category["items"]
        for item in items:
            result.append(FoodVO(
                name=get_field(item, "name"),
                description=get_field(item, "description"),
                price=get_field(item, "price"),
                weight=get_field(item, "weight"),
                src=get_nested_field(item, "picture", "uri"),
                restaurant_id=restaurant_id
            ))
    print("slug={} len(result)={}".format(slug, len(result)))
    return result


def load_retail_food(category_ids: list[int], slug) -> list[FoodVO]:
    print("loading food for /retail slug={}".format(slug))

    result = []
    for category_id in category_ids:
        url = "https://eda.yandex.ru/api/v2/menu/goods"
        body = {"slug": slug, "category": category_id, "filters": {}, "maxDepth": 100}
        rs = requests.post(url, json=body)
        try:
            json = rs.json()

            categories = json["payload"]["categories"]
            for category in categories:
                name = category["name"]
                items = category["items"]
                print("received {} items for category {}".format(len(items), name))

                if len(items) != 0:
                    for item in items:
                        vo = FoodVO(
                            restaurant_id=slug,
                            name=get_field(item, "name"),
                            description=get_field(item, "description"),
                            price=get_field(item, "price"),
                            weight=get_field(item, "weight"),
                            src=get_nested_field(item, "picture", "url")
                        )
                        result.append(vo)
        except:
            print("failed to POST:")
            print("POST {}".format(url))
            print(body)
            print("response ({}): ".format(rs.status_code))
            print(rs.content)

        print("slug={} len(result)={}".format(slug, len(result)))
        return result


def load_retail_info(slug) -> RestaurantVO:
    rs = requests.get("https://eda.yandex.ru/api/v2/catalog/{}".format(slug))
    json = rs.json()

    found_place = json["payload"]["foundPlace"]
    place = json["payload"]["foundPlace"]["place"]

    delivery_time = ""

    location_params = found_place["locationParams"]
    if location_params is not None:
        delivery_time = location_params["deliveryTime"]["min"] + "-" + location_params["deliveryTime"]["max"],

    return RestaurantVO(
        slug=slug,
        name=place["name"],
        rating=place["rating"],
        rating_count=place["ratingCount"],
        delivery_time=delivery_time,
        address=place["address"]["short"],
        longitude=place["address"]["location"]["longitude"],
        latitude=place["address"]["location"]["latitude"]
    )


def get_field(item: dict, name: str):
    if name in item:
        return str(item[name])
    else:
        return None


def get_nested_field(item, name1, name2):
    if name1 in item:
        nested = item[name1]
        if nested is not None and name2 in nested:
            return nested[name2]
        else:
            return None
    else:
        return None
