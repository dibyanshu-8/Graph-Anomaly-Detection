from django.conf.urls import url 

from .views import (
    BanksAPIView,
)

urlpatterns = [
    url(r'^banks',BanksAPIView.as_view(),name='banks'),
]
