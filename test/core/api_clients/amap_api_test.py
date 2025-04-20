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
    weather_info = amap_client.get_weather(city_code="110000")
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
    
    # Testing attractions search by city
    print("Testing attractions search by city")
    attractions_by_city = amap_client.get_attractions(
        city_name="北京",
        keywords="故宫",
        location=None,
        radius=3000,
        page=1,
        offset=20
    )
    print("attractions_by_city_result")
    print(json.dumps(attractions_by_city, ensure_ascii=False, indent=2))
    save_result_2_json(attractions_by_city, "attractions_by_city", output_dir)
    print("\n" + "-"*50 + "\n")
    
    # Testing attractions search by location
    print("Testing attractions search by location")
    attractions_by_location = amap_client.get_attractions(
        city_name="上海",
        keywords="外滩",
        location="121.490317,31.236305",  # Shanghai Bund coordinates
        radius=2000,
        page=1,
        offset=20
    )
    print("attractions_by_location_result")
    print(json.dumps(attractions_by_location, ensure_ascii=False, indent=2))
    save_result_2_json(attractions_by_location, "attractions_by_location", output_dir)
    print("\n" + "-"*50 + "\n")
    
    # Testing attractions search by different types
    print("Testing attractions search by different types")
    attractions_by_type = amap_client.get_attractions(
        city_name="杭州",
        keywords="西湖",
        location=None,
        radius=5000,
        page=1,
        offset=20
    )
    print("attractions_by_type_result")
    print(json.dumps(attractions_by_type, ensure_ascii=False, indent=2))
    save_result_2_json(attractions_by_type, "attractions_by_type", output_dir)
    print("\n" + "-"*50 + "\n")

    # Testing hotels search with POI direct search
    print("Testing hotels search with POI direct search")
    hotels_poi = amap_client.poi_search(
        keywords="酒店",
        types="100000",  # Using hotel POI type code
        city="110000",   # Beijing city code
        location=None,
        radius=3000,
        page=1,
        offset=20
    )
    print("hotels_poi_result")
    print(json.dumps(hotels_poi, ensure_ascii=False, indent=2))
    save_result_2_json(hotels_poi, "hotels_poi", output_dir)
    print("\n" + "-"*50 + "\n")

    # Testing restaurants search with POI direct search
    print("Testing restaurants search with POI direct search")
    restaurants_poi = amap_client.poi_search(
        keywords="餐厅",
        types="050000",  # Using catering service POI type code
        city="110000",   # Beijing city code
        location=None,
        radius=3000,
        page=1,
        offset=20
    )
    print("restaurants_poi_result")
    print(json.dumps(restaurants_poi, ensure_ascii=False, indent=2))
    save_result_2_json(restaurants_poi, "restaurants_poi", output_dir)
    print("\n" + "-"*50 + "\n")
    
    # Testing transportation within city (integrated)
    print("Testing transportation within city (integrated)")
    transportation_within_city = amap_client.get_transportation_between(
        origin="北京市",
        destination="北京市",
        city="北京市",
        departure_time="2023-05-01 08:00:00"
    )
    print("transportation_within_city_result")
    print(json.dumps(transportation_within_city, ensure_ascii=False, indent=2))
    save_result_2_json(transportation_within_city, "transportation_within_city", output_dir)
    print("\n" + "-"*50 + "\n")
    
    # Testing transportation between cities (driving)
    print("Testing transportation between cities (driving)")
    transportation_between_cities_driving = amap_client.get_transportation_between(
        origin="北京市",
        destination="天津市"
    )
    print("transportation_between_cities_driving_result")
    print(json.dumps(transportation_between_cities_driving, ensure_ascii=False, indent=2))
    save_result_2_json(transportation_between_cities_driving, "transportation_between_cities_driving", output_dir)
    print("\n" + "-"*50 + "\n")
    
    # Testing transportation within city (walking)
    print("Testing transportation within city (walking)")
    transportation_within_city_walking = amap_client.get_transportation_between(
        origin="上海市",
        destination="上海市",
        city="上海市"
    )
    print("transportation_within_city_walking_result")
    print(json.dumps(transportation_within_city_walking, ensure_ascii=False, indent=2))
    save_result_2_json(transportation_within_city_walking, "transportation_within_city_walking", output_dir)
    print("\n" + "-"*50 + "\n")
    
    # Testing transportation within city (using place names)
    print("Testing transportation within city (using place names)")
    transportation_same_city = amap_client.get_transportation_between(
        origin="天安门",
        destination="北京大学",
        city="北京市"
    )
    print("transportation_same_city_result")
    print(json.dumps(transportation_same_city, ensure_ascii=False, indent=2))
    save_result_2_json(transportation_same_city, "transportation_same_city", output_dir)
    print("\n" + "-"*50 + "\n")
    
    # Testing transportation between cities (using place names)
    print("Testing transportation between cities (using place names)")
    transportation_cross_city = amap_client.get_transportation_between(
        origin="北京市",
        destination="天津市"
    )
    print("transportation_cross_city_result")
    print(json.dumps(transportation_cross_city, ensure_ascii=False, indent=2))
    save_result_2_json(transportation_cross_city, "transportation_cross_city", output_dir)
    print("\n" + "-"*50 + "\n")
    
    # Testing transportation using coordinates
    print("Testing transportation using coordinates")
    transportation_by_coordinates = amap_client.get_transportation_between(
        origin="116.407526,39.904030",  # Tiananmen coordinates
        destination="116.310316,39.993260"  # Peking University coordinates
    )
    print("transportation_by_coordinates_result")
    print(json.dumps(transportation_by_coordinates, ensure_ascii=False, indent=2))
    save_result_2_json(transportation_by_coordinates, "transportation_by_coordinates", output_dir)
    print("\n" + "-"*50 + "\n")
    
    # Testing transportation with departure time
    print("Testing transportation with departure time")
    transportation_with_departure_time = amap_client.get_transportation_between(
        origin="人民广场",
        destination="陆家嘴",
        city="上海市",
        departure_time="2023-05-01 08:00:00"
    )
    print("transportation_with_departure_time_result")
    print(json.dumps(transportation_with_departure_time, ensure_ascii=False, indent=2))
    save_result_2_json(transportation_with_departure_time, "transportation_with_departure_time", output_dir)
    print("\n" + "-"*50 + "\n")
