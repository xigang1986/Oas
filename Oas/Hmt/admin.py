from django.contrib import admin

from Hmt import models

# Register your models here.
admin.site.register(models.Host)
admin.site.register(models.HostGroup)
admin.site.register(models.UserProfile)
admin.site.register(models.Task)