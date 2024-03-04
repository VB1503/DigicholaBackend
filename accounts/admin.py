from django.contrib import admin
from .models import User, OneTimePassword, BusinessUser, Category, BusinessDetails

admin.site.register(Category)
admin.site.register(User)
admin.site.register(BusinessUser)
admin.site.register(OneTimePassword)
admin.site.register(BusinessDetails)