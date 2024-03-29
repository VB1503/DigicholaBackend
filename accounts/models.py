from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken

from mptt.models import MPTTModel, TreeForeignKey
from accounts.managers import UserManager
# Create your models here.

AUTH_PROVIDERS ={'email':'email', 'google':'google', 'github':'github', 'linkedin':'linkedin'}

class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True, editable=False) 
    email = models.EmailField(
        max_length=255, verbose_name=_("Email Address"), unique=True
    )
    phone_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    is_business_user = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified=models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    auth_provider=models.CharField(max_length=50, blank=False, null=False, default=AUTH_PROVIDERS.get('email'))

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def tokens(self):    
        refresh = RefreshToken.for_user(self)
        return {
            "refresh":str(refresh),
            "access":str(refresh.access_token)
        }


    def __str__(self):
        return f"{self.email}-{self.id}"

    @property
    def get_full_name(self):
        return f"{self.first_name.title()} {self.last_name.title()}"



class Category(MPTTModel):
  category = models.CharField(max_length=200, unique=True)
  parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
  categoryImage = models.URLField()
  
  class MPTTMeta:
    order_insertion_by = ['category']

  class Meta:
    verbose_name_plural = 'Categories'

  def __str__(self):
    return self.category

class BusinessUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='business_profile')
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True)
    priority = models.IntegerField(default=0, blank=True, unique=True)
    
    def __str__(self):
        return f"{self.user}-{self.full_name}-{self.phone_number}"
class BusinessDetails(models.Model):
    business_id = models.BigAutoField(primary_key=True, editable=False)
    business_name = models.CharField(max_length=255)
    business_email = models.EmailField(max_length=255, verbose_name=_("Email Address"))
    business_count = models.PositiveIntegerField()
    business_phone_number = models.CharField(max_length=20)
    business_profile = models.URLField()
    place = models.CharField(max_length=255)
    rating = models.FloatField()
    description = models.TextField()
    category = TreeForeignKey(Category, on_delete=models.CASCADE)
    business_user = models.ForeignKey(BusinessUser, on_delete=models.CASCADE)
    
    def __str__(self):
       return f"{self.business_id}-{self.business_name}-{self.business_user}-{self.business_phone_number}"

class OneTimePassword(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    otp=models.CharField(max_length=6)


    def __str__(self):
        return f"{self.user.first_name} - otp code"