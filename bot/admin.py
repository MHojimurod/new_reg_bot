from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(User)
admin.site.register(Region)
admin.site.register(Question)
admin.site.register(Task)