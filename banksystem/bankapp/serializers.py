from rest_framework import serializers

from .models import *

class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields=('__all__')
        
        
class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model= Branch
        fields=('__all__')
        read_only_fields = ('id',)

        
class BranchDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ('__all__')