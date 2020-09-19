from geolocation.models import Coordinates, Address
from geolocation.utils import getCoordinatesFromRequest
import logging
from .tasks import *
db_logger = logging.getLogger('db')

class Config():
    DEFAULT_COORDS = {'lat': 40.712776, 'lng': -74.005974}

def get_coordinates(request, fieldname="coordinates"):
    try:
        lat, lng = (request.META['HTTP_LAT'], request.META["HTTP_LNG"])
        assert(lat != "" and lng != "")
        coords, _ = Coordinates.objects.get_or_create(lat=lat, lng=lng)
        process_request_data.delay(request.META['HTTP_LAT'], request.META["HTTP_LNG"], request.user.id)
        return coords
    except Exception as e:
        db_logger.exception(e)
        try:
            return getCoordinatesFromRequest(request)
        except:
            coords, _ = Coordinates.objects.get_or_create(lat=Config.DEFAULT_COORDS['lat'], lng=Config.DEFAULT_COORDS['lng'])
            return coords

def _get_coordinates(request, fieldname="coordinates"):
    lat, lng = (request.META['HTTP_LAT'], request.META["HTTP_LNG"])
    coords, _ = Coordinates.objects.get_or_create(lat=lat, lng=lng)
    return coords

def update_location(user, coordinates):
    user.coordinates = coordinates 
    user.address = coordinates.to_address()
    user.save()
    return user

def supported_version(request):
    supported = ["0"]
    return request.META.get('HTTP_APP_VERSION') in supported