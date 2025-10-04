from django.urls import path
from .views import (
    CompanyRegisterView,
    CompanyLoginView,
)

# URL configuration for company authentication
# Handles registration and login for both shrimp farming and exporting companies
urlpatterns = [
    # Registration endpoint for new companies
    path(
        route='register/',
        view=CompanyRegisterView.as_view(),
        name='register'
    ),

    # Login endpoint with type-based authentication (shrimp/export)
    path(
        route='login/',
        view=CompanyLoginView.as_view(),
        name='login'
    ),
]