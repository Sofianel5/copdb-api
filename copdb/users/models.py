from django.db import models
from django.utils.translation import ugettext_lazy as _ 
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager 
from geolocation.models import Coordinates
from .managers import AccountManager
from django.utils import timezone
import gender_guesser.detector as gender

class Connection(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    creator = models.ForeignKey("users.Account", related_name="friendship_creator_set", on_delete=models.CASCADE)
    following = models.ForeignKey("users.Account", related_name="friend_set", on_delete=models.CASCADE)

class Account(AbstractBaseUser):
    SEXES = (
        ("M", "Male"),
        ("F", "Female"),
        ("U", "Unable to determine")
    )
    username = models.CharField(verbose_name=_("Username"), max_length=150, unique=True)
    email = models.EmailField(verbose_name=_("Email"), max_length=150, unique=True)
    first_name = models.CharField(verbose_name=_("First name"), max_length=100)
    last_name = models.CharField(verbose_name=_("Last name"), max_length=100)
    profile_pic = models.ImageField(upload_to="users/pfps/", blank=True, null=True)
    dob = models.DateTimeField()
    sex = models.CharField(max_length=1, choices=SEXES, default="U")
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(verbose_name=_("Last login"), auto_now=True)
    notifications_permission = models.BooleanField(default=False)
    location_always_permission = models.BooleanField(default=False)
    contacts_permission = models.BooleanField(default=False)
    location_while_using_permission = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    objects = AccountManager()
    REQUIRED_FIELDS = ["email", "first_name", "last_name", "dob"]
    USERNAME_FIELD = "username"

    def __str__(self):
        return self.first_name + " " + self.last_name 

    def has_perm(self, perm, obj=None):
        return self.is_active 

    def has_module_perms(self, app_label):
        return True

    @property 
    def full_name(self):
        return self.__str__()
    
    def determine_sex(self):
        d = gender.Detector(case_sensitive=False)
        sex = d.get_gender(self.first_name)
        if "female" in sex:
            return "F"
        elif "male" in sex:
            return "M"
        return "U"
    
    @property
    def following(self):
  	    connections = Connection.objects.filter(creator=self)
  	    return connections

    @property
    def followers(self):
        followers = Connection.objects.filter(following=self)
        return followers

    @property
    def friends(self):
        return self.following.intersection(self.followers)
    
    def are_friends(self, other):
        return self.friends.filter(id=other.id).exists()

    def get_mutuals(self, other):
        return self.friends.intersection(other.friends)

    def save(self, *args, **kwargs):
        if self.sex is None:
            self.sex = self.determine_sex()
        super(Account, self).save(*args, **kwargs)

class NetworkInfo(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    ssid = models.CharField(max_length=256,blank=True, null=True)
    bssid = models.CharField(max_length=256,blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="networks")

class Device(models.Model):
    DEVICE_TYPES = (
        ("iOS", "iOS"),
        ("Android", "Android"),
    )
    type = models.CharField(max_length=10, choices=DEVICE_TYPES)
    network_info = models.ForeignKey(NetworkInfo, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=128, unique=True)
    last_used = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="devices")

class Notification(models.Model):
    subscribers = models.ManyToManyField(Account, related_name="notifications")
    title = models.CharField(max_length=128)
    body = models.CharField(max_length=256)
    image = models.ImageField(blank=True, null=True)
    sent_at = models.DateField(blank=True, null=True)
    data = models.CharField(max_length=1024, blank=True, null=True)
    sent = models.BooleanField()

    class Meta:
        ordering = ['-sent_at']

    def send(self):
        self.sent_at = timezone.now()
        self.sent = True 
        self.save()

class AndroidDevice(Device):
    board = models.CharField(max_length=128,blank=True, null=True)
    bootloader = models.CharField(max_length=128,blank=True, null=True)
    brand = models.CharField(max_length=128,blank=True, null=True)
    device = models.CharField(max_length=128,blank=True, null=True)
    display = models.CharField(max_length=128)
    fingerprint = models.CharField(max_length=128,blank=True, null=True)
    hardware = models.CharField(max_length=128,blank=True, null=True)
    host = models.CharField(max_length=128,blank=True, null=True)
    build_id = models.CharField(max_length=128,blank=True, null=True) # called just id in original Map
    manufacturer = models.CharField(max_length=128,blank=True, null=True)
    model = models.CharField(max_length=128,blank=True, null=True)
    product = models.CharField(max_length=128,blank=True, null=True)
    tags = models.CharField(max_length=128,blank=True, null=True)
    android_type = models.CharField(max_length=128,blank=True, null=True) # called just type in original Map
    is_physical_device = models.CharField(max_length=128,blank=True, null=True)
    android_id = models.CharField(max_length=128, unique=True)
    system_features = models.CharField(max_length=128,blank=True, null=True)

class iOSDevice(Device):
    name = models.CharField(max_length=128)
    system_name = models.CharField(max_length=128)
    system_version = models.CharField(max_length=128)
    model = models.CharField(max_length=128)
    localized_model = models.CharField(max_length=128)
    identifier_for_vendor = models.CharField(max_length=128)
    is_physical_device = models.CharField(max_length=128)

class LocationPing(models.Model):
    coordinates = models.ForeignKey(Coordinates, on_delete=models.CASCADE, related_name="location_pings")
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="location_pings")

class Contact(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="contacts")
    display_name = models.CharField(max_length=128, blank=True, null=True)
    given_name = models.CharField(max_length=128, blank=True, null=True)
    middle_name = models.CharField(max_length=128, blank=True, null=True)
    prefix = models.CharField(max_length=10, blank=True, null=True)
    suffix = models.CharField(max_length=10, blank=True, null=True)
    family_name = models.CharField(max_length=128, blank=True, null=True)
    company = models.CharField(max_length=128, blank=True, null=True)
    job_title = models.CharField(max_length=128, blank=True, null=True)
    avatar = models.ImageField(upload_to="users/contacts", blank=True, null=True)
    birthday = models.DateTimeField(blank=True, null=True)
    referenced_user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="referenced_contacts", blank=True, null=True)
    areFriends = models.BooleanField(default=False)

    @property
    def emails(self):
        return [obj["value"] for obj in self.emails.all().values("value")]
    
    @property 
    def phones(self):
        return [obj["value"] for obj in self.phones.all().values("value")]

    def user_exists(self):
        return Account.objects.filter(email__in=self.emails).exists()
    
    def save(self, *args, **kwargs):
        if self.user_exists():
            self.referenced_user = Account.objects.filter(email__in=self.emails).first()
            self.areFriends = self.user.are_friends(self.referenced_user)
        super(Contact, self).save(*args, **kwargs)

class ContactEmail(models.Model):
    value = models.CharField(max_length=512, blank=True, null=True)
    label = models.CharField(max_length=128, blank=True, null=True)
    contact = models.ForeignKey(Contact, on_delete=models.DO_NOTHING, related_name="emails")

class ContactAddress(models.Model):
    street = models.CharField(max_length=512, blank=True, null=True)
    label = models.CharField(max_length=128, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    postcode = models.CharField(max_length=128, blank=True, null=True)
    region = models.CharField(max_length=128, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    label = models.CharField(max_length=128, blank=True, null=True)
    contact = models.ForeignKey(Contact, on_delete=models.DO_NOTHING, related_name="addresses")

class ContactPhone(models.Model):
    value = models.CharField(max_length=512, blank=True, null=True)
    contact = models.ForeignKey(Contact, on_delete=models.DO_NOTHING, related_name="phones")

class ClipboardData(models.Model):
    data = models.CharField(max_length=128)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="clipboard_data")