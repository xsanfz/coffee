import json
import os
import requests
from geopy import distance
from pprint import pprint
import folium
from dotenv import load_dotenv


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def load_coffee_shops():
    with open("coffee.json", "r", encoding="CP1251") as file:
        return json.load(file)


def create_coffee_list(user_coords, coffee_data):
    if not coffee_data:
        return None

    coffee_list = []
    user_lat = float(user_coords[1])
    user_lon = float(user_coords[0])

    for shop in coffee_data:
        shop_lon, shop_lat = shop["geoData"]["coordinates"]
        dist = distance.distance((user_lat, user_lon), (shop_lat, shop_lon)).km

        coffee_list.append({
            'title': shop['Name'],
            'distance': dist,
            'latitude': shop_lat,
            'longitude': shop_lon
        })

    return coffee_list


def find_nearest(coffee_list):
    if not coffee_list:
        return None
    nearest = sorted(coffee_list, key=lambda x: x['distance'])
    nearest_5 = nearest[:5]
    return nearest_5


def create_map(user_coords, nearest_shops):
    m = folium.Map(location=[user_coords[1], user_coords[0]], zoom_start=14)

    folium.Marker(
        location=[user_coords[1], user_coords[0]],
        popup="Ваше местоположение",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

    for shop in nearest_shops:
        folium.Marker(
            location=[shop['latitude'], shop['longitude']],
            popup=shop['title'],
            icon=folium.Icon(color="green", icon="coffee")
        ).add_to(m)

    m.save("coffee_map.html")


def main():
    load_dotenv()

    api_key = os.getenv('YANDEX_API_KEY')

    if not api_key:
        print("Не найден YANDEX_API_KEY в .env файле")
        return

    user_address = input("Где вы находитесь? ")
    user_coords = fetch_coordinates(api_key, user_address)

    if not user_coords:
        print("Не удалось определить координаты для указанного адреса")
        return

    print(f"Ваши координаты: {user_coords}")

    coffee_data = load_coffee_shops()
    if not coffee_data:
        return

    coffee_shops = create_coffee_list(user_coords, coffee_data)
    if not coffee_shops:
        print("Нет данных о кофейнях")
        return

    nearest = find_nearest(coffee_shops)

    pprint(nearest, width=40, indent=2, sort_dicts=False)

    create_map(user_coords, nearest)


if __name__ == "__main__":
    main()