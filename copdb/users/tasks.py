from celery import shared_task
from .models import * 

@shared_task
def process_request_data(lat, lng, userid):
    user = Account.objects.get(id=userid)
    coords, _ = Coordinates.objects.get_or_create(lat=lat, lng=lng)
    ping = LocationPing.objects.create(user=user, coordinates=coords)