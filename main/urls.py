
from django.urls import path
from .views import *
urlpatterns = [

     path("add/", CitizenCreateAPIView.as_view(), name="citizen-create-api"),
     path("get/<str:aadhaar_card>/", CitizenByAadhaarAPIView.as_view(), name="citizen-by-aadhaar"),
]