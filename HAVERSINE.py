import math

#first we will convert the angle to radian 

def degree_to_radian(angle):
    return angle * (math.pi / 180)
# now we will implement the haversine formula to calculate the distance between two points on the earth's surface given their latitude and longitude
def haversine(lat1, lon1, lat2, lon2):
    earth_radius = 6371000 # in meters
    dlat = degree_to_radian(lat2 - lat1)
    dlon = degree_to_radian(lon2 - lon1)
    #  now we will calculate the distance using the haversine formula
    a = math.sin(dlat / 2) ** 2 + math.cos(degree_to_radian(lat1)) * math.cos(degree_to_radian(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = earth_radius * c
    return distance
# example usage berlin to munich
lat1 = 52.5200
lon1 = 13.4050
lat2 = 48.1351
lon2 = 11.5820
distance = haversine(lat1, lon1, lat2, lon2)
print(f"{distance/1000:.1f} km")  