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

    def get_location_by_name(self, address, city_name):
        """ Get location by name

        Get geocode based on address name.

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

        Gets the geocode of the city. if u need all info, set param "extensions" to 'all'

        Args:
            city_name: City name
        Returns:
            City code
        """
        params = {
            'keywords': city_name,
            'subdistrict': '0',
            'extensions': 'base' # Note, if u need all info, set param "extensions" to 'all'
        }
        result = self._send_request('config/district', params)
        if result.get('status') == '1' and result.get('districts'):
            districts = result.get('districts')
            if districts and len(districts) > 0:
                return districts[0].get('adcode')
        return None

    def geocode(self, address, city):
        """ Get Amap code

        Get the geocode of the landmark.

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

        Get geocode based on location name.

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

        Use the city name to get the local weather.

        Args:
            city_name: City name
            extensions: Extensions
        Returns:
            Weather
        """
        city_code = self.get_city_code(city_name)
        if city_code:
            return self.get_weather(city_code, extensions)
        else:
            return {"status": "0", "info": "City code not found"}

    def get_weather(self, city_code, extensions='base'):
        """ Get weather

        Use the city code to get the local weather.

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

        Plan paths based on start and end names.

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

        Plan a path based on the latitude and longitude of the start and end points.

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

        Search POIs by POI code

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
            'page': page,
            'offset': offset,
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

    def get_attractions(self, city_name, keywords=None, location=None, radius=3000, page=1, offset=20):
        """ Get attractions
        Args:
            city_name: City name
            keywords: User interest keywords
            location: The latitude and longitude of the center point are in the format of "longitude, latitude"
            radius: Search radius, in meters
            page: Page
            offset: Offset
        Returns:
            Attractions
        """
        if not city_name:
            return {"status": "0", "info": "City name is required"}

        city_code = self.get_city_code(city_name)
        if not city_code:
            return {"status": "0", "info": f"City code not found for {city_name}"}

        attraction_types = "110200,110201,110202,110203,110204,110205,110206,110207,110208"

        params = {
            'keywords': '景点',
            'types': attraction_types,
            'city': city_code,
            'page': page,
            'offset': offset,
            'extensions': 'all'
        }

        if keywords:
            params['keywords'] = keywords

        if location:
            params['location'] = location
            params['radius'] = radius

        result = self._send_request('place/text', params)

        if result.get('status') == '1' and result.get('pois'):
            attractions = []
            for poi in result.get('pois'):
                attraction = {
                    'name': poi.get('name'),
                    'location': poi.get('location'),
                    'address': poi.get('address'),
                    'rating': poi.get('biz_ext', {}).get('rating'),
                    'price': poi.get('biz_ext', {}).get('cost'),
                    'opening_hours': poi.get('business_area') or poi.get('biz_ext', {}).get('open_time'),
                    'recommended_duration': None,  # No Data from Amap
                    'photos': poi.get('photos'),
                    'tel': poi.get('tel'),
                    'type': poi.get('type')
                }
                attractions.append(attraction)
            return {'status': '1', 'attractions': attractions, 'count': len(attractions)}
        return result

    def get_hotels(self, city_name, keywords=None, location=None, radius=3000, page=1, offset=20):
        """ Get hotels information
        Args:
            city_name: City name
            keywords: Keywords for specific hotels
            location: Center location for search
            radius: Search radius in meters
            page: Page number
            offset: Results per page
        Returns:
            Hotels information including name, location, price, star rating, facilities, rating
        """
        # 确保城市名称有效
        if not city_name:
            return {"status": "0", "info": "City name is required"}
            
        # 获取城市编码
        city_code = self.get_city_code(city_name)
        if not city_code:
            return {"status": "0", "info": f"City code not found for {city_name}"}

        # 酒店类型编码 - 使用更精确的POI分类编码
        # 100000表示旅馆，100100表示宾馆酒店，100101表示五星级宾馆，100102表示四星级宾馆，100103表示三星级宾馆
        # 100104表示经济型连锁酒店，100105表示公寓式酒店，100200表示旅馆招待所，100201表示青年旅社
        hotel_types = "100000,100100,100101,100102,100103,100104,100105,100200,100201"

        # 构建基本参数
        params = {
            'types': hotel_types,
            'city': city_code,
            'page': page,
            'offset': offset,
            'extensions': 'all',
            'output': 'json'
        }

        # 添加关键词参数
        if keywords:
            params['keywords'] = keywords
        else:
            params['keywords'] = "酒店"  # 默认关键词
            
        # 添加位置参数
        if location:
            params['location'] = location
            params['radius'] = radius

        # 发送请求
        result = self._send_request('place/text', params)
        
        # 打印调试信息
        print(f"Hotel search params: {params}")
        print(f"Hotel search raw result status: {result.get('status')}, count: {result.get('count')}")

        # 处理结果
        if result.get('status') == '1' and result.get('pois'):
            hotels = []
            for poi in result.get('pois'):
                hotel = {
                    'name': poi.get('name'),
                    'location': poi.get('location'),
                    'address': poi.get('address'),
                    'rating': poi.get('biz_ext', {}).get('rating'),
                    'price': poi.get('biz_ext', {}).get('cost'),
                    'star_rating': poi.get('biz_ext', {}).get('rating_star') or poi.get('biz_ext', {}).get('star'),
                    'facilities': poi.get('biz_ext', {}).get('facilities'),
                    'photos': poi.get('photos'),
                    'tel': poi.get('tel'),
                    'type': poi.get('type')
                }
                hotels.append(hotel)
            return {'status': '1', 'hotels': hotels, 'count': len(hotels)}
        
        # 返回原始结果，便于调试
        return result

    def get_restaurants(self, city_name, keywords=None, cuisine_type=None, location=None, radius=3000, page=1, offset=20):
        """ Get restaurants information
        Args:
            city_name: City name
            keywords: Keywords for specific restaurants
            cuisine_type: Type of cuisine
            location: Center location for search
            radius: Search radius in meters
            page: Page number
            offset: Results per page
        Returns:
            Restaurants information including name, location, price range, cuisine type, rating, signature dishes
        """
        # 确保城市名称有效
        if not city_name:
            return {"status": "0", "info": "City name is required"}
            
        # 获取城市编码
        city_code = self.get_city_code(city_name)
        if not city_code:
            return {"status": "0", "info": f"City code not found for {city_name}"}

        # 餐饮类型编码 - 使用更精确的POI分类编码
        # 050000表示餐饮服务，050100表示中餐厅，050200表示外国餐厅
        restaurant_types = "050000,050100,050101,050102,050103,050104," + \
                          "050105,050106,050107,050108,050109,050110," + \
                          "050111,050112,050113,050114,050115,050116," + \
                          "050117,050118,050119,050120,050121,050122," + \
                          "050123,050200,050201,050202,050203,050204," + \
                          "050205,050206,050207,050208,050209,050210," + \
                          "050211,050212,050213,050214,050215"

        # 构建基本参数
        params = {
            'types': restaurant_types,
            'city': city_code,
            'page': page,
            'offset': offset,
            'extensions': 'all',
            'output': 'json'
        }

        # 处理关键词和菜系类型
        search_keywords = []
        if keywords:
            search_keywords.append(keywords)
        if cuisine_type:
            search_keywords.append(cuisine_type)
        
        if search_keywords:
            params['keywords'] = " ".join(search_keywords)
        else:
            params['keywords'] = "餐厅"  # 默认关键词
            
        # 添加位置参数
        if location:
            params['location'] = location
            params['radius'] = radius

        # 发送请求
        result = self._send_request('place/text', params)
        
        # 打印调试信息
        print(f"Restaurant search params: {params}")
        print(f"Restaurant search raw result status: {result.get('status')}, count: {result.get('count')}")

        # 处理结果
        if result.get('status') == '1' and result.get('pois'):
            restaurants = []
            for poi in result.get('pois'):
                # 提取营业时间信息
                opening_hours = None
                if poi.get('biz_ext', {}).get('open_time'):
                    opening_hours = poi.get('biz_ext', {}).get('open_time')
                elif poi.get('business_area'):
                    opening_hours = poi.get('business_area')
                
                # 提取菜系类型
                cuisine = None
                if poi.get('type'):
                    type_parts = poi.get('type').split(';')
                    if len(type_parts) > 1:
                        cuisine = type_parts[-1]
                
                restaurant = {
                    'name': poi.get('name'),
                    'location': poi.get('location'),
                    'address': poi.get('address'),
                    'rating': poi.get('biz_ext', {}).get('rating'),
                    'price_range': poi.get('biz_ext', {}).get('cost'),
                    'cuisine_type': cuisine,
                    'opening_hours': opening_hours,
                    'signature_dishes': None,  # 高德API不提供招牌菜信息
                    'photos': poi.get('photos'),
                    'tel': poi.get('tel'),
                    'type': poi.get('type'),
                    'tag': poi.get('tag') if 'tag' in poi else None,  # 添加标签信息
                    'distance': poi.get('distance') if 'distance' in poi else None  # 添加距离信息
                }
                restaurants.append(restaurant)
            return {'status': '1', 'restaurants': restaurants, 'count': len(restaurants)}
        
        # 返回原始结果，便于调试
        return result

    def get_transportation_between(self, origin_city, destination_city, departure_time=None, transportation_type='integrated'):
        """ Get transportation information between two cities
        Args:
            origin_city: Origin city name
            destination_city: Destination city name
            departure_time: Departure time in format 'YYYY-MM-DD HH:MM:SS'
            transportation_type: Type of transportation ('integrated', 'bus', 'driving', 'walking', 'cycling', 'train')
        Returns:
            Transportation information including mode, departure/arrival time, price, duration, ticket status
        """
        # 确保城市名称有效
        if not origin_city or not destination_city:
            return {"status": "0", "info": "Origin and destination city names are required"}
            
        # 获取城市编码
        origin_city_code = self.get_city_code(origin_city)
        destination_city_code = self.get_city_code(destination_city)

        if not origin_city_code or not destination_city_code:
            return {"status": "0", "info": f"City code not found for {origin_city} or {destination_city}"}

        # 获取城市中心点位置
        origin_location = self.get_location_by_name(origin_city, None)
        destination_location = self.get_location_by_name(destination_city, None)
        
        # 如果无法获取位置，使用默认坐标
        if not origin_location:
            if origin_city in ["北京", "北京市"]:
                origin_location = "116.407526,39.904030"  # 天安门坐标
            elif origin_city in ["上海", "上海市"]:
                origin_location = "121.473667,31.230525"  # 人民广场坐标
            elif origin_city in ["广州", "广州市"]:
                origin_location = "113.264385,23.129112"  # 广州塔坐标
            elif origin_city in ["深圳", "深圳市"]:
                origin_location = "114.057868,22.543099"  # 深圳市民中心坐标
            else:
                return {"status": "0", "info": f"Cannot get location for {origin_city}"}
                
        if not destination_location:
            if destination_city in ["北京", "北京市"]:
                destination_location = "116.407526,39.904030"  # 天安门坐标
            elif destination_city in ["上海", "上海市"]:
                destination_location = "121.473667,31.230525"  # 人民广场坐标
            elif destination_city in ["广州", "广州市"]:
                destination_location = "113.264385,23.129112"  # 广州塔坐标
            elif destination_city in ["深圳", "深圳市"]:
                destination_location = "114.057868,22.543099"  # 深圳市民中心坐标
            else:
                return {"status": "0", "info": f"Cannot get location for {destination_city}"}
        
        # 如果是同一个城市，使用不同的起终点位置
        if origin_city == destination_city:
            if origin_city in ["北京", "北京市"]:
                origin_location = "116.407526,39.904030"  # 天安门坐标
                destination_location = "116.310316,39.993260"  # 北京大学坐标
            elif origin_city in ["上海", "上海市"]:
                origin_location = "121.473667,31.230525"  # 人民广场坐标
                destination_location = "121.501654,31.239149"  # 陆家嘴坐标
        
        # 判断是否跨城市
        is_cross_city = origin_city_code != destination_city_code
        
        # 打印调试信息
        print(f"Transportation search: {origin_city}({origin_city_code}) to {destination_city}({destination_city_code})")
        print(f"Origin location: {origin_location}, Destination location: {destination_location}")
        print(f"Is cross city: {is_cross_city}, Transportation type: {transportation_type}")
            
        if transportation_type in ['integrated', 'bus']:
            # 公交/综合路线规划，仅限同城
            if is_cross_city:
                return {"status": "0", "info": "Integrated/bus mode only supports travel within the same city"}
                
            params = {
                'origin': origin_location,
                'destination': destination_location,
                'city': origin_city_code,
                'extensions': 'all',
                'output': 'json'
            }
            
            if departure_time:
                params['time'] = departure_time
                
            endpoint = 'direction/transit/integrated'
            if transportation_type == 'bus':
                # 使用公交规划API
                endpoint = 'direction/transit/integrated'
                
            result = self._send_request(endpoint, params)
            
            # 打印调试信息
            print(f"Transit search params: {params}")
            print(f"Transit search result status: {result.get('status')}")
            
            # 处理结果
            if result.get('status') == '1' and result.get('route'):
                transits = []
                for transit in result.get('route', {}).get('transits', []):
                    segments = transit.get('segments', [])
                    transport_info = {
                        'type': transportation_type,
                        'departure_time': transit.get('departure_time'),
                        'arrival_time': transit.get('arrival_time'),
                        'duration': transit.get('duration'),
                        'walking_distance': transit.get('walking_distance'),
                        'cost': transit.get('cost'),
                        'distance': transit.get('distance'),
                        'segments': []
                    }
                    
                    for segment in segments:
                        walking = segment.get('walking')
                        bus = segment.get('bus')
                        railway = segment.get('railway')
                        taxi = segment.get('taxi')
                        
                        segment_info = {
                            'mode': None,
                            'line': None,
                            'departure': None,
                            'arrival': None,
                            'duration': segment.get('duration'),
                            'distance': segment.get('distance')
                        }
                        
                        if walking:
                            segment_info['mode'] = 'walking'
                            segment_info['distance'] = walking.get('distance')
                            segment_info['duration'] = walking.get('duration')
                            
                        elif bus:
                            segment_info['mode'] = 'bus'
                            segment_info['line'] = bus.get('buslines', [{}])[0].get('name')
                            segment_info['departure'] = bus.get('buslines', [{}])[0].get('departure_stop', {}).get('name')
                            segment_info['arrival'] = bus.get('buslines', [{}])[0].get('arrival_stop', {}).get('name')
                            segment_info['duration'] = bus.get('buslines', [{}])[0].get('duration')
                            
                        elif railway:
                            segment_info['mode'] = 'subway'
                            segment_info['line'] = railway.get('name')
                            segment_info['departure'] = railway.get('departure_stop', {}).get('name')
                            segment_info['arrival'] = railway.get('arrival_stop', {}).get('name')
                            segment_info['duration'] = railway.get('duration')
                            
                        elif taxi:
                            segment_info['mode'] = 'taxi'
                            segment_info['distance'] = taxi.get('distance')
                            segment_info['duration'] = taxi.get('duration')
                            segment_info['cost'] = taxi.get('cost')
                        
                        transport_info['segments'].append(segment_info)
                    
                    transits.append(transport_info)
                
                return {'status': '1', 'transits': transits, 'count': len(transits)}
            
            # 返回原始结果，便于调试
            return result
        
        elif transportation_type in ['walking', 'cycling']:
            # 步行和骑行模式，仅限同城
            if is_cross_city:
                return {"status": "0", "info": f"{transportation_type} mode only supports travel within the same city"}
                
            result = self.route_planning(
                origin=origin_location,
                destination=destination_location,
                mode=transportation_type,
                waypoints=None,
                strategy=0
            )
            
            # 处理结果为统一格式
            if result.get('status') == '1' and result.get('route'):
                paths = result.get('route', {}).get('paths', [])
                if paths:
                    transits = []
                    for path in paths:
                        transport_info = {
                            'type': transportation_type,
                            'duration': path.get('duration'),
                            'distance': path.get('distance'),
                            'tolls': path.get('tolls', 0),
                            'toll_distance': path.get('toll_distance', 0),
                            'segments': []
                        }
                        
                        # 添加路段信息
                        for step in path.get('steps', []):
                            segment_info = {
                                'mode': transportation_type,
                                'instruction': step.get('instruction'),
                                'road_name': step.get('road_name'),
                                'duration': step.get('duration'),
                                'distance': step.get('distance')
                            }
                            transport_info['segments'].append(segment_info)
                        
                        transits.append(transport_info)
                    
                    return {'status': '1', 'transits': transits, 'count': len(transits)}
            
            # 返回原始结果
            return result
            
        elif transportation_type == 'driving':
            # 驾车模式，支持跨城市
            result = self.route_planning(
                origin=origin_location,
                destination=destination_location,
                mode=transportation_type,
                waypoints=None,
                strategy=0
            )
            
            # 处理结果为统一格式
            if result.get('status') == '1' and result.get('route'):
                paths = result.get('route', {}).get('paths', [])
                if paths:
                    transits = []
                    for path in paths:
                        transport_info = {
                            'type': 'driving',
                            'duration': path.get('duration'),
                            'distance': path.get('distance'),
                            'tolls': path.get('tolls', 0),
                            'toll_distance': path.get('toll_distance', 0),
                            'traffic_lights': path.get('traffic_lights', 0),
                            'segments': []
                        }
                        
                        # 添加路段信息
                        for step in path.get('steps', []):
                            segment_info = {
                                'mode': 'driving',
                                'instruction': step.get('instruction'),
                                'road_name': step.get('road_name'),
                                'duration': step.get('duration'),
                                'distance': step.get('distance'),
                                'tolls': step.get('tolls', 0),
                                'toll_distance': step.get('toll_distance', 0),
                                'toll_road': step.get('toll_road', False)
                            }
                            transport_info['segments'].append(segment_info)
                        
                        transits.append(transport_info)
                    
                    return {'status': '1', 'transits': transits, 'count': len(transits)}
            
            # 返回原始结果
            return result
        
        return {"status": "0", "info": f"Unsupported transportation type: {transportation_type}"}

    def get_transportation_between(self, origin, destination, city=None, departure_time=None, strategy=0):
        """ 获取两地之间的交通方案
        
        根据起点和终点提供交通方案。如果是跨城市，则只提供驾车方案；
        如果是同城市，则提供驾车、公交、步行和骑行四种方案。
        
        Args:
            origin: 起点，可以是地点名称或经纬度坐标（格式："经度,纬度"）
            destination: 终点，可以是地点名称或经纬度坐标（格式："经度,纬度"）
            city: 城市名称，当使用地点名称作为起终点时需要提供
            departure_time: 出发时间，格式为"YYYY-MM-DD HH:MM:SS"，仅对公交规划有效
            strategy: 路径规划策略，对驾车规划有效，0-9不同策略
            
        Returns:
            包含各种交通方案的字典，格式为：
            {
                "status": "1",
                "is_same_city": True/False,
                "plans": {
                    "driving": {...},  # 驾车方案
                    "transit": {...},  # 公交方案（仅同城）
                    "walking": {...},  # 步行方案（仅同城）
                    "cycling": {...}   # 骑行方案（仅同城）
                }
            }
        """
        # 初始化结果
        result = {
            "status": "1",
            "is_same_city": False,
            "plans": {}
        }
        
        # 处理起点和终点
        origin_location, origin_city_code = self._process_location(origin, city)
        destination_location, destination_city_code = self._process_location(destination, city)
        
        # 检查起点和终点是否有效
        if not origin_location or not destination_location:
            return {
                "status": "0", 
                "info": "无法获取起点或终点的位置信息"
            }
            
        # 判断是否同城
        is_same_city = origin_city_code == destination_city_code and origin_city_code is not None
        result["is_same_city"] = is_same_city
        
        # 打印调试信息
        print(f"交通规划: 从 {origin}({origin_city_code}) 到 {destination}({destination_city_code})")
        print(f"起点坐标: {origin_location}, 终点坐标: {destination_location}")
        print(f"是否同城: {is_same_city}")
        
        # 获取驾车方案（无论是否同城）
        driving_plan = self._get_driving_plan(origin_location, destination_location, strategy)
        if driving_plan.get("status") == "1":
            result["plans"]["driving"] = driving_plan
        
        # 如果是同城，获取其他交通方案
        if is_same_city:
            # 获取公交方案
            transit_plan = self._get_transit_plan(origin_location, destination_location, origin_city_code, departure_time)
            if transit_plan.get("status") == "1":
                result["plans"]["transit"] = transit_plan
            
            # 获取步行方案
            walking_plan = self._get_walking_plan(origin_location, destination_location)
            if walking_plan.get("status") == "1":
                result["plans"]["walking"] = walking_plan
            
            # 获取骑行方案
            cycling_plan = self._get_cycling_plan(origin_location, destination_location)
            if cycling_plan.get("status") == "1":
                result["plans"]["cycling"] = cycling_plan
        
        return result
    
    def _process_location(self, location, city=None):
        """处理位置信息，返回坐标和城市编码
        
        Args:
            location: 位置信息，可以是地点名称或坐标
            city: 城市名称，当location是地点名称时需要提供
            
        Returns:
            tuple: (坐标, 城市编码)
        """
        # 检查是否已经是坐标格式（经度,纬度）
        if isinstance(location, str) and "," in location and all(part.replace('.', '').isdigit() for part in location.split(',')):
            # 已经是坐标，通过逆地理编码获取城市编码
            result = self.reverse_geocode(location)
            if result.get("status") == "1" and result.get("regeocode"):
                address_component = result.get("regeocode", {}).get("addressComponent", {})
                city_code = address_component.get("adcode")
                return location, city_code
            return location, None
        
        # 是地点名称，需要地理编码
        location_coord = self.get_location_by_name(location, city)
        city_code = None
        
        # 如果提供了城市名称，获取城市编码
        if city:
            city_code = self.get_city_code(city)
        
        # 如果无法获取坐标，尝试使用预设的城市坐标
        if not location_coord:
            location_coord, city_code = self._get_preset_location(location)
        
        return location_coord, city_code
    
    def _get_preset_location(self, location):
        """获取预设的位置坐标和城市编码
        
        Args:
            location: 位置名称
            
        Returns:
            tuple: (坐标, 城市编码)
        """
        # 常用城市中心点坐标
        preset_locations = {
            "北京": ("116.407526,39.904030", "110000"),  # 天安门
            "北京市": ("116.407526,39.904030", "110000"),
            "上海": ("121.473667,31.230525", "310000"),  # 人民广场
            "上海市": ("121.473667,31.230525", "310000"),
            "广州": ("113.264385,23.129112", "440100"),  # 广州塔
            "广州市": ("113.264385,23.129112", "440100"),
            "深圳": ("114.057868,22.543099", "440300"),  # 市民中心
            "深圳市": ("114.057868,22.543099", "440300"),
            "杭州": ("120.155070,30.274084", "330100"),  # 西湖
            "杭州市": ("120.155070,30.274084", "330100"),
            "南京": ("118.796877,32.060255", "320100"),  # 新街口
            "南京市": ("118.796877,32.060255", "320100"),
            "成都": ("104.065735,30.659462", "510100"),  # 天府广场
            "成都市": ("104.065735,30.659462", "510100"),
            "重庆": ("106.551556,29.563009", "500000"),  # 解放碑
            "重庆市": ("106.551556,29.563009", "500000"),
            "武汉": ("114.298572,30.584355", "420100"),  # 黄鹤楼
            "武汉市": ("114.298572,30.584355", "420100"),
            "西安": ("108.946609,34.347269", "610100"),  # 钟楼
            "西安市": ("108.946609,34.347269", "610100"),
            "天津": ("117.190182,39.125596", "120000"),  # 天津之眼
            "天津市": ("117.190182,39.125596", "120000"),
            # 可以根据需要添加更多城市
        }
        
        # 常用地标坐标
        preset_landmarks = {
            "北京大学": ("116.310316,39.993260", "110000"),
            "清华大学": ("116.326343,40.002029", "110000"),
            "故宫": ("116.397026,39.918058", "110000"),
            "天安门": ("116.407526,39.904030", "110000"),
            "上海外滩": ("121.490317,31.236305", "310000"),
            "东方明珠": ("121.499705,31.239702", "310000"),
            "陆家嘴": ("121.501654,31.239149", "310000"),
            "西湖": ("120.143352,30.236821", "330100"),
            # 可以根据需要添加更多地标
        }
        
        # 先检查是否是预设的城市
        if location in preset_locations:
            return preset_locations[location]
        
        # 再检查是否是预设的地标
        if location in preset_landmarks:
            return preset_landmarks[location]
        
        return None, None
    
    def _get_driving_plan(self, origin, destination, strategy=0):
        """获取驾车规划方案
        
        Args:
            origin: 起点坐标
            destination: 终点坐标
            strategy: 路径规划策略，0-9不同策略
            
        Returns:
            驾车规划方案
        """
        result = self.route_planning(
            origin=origin,
            destination=destination,
            mode="driving",
            waypoints=None,
            strategy=strategy
        )
        
        # 处理结果为统一格式
        if result.get('status') == '1' and result.get('route'):
            paths = result.get('route', {}).get('paths', [])
            if paths:
                routes = []
                for path in paths:
                    route_info = {
                        'duration': path.get('duration'),  # 行驶时间，单位：秒
                        'distance': path.get('distance'),  # 行驶距离，单位：米
                        'tolls': path.get('tolls', 0),     # 道路收费，单位：元
                        'toll_distance': path.get('toll_distance', 0),  # 收费道路距离，单位：米
                        'traffic_lights': path.get('traffic_lights', 0),  # 红绿灯数量
                        'steps': []
                    }
                    
                    # 添加路段信息
                    for step in path.get('steps', []):
                        step_info = {
                            'instruction': step.get('instruction'),  # 行驶指示
                            'road_name': step.get('road_name'),      # 道路名称
                            'duration': step.get('duration'),        # 此段行驶时间
                            'distance': step.get('distance'),        # 此段行驶距离
                            'tolls': step.get('tolls', 0),           # 此段道路收费
                            'toll_distance': step.get('toll_distance', 0),  # 此段收费道路距离
                            'toll_road': step.get('toll_road', False)  # 是否收费道路
                        }
                        route_info['steps'].append(step_info)
                    
                    routes.append(route_info)
                
                return {'status': '1', 'routes': routes, 'count': len(routes)}
        
        # 返回原始结果
        return result
    
    def _get_transit_plan(self, origin, destination, city_code, departure_time=None):
        """获取公交规划方案
        
        Args:
            origin: 起点坐标
            destination: 终点坐标
            city_code: 城市编码
            departure_time: 出发时间，格式为"YYYY-MM-DD HH:MM:SS"
            
        Returns:
            公交规划方案
        """
        params = {
            'origin': origin,
            'destination': destination,
            'city': city_code,
            'extensions': 'all',
            'output': 'json'
        }
        
        if departure_time:
            params['time'] = departure_time
            
        result = self._send_request('direction/transit/integrated', params)
        
        # 打印调试信息
        print(f"公交搜索参数: {params}")
        print(f"公交搜索结果状态: {result.get('status')}")
        
        # 处理结果
        if result.get('status') == '1' and result.get('route'):
            transits = []
            for transit in result.get('route', {}).get('transits', []):
                segments = transit.get('segments', [])
                transit_info = {
                    'departure_time': transit.get('departure_time'),  # 出发时间
                    'arrival_time': transit.get('arrival_time'),      # 到达时间
                    'duration': transit.get('duration'),              # 行程总时间，单位：秒
                    'walking_distance': transit.get('walking_distance'),  # 步行距离，单位：米
                    'cost': transit.get('cost'),                      # 费用，单位：元
                    'distance': transit.get('distance'),              # 行程总距离，单位：米
                    'segments': []
                }
                
                for segment in segments:
                    walking = segment.get('walking')
                    bus = segment.get('bus')
                    railway = segment.get('railway')
                    taxi = segment.get('taxi')
                    
                    segment_info = {
                        'mode': None,
                        'line': None,
                        'departure': None,
                        'arrival': None,
                        'duration': segment.get('duration'),
                        'distance': segment.get('distance')
                    }
                    
                    if walking:
                        segment_info['mode'] = 'walking'
                        segment_info['distance'] = walking.get('distance')
                        segment_info['duration'] = walking.get('duration')
                        
                    elif bus:
                        segment_info['mode'] = 'bus'
                        segment_info['line'] = bus.get('buslines', [{}])[0].get('name')
                        segment_info['departure'] = bus.get('buslines', [{}])[0].get('departure_stop', {}).get('name')
                        segment_info['arrival'] = bus.get('buslines', [{}])[0].get('arrival_stop', {}).get('name')
                        segment_info['duration'] = bus.get('buslines', [{}])[0].get('duration')
                        
                    elif railway:
                        segment_info['mode'] = 'subway'
                        segment_info['line'] = railway.get('name')
                        segment_info['departure'] = railway.get('departure_stop', {}).get('name')
                        segment_info['arrival'] = railway.get('arrival_stop', {}).get('name')
                        segment_info['duration'] = railway.get('duration')
                        
                    elif taxi:
                        segment_info['mode'] = 'taxi'
                        segment_info['distance'] = taxi.get('distance')
                        segment_info['duration'] = taxi.get('duration')
                        segment_info['cost'] = taxi.get('cost')
                    
                    transit_info['segments'].append(segment_info)
                
                transits.append(transit_info)
            
            return {'status': '1', 'routes': transits, 'count': len(transits)}
        
        # 返回原始结果
        return result
    
    def _get_walking_plan(self, origin, destination):
        """获取步行规划方案
        
        Args:
            origin: 起点坐标
            destination: 终点坐标
            
        Returns:
            步行规划方案
        """
        result = self.route_planning(
            origin=origin,
            destination=destination,
            mode="walking",
            waypoints=None,
            strategy=0
        )
        
        # 处理结果为统一格式
        if result.get('status') == '1' and result.get('route'):
            paths = result.get('route', {}).get('paths', [])
            if paths:
                routes = []
                for path in paths:
                    route_info = {
                        'duration': path.get('duration'),  # 步行时间，单位：秒
                        'distance': path.get('distance'),  # 步行距离，单位：米
                        'steps': []
                    }
                    
                    # 添加路段信息
                    for step in path.get('steps', []):
                        step_info = {
                            'instruction': step.get('instruction'),  # 行走指示
                            'road_name': step.get('road_name'),      # 道路名称
                            'duration': step.get('duration'),        # 此段步行时间
                            'distance': step.get('distance'),        # 此段步行距离
                            'direction': step.get('orientation')     # 行走方向
                        }
                        route_info['steps'].append(step_info)
                    
                    routes.append(route_info)
                
                return {'status': '1', 'routes': routes, 'count': len(routes)}
        
        # 返回原始结果
        return result
    
    def _get_cycling_plan(self, origin, destination):
        """获取骑行规划方案
        
        Args:
            origin: 起点坐标
            destination: 终点坐标
            
        Returns:
            骑行规划方案
        """
        result = self.route_planning(
            origin=origin,
            destination=destination,
            mode="cycling",
            waypoints=None,
            strategy=0
        )
        
        # 处理结果为统一格式
        if result.get('status') == '1' and result.get('route'):
            paths = result.get('route', {}).get('paths', [])
            if paths:
                routes = []
                for path in paths:
                    route_info = {
                        'duration': path.get('duration'),  # 骑行时间，单位：秒
                        'distance': path.get('distance'),  # 骑行距离，单位：米
                        'steps': []
                    }
                    
                    # 添加路段信息
                    for step in path.get('steps', []):
                        step_info = {
                            'instruction': step.get('instruction'),  # 骑行指示
                            'road_name': step.get('road_name'),      # 道路名称
                            'duration': step.get('duration'),        # 此段骑行时间
                            'distance': step.get('distance'),        # 此段骑行距离
                            'direction': step.get('orientation')     # 骑行方向
                        }
                        route_info['steps'].append(step_info)
                    
                    routes.append(route_info)
                
                return {'status': '1', 'routes': routes, 'count': len(routes)}
        
        # 返回原始结果
        return result
