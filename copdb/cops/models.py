from django.db import models
from django.db.models import F, Value, Func, Count
from users.models import Account
from geolocation.models import Coordinates, CopDBCity, Address
import gender_guesser.detector as gender
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
import math
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

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
        qs = PoliceDepartment.objects.all().annotate(
            distance=Value(R)*Func(
                    Func(
                        F("city__epicenter__lat")*Value(math.sin(math.pi/180)),
                        function="sin",
                        output_field=models.FloatField()
                    ) * Value(
                        math.sin(lat*math.pi/180)
                    ) + Func(
                        F("city__epicenter__lat")* Value(math.pi/180),
                        function="cos",
                        output_field=models.FloatField()
                    ) * Value(
                        math.cos(lat*math.pi/180)
                    ) * Func(
                        Value(lng*math.pi/180) - F("city__epicenter__lng") * Value(math.pi/180),
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
    
    def get_nearby_coords(lat, lng, max_distance=None):
        """
        Return objects sorted by distance to specified coordinates
        which distance is less than max_distance given in kilometers
        """
        # Great circle distance formula
        R = 6371
        qs = Cop.objects.all().annotate(
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
    date_recieved = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    description = models.CharField(max_length=256, blank=True, null=True)
    outcome = models.CharField(max_length=128, blank=True, null=True)
    finding = models.CharField(max_length=128, blank=True, null=True)
    date_concluded = models.DateTimeField(blank=True, null=True)

    @property 
    def date(self):
        return self.date_recieved

    def get_nearby_coords(lat, lng, max_distance=None):
        """
        Return objects sorted by distance to specified coordinates
        which distance is less than max_distance given in kilometers
        """
        # Great circle distance formula
        R = 6371
        qs = Complaint.objects.all().annotate(
            distance=Value(R)*Func(
                    Func(
                        F("cop__precinct__coordinates__lat") * Value(math.sin(math.pi/180)),
                        function="sin",
                        output_field=models.FloatField()
                    ) * Value(
                        math.sin(lat*math.pi/180)
                    ) + Func(
                        F("cop__precinct__coordinates__lat") * Value(math.pi/180),
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
    location = models.ForeignKey(Coordinates, on_delete=models.PROTECT, related_name="complaints")
    address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name="complaints")
    image = models.ImageField(upload_to="complaints", blank=True, null=True)
    complainant_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="complaints")
    verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.verified = self.complainant_account.verified and self.cop is not None
        if not self.verified:
            self.alert_user_of_complaint_verification()
        if (not self.address) and self.coordinates:
            self.address = self.coordinates.to_address()
        super(Cop, self).save(*args, **kwargs)

    def alert_user_of_complaint_verification(self):
        user = self.complainant_account
        complaint = self
        htmly = get_template("cops/verification_needed.html")
        plaintext = get_template("cops/verification_needed.txt")
        subject = get_template("cops/verification_needed_subject.txt")
        d = Context({"user": user, "complaint": complaint})
        text_content = plaintext.render(d)
        html_content = htmly.render(d)
        subject_content = subject.render(d)
        msg = EmailMultiAlternatives(subject_content, text_content, "users@copdb.app", [user.email], reply_to=["reports@copdb.app"])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
    def alert_admin_of_complaint(self):
        pass

class CopDBComplaintRequest(models.Model):
    complaint = models.ForeignKey(CopDBComplaint, on_delete=models.CASCADE)

    cop_first_name = models.CharField(max_length=128, blank=True, null=True)
    cop_last_name = models.CharField(max_length=128, blank=True, null=True)
    cop_sex = models.CharField(max_length=1, choices=Account.SEXES, default="U")
    cop_ethnicity = models.CharField(max_length=16, blank=True, null=True)
    cop_badge_number = models.CharField(max_length=128, blank=True, null=True)


class CopDBEvent(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    sharers = models.ManyToManyField(Account, related_name="events_shared")
    promoters = models.ManyToManyField(Account, related_name="events_promoted")
    title = models.CharField(max_length=128)

    @property 
    def date(self):
        return self.complaint.date_recieved

    class Meta:
        ordering = ['-complaint__date_recieved']
        
    def get_nearby_coords(lat, lng, max_distance=None):
        """
        Return objects sorted by distance to specified coordinates
        which distance is less than max_distance given in kilometers
        """
        # Great circle distance formula
        R = 6371
        qs = CopDBEvent.objects.all().annotate(
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
    
    @property
    def num_shares(self):
        return self.sharers.count()
    
    @property
    def num_promotions(self):
        return self.promoters.count()

    def __str__(self):
        return f"{self.abuse_type}: {self.allegation} by {self.cop}"