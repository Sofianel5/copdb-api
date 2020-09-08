from django.utils.translation import ugettext_lazy as _ 
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager 

class AccountManager(BaseUserManager):
    def create_user(self, username, email, first_name, last_name, dob, password, **extra_fields):
        if not username:
            raise ValueError("no_username")
        if not email:
            raise ValueError("no_email")
        if not (first_name or last_name):
            raise ValueError("no_full_name")
        if not dob:
            raise ValueError("no_dob")
        user = self.model(
            username = AbstractBaseUser.normalize_username(username),
            email = self.normalize_email(email),
            first_name=first_name.strip().capitalize(),
            last_name=last_name.strip().capitalize(),
            dob=dob,
            **extra_fields
        )
        user.first_name = user.first_name.strip().capitalize()
        user.last_name = user.last_name.strip().capitalize()
        user.set_password(password)
        user.save(using=self._db)
        return user 

    def create_superuser(self, username, email, first_name, last_name, dob, password, **extra_fields):
        user = self.model(
            username = AbstractBaseUser.normalize_username(username),
            email = self.normalize_email(email),
            first_name=first_name.strip().capitalize(),
            last_name=last_name.strip().capitalize(),
            dob=dob,
            **extra_fields
        )
        user.set_password(password)
        user.is_admin = True 
        user.is_staff = True 
        user.save(using=self._db)
        return user