from __future__ import unicode_literals
from django.db import models


# Create your models here.
class branch(models.Model):
    name=models.CharField(max_length=200)
    address=models.CharField(max_length=200)
    branch_code=models.CharField(max_length=200)
    
    class Meta:
         verbose_name_plural = "Branches"
         
         
    def json_object(self):
        return {
            "name":self.name,
            "address":self.address,
            "branch_code":self.branch_code
        }
    
    def __str__(self):
        return self.name

class Bank(models.Model):
    name=models.CharField(max_length=200)
    branch=models.ForeignKey(branch,on_delete=models.CASCADE)
    
    def json_object(self):
        return {
            'name':self.name,
            'branch':self.branch
        }
    def __str__(self):
        return self.name
    
class ClientManager(models.Model):
    name=models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
    
class Client(models.Model):
    name=models.CharField(max_length=200)
    address=models.CharField(max_length=200)
    
    
    def json_object(self):
        return{
            'name': self.name,
            'address': self.address
        }
    
    def __str__(self):
        return self.name
    