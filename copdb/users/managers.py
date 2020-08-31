from django.utils.translation import ugettext_lazy as _ 
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager 

class AccountManager(BaseUserManager):
    def create_user(self, username, email, first_name, last_name, password, **extra_fields):
        if not username:
            raise ValueError("Users must have an username.")
        if not email:
            raise ValueError("Users must have an email.")
        if not (first_name or last_name):
            raise ValueError("Users must have a full name.")
        user = self.model(
            username = AbstractBaseUser.normalize_username(username),
            email = self.normalize_email(email),
            first_name=first_name.strip().capitalize(),
            last_name=last_name.strip().capitalize(),
            **extra_fields
        )
        user.first_name = user.first_name.strip().capitalize()
        user.last_name = user.last_name.strip().capitalize()
        user.set_password(password)
        user.save(using=self._db)
        return user 

    def create_superuser(self, username, email, first_name, last_name, password, **extra_fields):
        user = self.model(
            username = AbstractBaseUser.normalize_username(username),
            email = self.normalize_email(email),
            first_name=first_name.strip().capitalize(),
            last_name=last_name.strip().capitalize(),
            **extra_fields
        )
        user.set_password(password)
        user.is_admin = True 
        user.is_staff = True 
        user.save(using=self._db)
        return user