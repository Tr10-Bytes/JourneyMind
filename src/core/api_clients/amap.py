# !/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project: JourneyMind
@File   : amap.py
@IDE    : PyCharm
@Author : Reznov Lee
@Date   : 2025/04/12 15:21
"""
import requests


class AMapClient:
    """ Amap API calling base class, used to obtain information such as paths, routes, and weather

    Attributes:
        api_key: Amap API key

    """
    def __init__(self,api_key):
        """ Initialize AmapClient class
        Args:
            api_key: Amap API key
        """
        self.api_key = api_key
        self.url = "https://restapi.amap.com/v3"

    def _send_request(self, endpoint, params):
        """ Send request to Amap API
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

    def get_location_by_name(self, address, city_name):
        """ Get location by name
        Args:
            address: Name
            city_name: City name
        Returns:
            Location
        """
        result = self.geocode(address, city_name)
        if result.get('status') == '1' and result.get('geocodes'):
            geocodes = result.get('geocodes')
            if geocodes and len(geocodes) > 0:
                return geocodes[0].get('location')
        return None

    def get_city_code(self, city_name):
        """ Get city code
        Args:
            city_name: City name
        Returns:
            City code
        """
        params = {
            'keywords': city_name,
            'subdistrict': '0',
            'extensions': 'base'
        }
        result = self._send_request('config/district', params)
        if result.get('status') == '1' and result.get('districts'):
            districts = result.get('districts')
            if districts and len(districts) > 0:
                return districts[0].get('adcode')
        return None

    def geocode(self, address, city):
        """ Get Amap code
        Args:
            address: Address
            city: City
        Returns:
            Amap code
        """
        params = {
            'address': address
        }
        if city:
            params['city'] = city
        return self._send_request('geocode/geo', params)

    def reverse_geocode(self, location):
        """ Get reverse geocode
        Args:
            location: Location
        Returns:
            Reverse geocode
        """
        params = {
            'location': location,
            'extensions': 'all'
        }
        return self._send_request('geocode/regeo', params)

    def get_weather_by_city_name(self, city_name, extensions='base'):
        """ Get weather by city name
        Args:
            city_name: City name
            extensions: Extensions
        Returns:
            Weather
        """
        city_code = self.get_city_code(city_name)
        if city_code:
            return self.weather(city_code, extensions)
        else:
            return {"status": "0", "info": "City code not found"}

    def weather(self, city_code, extensions='base'):
        """ Get weather
        Args:
            city_code: City code
            extensions: Extensions
        Returns:
            Weather
        """
        params = {
            'city': city_code,
            'extensions': extensions
        }
        return self._send_request('weather/weatherInfo', params)

    def plan_route_by_name(self,
                           origin_name,
                           destination_name,
                           city_name,
                           mode,
                           waypoints,
                           strategy):
        """ Get route planning by name
        Args:
            origin_name: Startpoint name
            destination_name: Endpoint name
            city_name: City name
            mode: Travel modes, optional values: driving, walking, cycling, transit
            waypoints: The latitude and longitude of the passing point are in the format of "longitude1, latitude1; longitude2, latitude2" and can be selected
            strategy: Path planning strategy, only effective when driving, 0-9 different strategies
        Returns:
            Route planning
        """
        origin_location = self.get_location_by_name(origin_name, city_name)
        if not origin_location:
            return {"status": "0", "info": "Origin not found"}

        destination_location = self.get_location_by_name(destination_name, city_name)
        if not destination_location:
            return {"status": "0", "info": "Destination not found"}

        waypoints_location = None
        if waypoints:
            if isinstance(waypoints, list):
                waypoints_locations = []
                for waypoint in waypoints:
                    location = self.get_location_by_name(waypoint, city_name)
                    if location:
                        waypoints_locations.append(location)
                if waypoints_locations:
                    waypoints_location = ";".join(waypoints_locations)
            else:
                waypoints_location = self.get_location_by_name(waypoints, city_name)

        return self.route_planning(
            origin=origin_location,
            destination=destination_location,
            mode=mode,
            waypoints=waypoints_location,
            strategy=strategy
        )

    def route_planning(self,
                       origin,
                       destination,
                       mode,
                       waypoints,
                       strategy):
        """ Get route planning
        Args:
            origin: Startpoint latitude and longitude, in the format of "longitude, latitude"
            destination: Endpoint latitude and longitude, in the format of "longitude, latitude"
            mode: Travel modes, optional values: driving, walking, cycling, transit
            waypoints: The latitude and longitude of the passing point are in the format of "longitude1, latitude1; longitude2, latitude2" and can be selected
            strategy: Path planning strategy, only effective when driving, 0-9 different strategies
        Returns:
            Route planning
        """
        params = {
            'origin': origin,
            'destination': destination,
            'strategy': strategy
        }

        if waypoints:
            params['waypoints'] = waypoints

        if mode == 'driving':
            endpoint = 'direction/driving'
        elif mode == 'walking':
            endpoint = 'direction/walking'
        elif mode == 'cycling':
            endpoint = 'direction/bicycling'
        elif mode == 'transit':
            endpoint = 'direction/transit/integrated'
        else:
            raise ValueError('Invalid mode: {mode}')

        return self._send_request(endpoint, params)

    def search_poi_by_name(self,
                           keywords,
                           poi_name,
                           city_name,
                           radius,
                           page,
                           offset):
        """ Get POI search by name
        Args:
            keywords: User interest keywords
            poi_name: POI name
            city_name: City name
            radius: Search radius, in meters
            page: Page
            offset: Offset
        Returns:
            POI search result
        """
        location = self.get_location_by_name(poi_name, city_name)
        if not location:
            return {"status": "0", "info": "POI not found"}
        city_code = None
        if city_name:
            city_code = self.get_city_code(city_name)

        return self.poi_search(
            keywords=keywords,
            types=None,
            city=city_code,
            location=location,
            radius=radius,
            page=page,
            offset=offset
        )

    def poi_search(self,
                   keywords,
                   types,
                   city,
                   location,
                   radius,
                   page=1,
                   offset=20):
        """ Get POI search
        Args:
            keywords: User interest keywords
            types: POI type
            city: City
            location: The latitude and longitude of the center point are in the format of "longitude, latitude"
            radius: Search radius, in meters
            page: Page
            offset: Offset
        Returns:
            POI search result
        """
        params = {
            page: page,
            offset: offset,
        }

        if keywords:
            params['keywords'] = keywords
        if types:
            params['types'] = types
        if city:
            params['city'] = city
        if location:
            params['location'] = location
            params['radius'] = radius
        return self._send_request('place/text', params)

    def distance(self,
                origins,
                destinations,
                type):
        """ Get distance
        Args:
            origins: Startpoint latitude and longitude, in the format of "longitude, latitude"
            destinations: Endpoint latitude and longitude, in the format of "longitude, latitude"
            type: Distance calculation mode, 0-1, 0: driving distance, 1: walking distance
        Returns:
            Distance
        """
        params = {
            'origins': origins,
            'destination': destinations,
            'type': type
        }
        return self._send_request('distance', params)