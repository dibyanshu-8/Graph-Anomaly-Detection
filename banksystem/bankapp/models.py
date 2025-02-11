from django.db import models
from __future__ import unicode_literals

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

        
    