from django.db import models

# Create your models here.
from django.db import models

class Name(models.Model):
    from django.db import models

class Citizen(models.Model):
    aadhaar_card = models.CharField(
        max_length=12,
        unique=True,
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    relation_name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )  # Son/Daughter/Wife of

    ward = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    gpu = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    district = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    coi = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )  # Certificate of Identity

    voter_id = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    bank_number = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    contact_no = models.CharField(
        max_length=15,
        null=True,
        blank=True
    )

    qualification = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    profession = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    home_category = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    professional_details = models.TextField(
        null=True,
        blank=True
    )

    land_details = models.TextField(
        null=True,
        blank=True
    )

    schemes_applied = models.TextField(
        null=True,
        blank=True
    )

    health_status = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name or "Citizen"

