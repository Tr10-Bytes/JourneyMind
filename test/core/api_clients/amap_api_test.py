# !/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project: JourneyMind
@File   : amap_api_test.py
@IDE    : PyCharm
@Author : Reznov Lee
@Date   : 2025/04/13 13:01
"""
import datetime
import json
import os

from src.core.api_clients.amap import AMapClient


def save_result_2_json(date, filename, direction):
    """
    Save the result to a json file.
    :param date: The date of the file to be saved.
    :param filename: The name of the file to be saved.
    :param direction: The direction of the file to be saved.
    :return: None
    """
    if not os.path.exists(direction):
        os.makedirs(direction)

    file_path = os.path.join(direction, f"{filename}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(date, f, ensure_ascii=False, indent=2)
    print(f"Results have saved to {file_path}")

if __name__ == '__main__':
    amap_client = AMapClient(api_key="abb58eef7776ca203132dd616d746dc1")

    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    output_dir = f"output/amap_api_test_{today_date}"

    print("Using code to get info")
    weather_info = amap_client.weather(city_code="110000")
    print("weather_info")
    print(json.dumps(weather_info, ensure_ascii=False, indent=4))
    save_result_2_json(weather_info, "weather", output_dir)
    print("\n" + "-"*50 + "\n")

    route = amap_client.route_planning(
        origin="116.481028,39.989643",
        destination="116.465302,40.003768",
        mode="driving",
        waypoints="116.481028,39.989643;116.465302,40.003768",
        strategy=0
    )
    print("route_info")
    print(json.dumps(route, ensure_ascii=False, indent=2))
    save_result_2_json(route, "route", output_dir)
    print("\n" + "-"*50 + "\n")

    poi_search = amap_client.poi_search(
        keywords="美食",
        types="050000",
        city="110000",
        location="116.481028,39.989643",
        radius=1000,
        page=1,
        offset=20
    )
    print("poi_search_result")
    print(json.dumps(poi_search, ensure_ascii=False, indent=2))
    save_result_2_json(poi_search, "poi_search", output_dir)
    print("\n" + "-"*50 + "\n")

    print("Using name to get info")

    weather_info = amap_client.get_weather_by_city_name(city_name="长沙")
    print("weather_info")
    print(json.dumps(weather_info, ensure_ascii=False, indent=4))
    save_result_2_json(weather_info, "weather_by_name", output_dir)
    print("\n" + "-"*50 + "\n")
    route = amap_client.plan_route_by_name(
        origin_name="长沙站",
        destination_name="长沙南站",
        city_name="长沙市",
        mode="driving",
        waypoints="德思勤",
        strategy=0
    )
    print("route_info")
    print(json.dumps(route, ensure_ascii=False, indent=2))
    save_result_2_json(route, "route_by_name", output_dir)
    print("\n" + "-"*50 + "\n")
    poi_search = amap_client.search_poi_by_name(
        keywords="美食",
        poi_name="中南大学天心校区",
        city_name="长沙市",
        radius=5000,
        page=1,
        offset=20
    )
    print("poi_search_result")
    print(json.dumps(poi_search, ensure_ascii=False, indent=2))
    save_result_2_json(poi_search, "poi_search_by_name", output_dir)
    print("\n" + "-"*50 + "\n")

