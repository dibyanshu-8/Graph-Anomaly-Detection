from __future__ import unicode_literals

from django.shortcuts import render
from django.http import Http404

from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.views import APIView
# Create your views here.

from .models import*
from .serializers import*

class BanksAPIView(generics.ListCreateAPIView):
    queryset=Bank.objects.all()
    serializer_class=BankSerializer
    