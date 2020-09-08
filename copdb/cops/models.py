from django.db import models
from django.db.models import F, Value, Func, Count
from users.models import Account
from geolocation.models import Coordinates, CopDBCity, Address
import gender_guesser.detector as gender
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
import math

class PoliceDepartment(models.Model):
    name = models.CharField(max_length=64)
    image = models.ImageField(upload_to="police_departments", blank=True, null=True)
    city = models.ForeignKey(CopDBCity, on_delete=models.DO_NOTHING, blank=True, null=True)
    def get_nearby_coords(lat, lng, max_distance=None):
        """
        Return objects sorted by distance to specified coordinates
        which distance is less than max_distance given in kilometers
        """
        # Great circle distance formula
        R = 6371
        qs = Precinct.objects.all().annotate(
            distance=Value(R)*Func(
                    Func(
                        F("city__epicenter__coordinates__lat")*Value(math.sin(math.pi/180)),
                        function="sin",
                        output_field=models.FloatField()
                    ) * Value(
                        math.sin(lat*math.pi/180)
                    ) + Func(
                        F("city__epicenter__coordinates__lat")* Value(math.pi/180),
                        function="cos",
                        output_field=models.FloatField()
                    ) * Value(
                        math.cos(lat*math.pi/180)
                    ) * Func(
                        Value(lng*math.pi/180) - F("city__epicenter__coordinates__lng") * Value(math.pi/180),
                        function="cos",
                        output_field=models.FloatField()
                    ),
                    function="acos"
                )
        ).order_by("distance")
        if max_distance is not None:
            qs = qs.filter(distance__lt=max_distance)
        return qs
    def __str__(self):
        return self.name

class Precinct(models.Model):
    name = models.CharField(max_length=64)
    image = models.ImageField(upload_to="precints", blank=True, null=True)
    police_department = models.ForeignKey(PoliceDepartment, on_delete=models.DO_NOTHING)
    is_hq = models.BooleanField(default=False)
    coordinates = models.ForeignKey(Coordinates, on_delete=models.CASCADE, related_name="precincts")
    address = models.ForeignKey(Address, on_delete=models.CASCADE, blank=True, null=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "police_department"], name="unique_precinct")
        ]
    
    def get_nearby_coords(lat, lng, max_distance=10):
        """
        Return objects sorted by distance to specified coordinates
        which distance is less than max_distance given in kilometers
        """
        # Great circle distance formula
        R = 6371
        qs = Precinct.objects.all().annotate(
            distance=Value(R)*Func(
                    Func(
                        F("coordinates__lat")*Value(math.sin(math.pi/180)),
                        function="sin",
                        output_field=models.FloatField()
                    ) * Value(
                        math.sin(lat*math.pi/180)
                    ) + Func(
                        F("coordinates__lat")* Value(math.pi/180),
                        function="cos",
                        output_field=models.FloatField()
                    ) * Value(
                        math.cos(lat*math.pi/180)
                    ) * Func(
                        Value(lng*math.pi/180) - F("coordinates__lng") * Value(math.pi/180),
                        function="cos",
                        output_field=models.FloatField()
                    ),
                    function="acos"
                )
        ).order_by("distance")
        if max_distance is not None:
            qs = qs.filter(distance__lt=max_distance)
        return qs
        
    def __str__(self):
        return self.name


class Cop(models.Model):
    ETHNICITY_TYPES = (
        ("White", "White"),
        ("Black", "Black"),
        ("Hispanic", "Hispanic"),
        ("American Indian", "American Indian"),
        ("Other Race", "Other"),
        ("Unknown", "Unknown"),
    )
    first_name = models.CharField(max_length=128, blank=True, null=True)
    last_name = models.CharField(max_length=128, blank=True, null=True)
    sex = models.CharField(max_length=1, choices=Account.SEXES, default="U")
    ethnicity = models.CharField(max_length=16, choices=ETHNICITY_TYPES, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    rank = models.CharField(max_length=128, blank=True, null=True)
    badge_number = models.CharField(max_length=128, blank=True, null=True)
    precinct = models.ForeignKey(Precinct, blank=True, null=True, on_delete=models.DO_NOTHING, related_name="cops")
    police_department = models.ForeignKey(PoliceDepartment, blank=True, null=True, on_delete=models.DO_NOTHING)
    description = models.CharField(max_length=128, blank=True, null=True)
    image = models.ImageField(upload_to="cops", blank=True, null=True)

    def determine_sex(self):
        d = gender.Detector(case_sensitive=False)
        sex = d.get_gender(self.first_name)
        if "female" in sex:
            return "F"
        elif "male" in sex:
            return "M"
        return "U"
    
    def get_highest_offenders():
        top_offenders = Cop.objects.all().annotate(num_complaints=Count("complaints")).order_by("-num_complaints")
        return top_offenders
    
    def get_nearby_coords(lat, lng, max_distance=10):
        """
        Return objects sorted by distance to specified coordinates
        which distance is less than max_distance given in kilometers
        """
        # Great circle distance formula
        R = 6371
        qs = Precinct.objects.all().annotate(
            distance=Value(R)*Func(
                    Func(
                        F("precinct__coordinates__lat")*Value(math.sin(math.pi/180)),
                        function="sin",
                        output_field=models.FloatField()
                    ) * Value(
                        math.sin(lat*math.pi/180)
                    ) + Func(
                        F("precinct__coordinates__lat")* Value(math.pi/180),
                        function="cos",
                        output_field=models.FloatField()
                    ) * Value(
                        math.cos(lat*math.pi/180)
                    ) * Func(
                        Value(lng*math.pi/180) - F("precinct__coordinates__lng") * Value(math.pi/180),
                        function="cos",
                        output_field=models.FloatField()
                    ),
                    function="acos"
                )
        ).order_by("distance")
        if max_distance is not None:
            qs = qs.filter(distance__lt=max_distance)
        return qs

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["first_name", "last_name", "badge_number"], name="unique_officer")
        ]
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        super(Cop, self).save(*args, **kwargs)

