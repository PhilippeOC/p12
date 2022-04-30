from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from events.models import ClientAssociation, ContractAssociation, EventAssociation


class Person(models.Model):
    email = models.EmailField(max_length=200, unique=True, null=False)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    mobile = models.CharField(max_length=20, blank=True)

    class Meta:
        abstract = True


class EmployeeManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Vous devez entrer un email')

        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **kwargs):
        user = self.create_user(email=email, password=password, **kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.role = 'M'
        user.save()
        return user


class Employee(AbstractBaseUser, PermissionsMixin, Person):
    customers = models.ManyToManyField('users.Client',
                                       through=ClientAssociation,
                                       related_name='customer_employees')
    contracts = models.ManyToManyField('events.Contract',
                                       through=ContractAssociation,
                                       related_name='contract_employees')
    events = models.ManyToManyField('events.Event',
                                    through=EventAssociation,
                                    related_name='event_employees')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    class Roles(models.TextChoices):
        MANAGEMENT = 'M', 'Management'
        SUPPORT = 'S', 'Support'
        BUSINESS = 'B', 'Business'

    role = models.CharField(max_length=1, choices=Roles.choices, default=Roles.SUPPORT)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['last_name', 'first_name']

    objects = EmployeeManager()

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return f"Employee id: {self.pk}"


class Client(Person):
    company_name = models.CharField(max_length=250)
    is_client = models.BooleanField(default=False)

    def __str__(self):
        return f"Client id: {self.pk}"
