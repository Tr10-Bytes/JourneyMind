# !/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project: JourneyMind
@File   : weather.py
@IDE    : PyCharm
@Author : Reznov Lee
@Date   : 2025/04/28 13:25
"""
import poi_search as ps

class Weather:
    def __init__(self, api_key):
        self.api_key = api_key
        self.amap_client = ps.AMapClient(api_key)

    def get_weather(self, city_code, extensions="full"):
        """
        Get the weather information of a city.
        :param city_code: The city code of the city to be queried.
        :param extensions: The extension of the weather information.
        :return: The weather information of the city.
        """
        params = {
            'city': city_code,
            'extensions': extensions
        }
        return self._send_request('weather/weatherInfo', params)

    def get_weather_by_city_name(self, city_name, extensions='base'):
        """
        Get the weather information of a city by city name.
        :param city_name: The name of the city to be queried.
        :param extensions: The extension of the weather information.
        :return: The weather information of the city.
        """
        city_code = ps.AMapClient.get_city_code(city_name)
        if city_code:
            return self.get_weather(city_code, extensions)
        else:
            return {"status": "0", "info": "City code not found"}