# !/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project: JourneyMind
@File   : amap.py
@IDE    : PyCharm
@Author : Reznov Lee
@Date   : 2025/04/23 22:01
"""
import requests


class AMapClient:
    """ Amap API calling base class, used to obtain information such as paths, routes, and weather

    Attributes:
        api_key: Amap API key

    """
    def __init__(self,api_key):
        """ Initialize AmapClient class

        The initializer is mainly used to specify the API key used by AMAP.

        Args:
            api_key: Amap API key
        """
        self.api_key = api_key
        self.url = "https://restapi.amap.com/v3"

    def _send_request(self, endpoint, params):
        """ Send request to Amap API

        Internal method to send request to AMAP to get data.

        Args:
            endpoint: Amap API endpoint
            params: Amap API parameters
        Returns:
            response: Amap API response
        """
        params['key'] = self.api_key
        url = f"{self.url}/{endpoint}"
        response = requests.get(url, params=params)
        return response.json()

def get_location_by_name(self, facility_type, name, city_name):
        """Get location information by place name

        Args:
            facility_type: Type of facility to search for ('restaurant', 'attraction', 'mall', 'shop', 'supermarket')
            name: Place name to search for
            city_name: City name to limit search scope

        Returns:
            dict: JSON response containing location information for specified facility type
        """
        # 设置设施类型映射
        type_mapping = {
            'restaurant': '050000',    # 餐饮服务
            'attraction': '110000',    # 风景名胜
            'mall': '060100',         # 商场
            'shop': '060200',         # 购物服务
            'supermarket': '060400'    # 超级市场
        }
        
        if facility_type not in type_mapping:
            raise ValueError(f"Unsupported facility type. Supported types are: {', '.join(type_mapping.keys())}")
            
        params = {
            'keywords': name,
            'extensions': 'all',
            'output': 'json',
            'types': type_mapping[facility_type]
        }
        
        if city_name:
            params['city'] = city_name
            
        return self._send_request('place/text', params)