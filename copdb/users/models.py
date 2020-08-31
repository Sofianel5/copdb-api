from django.db import models
from django.utils.translation import ugettext_lazy as _ 
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager 
from assistants.models import Assistant
from .managers import AccountManager

class Account(AbstractBaseUser):
    username = models.CharField(verbose_name=_("Username"), max_length=150, unique=True)
    email = models.EmailField(verbose_name=_("Email"), max_length=150, unique=True)
    first_name = models.CharField(verbose_name=_("First name"), max_length=100)
    last_name = models.CharField(verbose_name=_("Last name"), max_length=100)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(verbose_name=_("Last login"), auto_now=True)
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE, related_name="users", null=True, blank=True)
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
    
    def save(self, *args, **kwargs):
        super(Account, self).save(*args, **kwargs)
    