class Complaint(models.Model):
    abuse_type = models.CharField(max_length=128)
    allegation = models.CharField(max_length=128)
    cop = models.ForeignKey(Cop, on_delete=models.CASCADE, blank=True, null=True, related_name="complaints")
    complainant_name = models.CharField(max_length=64, blank=True, null=True)
    complainant_gender = models.CharField(max_length=1, blank=True, null=True, choices=Account.SEXES, default="U")
    complainant_ethnicity = models.CharField(max_length=16, choices=Cop.ETHNICITY_TYPES, blank=True, null=True)
    complainant_age = models.IntegerField(blank=True, null=True)
    contact_reason = models.CharField(max_length=64, blank=True, null=True)
    date_recieved = models.DateTimeField(blank=True, null=True)
    description = models.CharField(max_length=256, blank=True, null=True)
    outcome = models.CharField(max_length=128, blank=True, null=True)
    finding = models.CharField(max_length=128, blank=True, null=True)
    date_concluded = models.DateTimeField(blank=True, null=True)

    def get_nearby_coords(lat, lng, max_distance=10):
        """
        Return objects sorted by distance to specified coordinates
        which distance is less than max_distance given in kilometers
        """
        # Great circle distance formula
        R = 6371
        qs = Precinct.objects.all().annotate(
            distance=Value(R)*Func(
                    Func(
                        F("cop__precinct__coordinates__lat")*Value(math.sin(math.pi/180)),
                        function="sin",
                        output_field=models.FloatField()
                    ) * Value(
                        math.sin(lat*math.pi/180)
                    ) + Func(
                        F("cop__precinct__coordinates__lat")* Value(math.pi/180),
                        function="cos",
                        output_field=models.FloatField()
                    ) * Value(
                        math.cos(lat*math.pi/180)
                    ) * Func(
                        Value(lng*math.pi/180) - F("cop__precinct__coordinates__lng") * Value(math.pi/180),
                        function="cos",
                        output_field=models.FloatField()
                    ),
                    function="acos"
                )
        ).order_by("distance")
        if max_distance is not None:
            qs = qs.filter(distance__lt=max_distance)
        return qs

    class Meta:
        ordering = ['-date_recieved']

    def __str__(self):
        return f"{self.abuse_type}: {self.allegation} by {self.cop}"

class CopDBComplaint(Complaint):
    location = models.ForeignKey(Coordinates, on_delete=models.DO_NOTHING, related_name="complaints")
    image = models.ImageField(upload_to="complaints", blank=True, null=True)
    complainant_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="complaints")

class CopDBEvent(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    sharers = models.ManyToManyField(Account, related_name="events_shared")
    promoters = models.ManyToManyField(Account, related_name="events_promoted")
    def get_nearby_coords(lat, lng, max_distance=10):
        """
        Return objects sorted by distance to specified coordinates
        which distance is less than max_distance given in kilometers
        """
        # Great circle distance formula
        R = 6371
        qs = Precinct.objects.all().annotate(
            distance=Value(R)*Func(
                    Func(
                        F("complaint__cop__precinct__coordinates__lat")*Value(math.sin(math.pi/180)),
                        function="sin",
                        output_field=models.FloatField()
                    ) * Value(
                        math.sin(lat*math.pi/180)
                    ) + Func(
                        F("complaint__cop__precinct__coordinates__lat")* Value(math.pi/180),
                        function="cos",
                        output_field=models.FloatField()
                    ) * Value(
                        math.cos(lat*math.pi/180)
                    ) * Func(
                        Value(lng*math.pi/180) - F("complaint__cop__precinct__coordinates__lng") * Value(math.pi/180),
                        function="cos",
                        output_field=models.FloatField()
                    ),
                    function="acos"
                )
        ).order_by("distance")
        if max_distance is not None:
            qs = qs.filter(distance__lt=max_distance)
        return qs

    class Meta:
        ordering = ['-complaint__date_recieved']

    def __str__(self):
        return f"{self.abuse_type}: {self.allegation} by {self.cop}"