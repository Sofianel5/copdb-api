from django.db import models
from users.models import Account

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

class Complainer(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=64)

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
    complainant_details = models.CharField(max_length=64)
    conclusion = models.ForeignKey(Conclusion, on_delete=models.CASCADE)
    year_recieved = models.IntegerField()
