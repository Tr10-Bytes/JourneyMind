# !/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project: JourneyMind
@File   : amap_api_test.py
@IDE    : PyCharm
@Author : Reznov Lee
@Date   : 2025/04/23 22:15
"""
import datetime
import json
import os

from src.core.api_clients.poi_search import AMapClient

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
    
    print("-" * 10 + "POI search test" + "-" * 10 + "\n")
    poi_search_result = amap_client.get_location_by_name(name="德思勤", city_name="长沙", facility_type="attraction")
    save_result_2_json(poi_search_result, "poi_search_result_of_attraction", output_dir)

    print("-" * 10 + "POI search test" + "-" * 10 + "\n")
    # poi_search_result = amap_client.get_location_by_name(name="鸟巢",