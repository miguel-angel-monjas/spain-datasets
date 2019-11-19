#!/usr/bin/env python
# coding: utf-8

import pyproj

_projections = {}


def get_zone(coordinates):
    if 56 <= coordinates[1] < 64 and 3 <= coordinates[0] < 12:
        return 32
    if 72 <= coordinates[1] < 84 and 0 <= coordinates[0] < 42:
        if coordinates[0] < 9:
            return 31
        elif coordinates[0] < 21:
            return 33
        elif coordinates[0] < 33:
            return 35
        return 37
    return int((coordinates[0] + 180) / 6) + 1


def get_letter(coordinates):
    return 'CDEFGHJKLMNPQRSTUVWXX'[int((coordinates[1] + 80) / 8)]


def project(coordinates):
    utm_zone = get_zone(coordinates)
    utm_letter = get_letter(coordinates)
    if utm_zone not in _projections:
        _projections[utm_zone] = pyproj.Proj(proj='utm', zone=utm_zone, ellps='WGS84')
    x, y = _projections[utm_zone](coordinates[0], coordinates[1])
    if y < 0:
        y += 10000000
    return utm_zone, utm_letter, x, y


def unproject(zone, letter, x, y):
    if zone not in _projections:
        _projections[zone] = pyproj.Proj(proj='utm', zone=zone, ellps='WGS84')
    if letter < 'N':
        y -= 10000000
    lng, lat = _projections[zone](x, y, inverse=True)
    return lng, lat
