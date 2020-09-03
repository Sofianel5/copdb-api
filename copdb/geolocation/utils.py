from django.contrib.gis.geoip2 import GeoIP2
from .models import Coordinates
import math  
from django.core.exceptions import PermissionDenied
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="falah")

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def getCoordinatesFromRequest(request):
    ip = get_client_ip(request)
    g = GeoIP2()
    lat, lng = g.lat_lon(ip)
    coordinates, _ = Coordinates.objects.get_or_create(lat=lat, lng=lng)
    return coordinates

def distanceInMetersFromCoordinates(lat1, lat2, lng1, lng2):
    lat1 = lat1 * math.pi / 180
    lat2 = lat2 * math.pi / 180
    lng1 = lng1 * math.pi / 180
    lng2 = lng2 * math.pi / 180
    dlng = abs(lng1 - lng2)
    dlat = abs(lat1 - lat2)
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    R = 6371000
    return R * c