from django.db import models
from django.utils.translation import ugettext_lazy as _ 
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager 
from .managers import AccountManager
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
    profile_pic = models.ImageField(blank=True, null=True)
    dob = models.DateTimeField()
    sex = models.CharField(max_length=1, choices=SEXES)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(verbose_name=_("Last login"), auto_now=True)
    objects = AccountManager()
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]
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

    def save(self, *args, **kwargs):
        if self.sex is None:
            self.sex = self.determine_sex()
        super(Account, self).save(*args, **kwargs)

class NetworkInfo(models.Model):
    ip_address = models.GenericIPAddressField()
    ssid = models.CharField(max_length=128)
    bssid = models.CharField(max_length=128)

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

class AndroidDevice(Device):
    board = models.CharField(max_length=128)
    bootloader = models.CharField(max_length=128)
    brand = models.CharField(max_length=128)
    device = models.CharField(max_length=128)
    display = models.CharField(max_length=128)
    fingerprint = models.CharField(max_length=128)
    hardware = models.CharField(max_length=128)
    host = models.CharField(max_length=128)
    build_id = models.CharField(max_length=128) # called just id in original Map
    manufacturer = models.CharField(max_length=128)
    model = models.CharField(max_length=128)
    product = models.CharField(max_length=128)
    tags = models.CharField(max_length=128)
    android_type = models.CharField(max_length=128) # called just type in original Map
    is_physical_device = models.CharField(max_length=128)
    androidId = models.CharField(max_length=128)
    systemFeatures = models.CharField(max_length=128)

class iOSDevice(Device):
    name = models.CharField(max_length=128)
    system_name = models.CharField(max_length=128)
    system_version = models.CharField(max_length=128)
    model = models.CharField(max_length=128)
    localized_model = models.CharField(max_length=128)
    identifier_for_vendor = models.CharField(max_length=128)
    is_physical_device = models.CharField(max_length=128)

class LocationPing(models.Model):
    lat = models.FloatField()
    lng = models.FloatField()
    timestamp = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="location_pings")

class Contact(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="contacts")
    display_name = models.CharField(max_length=128)
    given_name = models.CharField(max_length=128)
    middle_name = models.CharField(max_length=128)
    prefix = models.CharField(max_length=10)
    suffix = models.CharField(max_length=10)
    family_name = models.CharField(max_length=128)
    emails_raw = models.CharField(max_length=512)
    phones_raw = models.CharField(max_length=512)
    addresses_raw = models.CharField(max_length=512)
    company = models.CharField(max_length=128)
    job_title = models.CharField(max_length=128)

    @property 
    def emails(self):
        return emails_raw.strip()

    @property 
    def phones(self):
        return phones_raw.strip()
    
    @property 
    def addresses(self):
        return addresses_raw.strip()

class ClipboardData(models.Model):
    data = models.CharField(max_length=128)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="clipboard_data")