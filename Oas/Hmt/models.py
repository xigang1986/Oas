from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Host(models.Model):
    ip =  models.GenericIPAddressField(unique=True)
    key = models.TextField()
    status_choices = ((0,'Waiting Approval'),
                      (1,'Accepted'),
                      (2,'Rejected'))
    status = models.SmallIntegerField(choices=status_choices,default=0)
    def __str__(self):
        return self.ip
class HostGroup(models.Model):
    name =  models.CharField(max_length=64,unique=True)
    hosts = models.ManyToManyField(Host,blank=True)
    def __str__(self):
        return self.name
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length=32)
    def __str__(self):
        return self.name
class Task(models.Model):
    user =models.ForeignKey(UserProfile)
    datetime = models.DateTimeField(auto_now_add=True)
    memo = models.TextField(u'备注', null=True, blank=True)
    #hosts = models.ManyToManyField(Host)
    #script_name =  models.CharField(max_length=64)
    # status_choices = (('comand',"命令行"),
    #                   ('script',"脚本"),
    #                   )
    # status = models.CharField(choices=status_choices,max_length=64)
    def __str__(self):
        return '%d'%self.id
# class TaskHandle(models.Model):
#     task = models.OneToOneField(Task)
