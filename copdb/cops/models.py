from django.db import models
from users.models import Account
from geolocation.models import Coordinates

class Cop(models.Model):
    first_name = models.CharField(max_length=128, blank=True, null=True)
    last_name = models.CharField(max_length=128, blank=True, null=True)
    description = models.CharField(max_length=128, blank=True, null=True)
    age = models.CharField(max_length=128, blank=True, null=True)
    badge_number = models.CharField(max_length=128, blank=True, null=True)
    precinct = models.CharField(max_length=128, blank=True, null=True)
    police_department = models.CharField(max_length=128, blank=True, null=True)

class Conclusion(models.Model):
    type = models.CharField(max_length=32, blank=True, null=True)
    discipline = models.CharField(max_length=32, blank=True, null=True)
    date_concluded = models.DateTimeField()

class Complainer(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True)
    description = models.CharField(max_length=64, blank=True, null=True)

class CCRBComplainer(Complainer):
    def save(self, *args, **kwargs):
        super(CCRBComplainer, self).save(*args, **kwargs)

class CopDBComplainer(Complainer):
    user = models.ForeignKey(Account, on_delete=models.DO_NOTHING)
    def save(self, *args, **kwargs):
        self.name = user.username
        self.description = "CopDB user"
        super(CCRBComplainer, self).save(*args, **kwargs)

class Complaint(models.Model):
    category = models.CharField(max_length=32)
    allegation = models.CharField(max_length=64)
    complainer = models.ForeignKey(Complainer, on_delete=models.DO_NOTHING)

class CCRBComplaint(Complaint):
    complainant_details = models.CharField(max_length=64, blank=True, null=True)
    conclusion = models.ForeignKey(Conclusion, on_delete=models.CASCADE, blank=True, null=True)
    date_recieved = models.DateTimeField()

class CopDBComplaint(Complaint):
    complainer = models.ForeignKey(CopDBComplainer, on_delete=models.DO_NOTHING)
    description = models.CharField(max_length=256)
    location = models.ForeignKey(Coordinates, on_delete=models.DO_NOTHING)

class CopDBEvent(models.Model):
    complaint = models.ForeignKey(CopDBComplaint, on_delete=models.CASCADE)
    sharers = models.ManyToManyField(Account)
    promoters = models.ManyToManyField(Account)
    
