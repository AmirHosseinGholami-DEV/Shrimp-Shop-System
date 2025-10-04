import os
from django.db import models
from django.utils import timezone

def company_logo_path(instance, filename):
    """
    Generates the upload path for the company logo based on the company type.
    """
    # Determine the company type and use it as the folder name
    if isinstance(instance, ShrimpFarmingCompany):
        company_type = "ShrimpFarmingCompany"
    elif isinstance(instance, ExportingCompany):
        company_type = "ExportingCompany"
    else:
        raise ValueError("Unknown company type")

    # Return the full path including the company type folder
    return os.path.join("logos", company_type, filename)

class CompanyInfoAbstract(models.Model):
    """
    Abstract base class representing common fields for both shrimp farming and exporting companies.
    """
    company_name = models.CharField(max_length=255, verbose_name="Company Name")
    ceo_name = models.CharField(max_length=255, verbose_name="CEO Name")
    location = models.CharField(max_length=255, verbose_name="Location")
    address = models.TextField(verbose_name="Company Address")
    logo = models.ImageField(
        upload_to=company_logo_path, null=True, blank=True, verbose_name="Company Logo"
    )
    phone_number = models.CharField(max_length=15, verbose_name="Phone Number")
    password = models.CharField(max_length=128, verbose_name="Password")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        abstract = True

class ShrimpFarmingCompany(CompanyInfoAbstract):
    """
    Model representing a shrimp farming company, inheriting common fields from CompanyInfoAbstract.
    """
    class Meta:
        verbose_name = "Shrimp Farming Company"
        verbose_name_plural = "Shrimp Farming Companies"

    def __str__(self):
        return self.company_name

class ExportingCompany(CompanyInfoAbstract):
    """
    Model representing an exporting company, inheriting common fields from CompanyInfoAbstract.
    """
    class Meta:
        verbose_name = "Exporting Company"
        verbose_name_plural = "Exporting Companies"

    def __str__(self):
        return self.company_name