
from django.urls import path
from .views import *
from . import views
urlpatterns = [

     path("add/", CitizenCreateAPIView.as_view(), name="citizen-create-api"),
     path("get/<str:aadhaar_card>/", CitizenByAadhaarAPIView.as_view(), name="citizen-by-aadhaar"),
     path("citizen/<str:aadhaar>/pdf/", citizen_pdf),
     path("family/<str:aadhaar>/", views.get_family),
     path("fam/<str:aadhaar>/pdf/", views.family_pdf),
     
     
]