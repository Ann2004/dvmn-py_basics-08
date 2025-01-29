import json
import requests
from geopy import distance
from pprint import pprint
import folium
from dotenv import load_dotenv
import os


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()["response"]["GeoObjectCollection"]["featureMember"]

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant["GeoObject"]["Point"]["pos"].split(" ")
    return lon, lat


def get_coffee_shop_distance(coffee_shop):
    return coffee_shop["distance"]


def main():
    with open("coffee.json", "r", encoding="CP1251") as coffe_file:
        coffee_contents = coffe_file.read()
    
    coffee_shops = json.loads(coffee_contents)

    user_address = input("Где вы находитесь? ")

    load_dotenv()
    apikey = os.getenv("API_KEY")

    user_address_coords = fetch_coordinates(apikey, user_address)
    user_address_coords = (user_address_coords[1], user_address_coords[0])

    coffee_shops_info = []
    for coffee_shop in coffee_shops:
        coffee_shop_coords = (coffee_shop["geoData"]["coordinates"][1], coffee_shop["geoData"]["coordinates"][0])
        spacing = distance.distance(user_address_coords, coffee_shop_coords).km
        coffee_shop_info = {"title": coffee_shop["Name"],
                           "distance": spacing,
                           "latitude": coffee_shop_coords[0],
                           "longitude": coffee_shop_coords[1]
                           }
        coffee_shops_info.append(coffee_shop_info)

    coffee_shops_sorted_distance = sorted(coffee_shops_info, key=get_coffee_shop_distance)
    nearest_coffee_shops = coffee_shops_sorted_distance[:5]

    m = folium.Map(list(user_address_coords), zoom_start=12)

    for coffee_shop in nearest_coffee_shops:
        folium.Marker(
            location=[coffee_shop["latitude"], coffee_shop["longitude"]],
            tooltip="Click me!",
            popup=coffee_shop["title"],
            icon=folium.Icon(color="darkpurple"),
        ).add_to(m)

    m.save("map.html")
    

if __name__ == '__main__':
    main()