# -*- coding: utf-8 -*-
"""
@ Created on 2024-09-20 16:56
---------
@summary: 
---------
@author: XiaoBai
"""
import math
import typing
from shapely import wkt, Polygon, Point

from nbclass.typeshed import StrFloat

PI = 3.1415926535897932384626  # π
MAJOR_SEMI_AXIS = 6378245.0  # 长半轴(地球半径)
ECCENTRICITY = 0.00669342162296594323  # 偏心率平方
X_PI = 3.14159265358979324 * 3000.0 / 180.0
StrPolygon = typing.Union[str, Polygon, typing.List[tuple]]


def _transform_lat(lng: float, lat: float):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 *
            math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * PI) + 40.0 *
            math.sin(lat / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * PI) + 320 *
            math.sin(lat * PI / 30.0)) * 2.0 / 3.0
    return ret


# 变换经度
def _transform_lng(lng: float, lat: float):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 *
            math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * PI) + 40.0 *
            math.sin(lng / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * PI) + 300.0 *
            math.sin(lng / 30.0 * PI)) * 2.0 / 3.0
    return ret


def bd09_to_gcj02(lng: StrFloat, lat: StrFloat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    百度——>谷歌、高德
    :param lat:百度坐标纬度
    :param lng:百度坐标经度
    :return:转换后的坐标列表形式
    """
    lng = float(lng)
    lat = float(lat)

    x = lng - 0.0065
    y = lat - 0.006

    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * X_PI)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * X_PI)

    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)

    return gg_lng, gg_lat


def bd09_to_wgs84(lng: StrFloat, lat: StrFloat):
    lng, lat = bd09_to_gcj02(lng, lat)
    return gcj02_to_wgs84(lng, lat)


def compute_wkt_area(polygon: StrPolygon):
    """
    计算围栏面积
    :return：面积(单位:)
    """

    wkt1_polygon = normalizing_wkt(polygon)
    area = wkt1_polygon.area
    return area * 1000000


def compute_wkt_intersection(polygon1: StrPolygon, polygon2: StrPolygon):
    # todo：distance（最近距离）待完成
    """
    计算两个围栏是否有交集
    :wkt1 polygon((x,y x1,y1 x2,y2))
    :return  area（面积 单位：）
             state（是否相交）：1相交 0不相交
             distance（最近距离）： 未完成
    """

    wkt1_polygon = normalizing_wkt(polygon1)
    wkt2_polygon = normalizing_wkt(polygon2)

    area = wkt1_polygon.intersection(wkt2_polygon).area
    distance = wkt1_polygon.distance(wkt2_polygon)

    if area == 0:
        return 0, None, distance
    else:
        return 1, round(area, 10), round(distance, 10)


def compute_wkt_relation(polygon: StrPolygon, poi: typing.Union[list, tuple, Point]):
    """
    计算点与轮廓的关系
    :param polygon:
    :param poi:
    :return:
    """
    wkt1_polygon = normalizing_wkt(polygon)
    if not isinstance(poi, Point):
        poi = Point(poi)

    relation = wkt1_polygon.contains(poi)
    distance = wkt1_polygon.distance(poi)
    return relation, distance * 103.25


def coordinates_correct(lng: StrFloat, lat: StrFloat):
    """
    修正错乱的经纬度
    :return:
    """
    lng, lat = float(lng), float(lat)
    return (lng, lat) if lng > lat else (lat, lng)


def coordinates_distance(lng1: StrFloat, lat1: StrFloat, lng2: StrFloat, lat2: StrFloat):
    # 将经纬度转换为弧度
    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lng1))
    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lng2))

    # 应用 Haversine 公式计算距离
    d_lon = lon2 - lon1
    d_lat = lat2 - lat1
    a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return 6371 * c * 1000  # 地球平均半径，单位为公里


def gcj02_to_bd09(lng: StrFloat, lat: StrFloat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    谷歌、高德——>百度
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    lng = float(lng)
    lat = float(lat)

    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * X_PI)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * X_PI)

    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006

    return bd_lng, bd_lat


def gcj02_to_wgs84(lng: StrFloat, lat: StrFloat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    lng = float(lng)
    lat = float(lat)
    if out_of_china(lng, lat):
        return [lng, lat]

    d_lat = _transform_lat(lng - 105.0, lat - 35.0)
    d_lng = _transform_lng(lng - 105.0, lat - 35.0)

    rad_lat = lat / 180.0 * PI
    magic = math.sin(rad_lat)
    magic = 1 - ECCENTRICITY * magic * magic
    sqr_tmagic = math.sqrt(magic)

    d_lat = (d_lat * 180.0) / ((MAJOR_SEMI_AXIS * (1 - ECCENTRICITY)) / (magic * sqr_tmagic) * PI)
    d_lng = (d_lng * 180.0) / (MAJOR_SEMI_AXIS / sqr_tmagic * math.cos(rad_lat) * PI)

    mg_lat = lat + d_lat
    mg_lng = lng + d_lng

    return lng * 2 - mg_lng, lat * 2 - mg_lat


def normalizing_wkt(_wkt: StrPolygon) -> Polygon:
    """
    格式化围栏wkt
    1、含'POLYGON (('的数据直接返回
    2、判断围栏是否闭尾并返回格式化围栏 polygon((x,y x1,y1 x2,y2))
    """
    if isinstance(_wkt, Polygon):
        return _wkt

    if 'POLYGON ((' in _wkt:
        return wkt.loads(_wkt)

    if _wkt.split(',')[0] == _wkt.split(',')[-1]:
        new_wkt = 'POLYGON ((' + _wkt + '))'
    else:
        new_wkt = 'POLYGON ((' + _wkt + ',' + _wkt.split(',')[0] + '))'
    return wkt.loads(new_wkt)


def out_of_china(lng: float, lat: float):
    """ 判断是否在国内，不在国内不做偏移 """
    return not (73.66 < lng < 135.05 and 3.86 < lat < 53.55)


def wgs84_to_gcj02(lng: StrFloat, lat: StrFloat):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    lng = float(lng)
    lat = float(lat)
    if out_of_china(lng, lat):  # 判断是否在国内
        return [lng, lat]

    d_lat = _transform_lat(lng - 105.0, lat - 35.0)
    d_lng = _transform_lng(lng - 105.0, lat - 35.0)

    rad_lat = lat / 180.0 * PI
    magic = math.sin(rad_lat)
    magic = 1 - ECCENTRICITY * magic * magic
    sqr_tmagic = math.sqrt(magic)

    d_lat = (d_lat * 180.0) / ((MAJOR_SEMI_AXIS * (1 - ECCENTRICITY)) / (magic * sqr_tmagic) * PI)
    d_lng = (d_lng * 180.0) / (MAJOR_SEMI_AXIS / sqr_tmagic * math.cos(rad_lat) * PI)

    mg_lat = lat + d_lat
    mg_lng = lng + d_lng

    return mg_lng, mg_lat


def wgs84_to_bd09(lng: StrFloat, lat: StrFloat):
    lng, lat = wgs84_to_gcj02(lng, lat)
    return gcj02_to_bd09(lng, lat)
