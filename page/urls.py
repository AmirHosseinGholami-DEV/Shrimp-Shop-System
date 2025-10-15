from django.urls import path
from . import views


# URL configuration for the main website frontend
# Handles public pages accessible to all users: home, about, contact, product listing,
# company info, and product request flow.

urlpatterns = [
    # Home page
    path(
        route='',
        view=views.HomeView.as_view(),
        name='home'
    ),

    # About us page
    path(
        route='about/',
        view=views.AboutView.as_view(),
        name='about'
    ),

    # Contact form page
    path(
        route='contact/',
        view=views.ContactView.as_view(),
        name='contact'
    ),

    # Product listing page
    path(
        route='product/',
        view=views.ProductView.as_view(),
        name='product'
    ),

    # Submit request for a specific product (by ID)
    path(
        route='request-product/<int:product_id>/',
        view=views.RequestProductView.as_view(),
        name='request_product'
    ),

    # Company overview page
    path(
        route='company/',
        view=views.CompanyView.as_view(),
        name='company'
    ),
]