from django.db import models
from django.db import models
from django.utils.translation import ugettext_lazy as _
from localflavor.us.models import USZipCodeField
from localflavor.us.us_states import US_STATES
from django.conf import settings
import requests
import math
from timezonefinder import TimezoneFinder
import logging
db_logger = logging.getLogger('db')

# Create your models here.
class Coordinates(models.Model):
    lat = models.FloatField() 
    lng = models.FloatField() 
    def __str__(self):
        return "{'lat': " + str(self.lat) + ", 'lng': " + str(self.lng) + "}" 
    def distance(self, other):
        try:
            lat1 = float(self.lat) * math.pi / 180
            lat2 = float(other.lat) * math.pi / 180
            lng1 = float(self.lng) * math.pi / 180
            lng2 = float(other.lng) * math.pi / 180
            dlng = abs(lng1 - lng2)
            dlat = abs(lat1 - lat2)
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            R = 6371000
            return R * c
        except Exception as e:
            db_logger.exception(e)
            raise e
    def to_csv(self):
        return str(self.lat) + ", " +str(self.lng)
    def to_address(self):
        GOOGLE_KEY = settings.GOOGLE_KEY
        request = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?latlng={self.to_csv()}&key={GOOGLE_KEY}")
        response = dict(request.json())
        db_logger.info(response)
        try:
            address_1 = response['results'][0]["address_components"][0]['long_name'] + " " + response['results'][0]["address_components"][1]['long_name'] 
            post_code = response['results'][0]["address_components"][7]['long_name']
            city = response['results'][0]["address_components"][3]['long_name']
            state = response['results'][0]["address_components"][5]['short_name']
            obj, _ = Address.objects.get_or_create(address_1=address_1, post_code=post_code, city=city, state=state)
            obj.save()
            return obj
        except Exception as e:
            db_logger.exception(e)
            return None
    def to_timezone(self):
        tf = TimezoneFinder()
        latitude, longitude = (self.lat, self.lng)
        timezone = tf.timezone_at(lng=longitude, lat=latitude)
        return timezone

class Address(models.Model):
    address_1 = models.CharField(_("Address 1"), max_length=128)
    address_2 = models.CharField(_("Address 2"), max_length=128, blank=True, null=True)
    post_code = USZipCodeField()
    city = models.CharField(_("City"), max_length=64)
    state = models.CharField(_("State"), max_length=2, choices=US_STATES)
    def __str__(self):
        return f"{self.address_1} {self.address_2} {self.city}, {self.state}, {self.post_code}"
    def to_coordinates(self):
        GOOGLE_KEY = settings.GOOGLE_KEY
        try:
            request = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?address={self.__str__()}&key={GOOGLE_KEY}")
            db_logger.info(request)
            response = dict(request.json())
            coordinates = response['results'][0]['geometry']['location']
            obj, _ = Coordinates.objects.get_or_create(lat=coordinates['lat'], lng=coordinates['lng'])
            obj.save()
            return obj
        except Exception as e:
            db_logger.exception(e)
            return None