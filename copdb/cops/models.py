from django.db import models

# Create your models here.
class Cop(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    description = models.CharField(max_length=128)
    age = models.CharField(max_length=128)
    badge_number = models.CharField(max_length=128)
    precinct = models.CharField(max_length=128)

class Conclusion(models.Model):
    type = models.CharField(max_length=32)
    discipline = models.CharField(max_length=32)

class Complaint(models.Model):
    COMPLAINT_TYPES = (
        ("Force", "Force"),
        ("Abuse of Authority", "Abuse of Authority"),
        ("Discourtesy", "Discourtesy"),
        ("Offensive Language", "Offensive Language"),
    )
    type = models.CharField(max_length=32, choices=COMPLAINT_TYPES)
    detail_type = models.CharField(max_length=64)
    complainant_details = models.CharField(max_length=64)
    conclusion = models.ForeignKey(Conclusion, on_delete=models.CASCADE)
    year_recieved = models.IntegerField()