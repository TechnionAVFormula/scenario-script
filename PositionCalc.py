import math
import numpy as np
import matplotlib.pyplot as plt

R = 6378.137 * pow(10, 3) * 1.0 # Earth radius
ZeroLong = -116.94813653826716
ZeroLatitude = 41.71254903708573

def add_meters_to_lng(lng, lat, meters):
    return lng + (meters/R) * (180 / np.pi) / np.cos(lat * np.pi/180) 

def add_meters_to_lat(lat, meters):
    return lat + (meters/R) * (180 / np.pi)


