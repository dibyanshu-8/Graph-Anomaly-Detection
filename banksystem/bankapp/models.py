from django.db import models
from __future__ import unicode_literals

# Create your models here.
class branch(models.Model):
    name=models.CharField(max_length=200)
    address=models.CharField(max_length=200)
    branch_code=models.CharField(max_length=200)
    
    class Meta:
         verbose_name_plural = "Branches"
        
    