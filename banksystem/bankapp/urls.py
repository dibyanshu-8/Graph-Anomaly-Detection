from django.conf.urls import url 

from .views import (
    BranchesAPIView,
    BanksAPIView,
)

urlpatterns = [
    url(r'^branches/',BranchesAPIView.as_view(),name='branches'),
    url(r'^banks',BanksAPIView.as_view(),name='banks'),
]
