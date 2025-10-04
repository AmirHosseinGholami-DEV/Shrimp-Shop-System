from django.urls import path
from .views import (
    ExportDashboardView,
    ExporterPurchasedView,
    CreatePackageView,
    CompanyLogoutView,
)

# URL patterns for the export company dashboard section
urlpatterns = [
    # Dashboard main info page
    path(
        route='dashboard/info/',
        view=ExportDashboardView.as_view(),
        name='export_dashboard_info'
    ),

    # Purchased products tracking
    path(
        route='dashboard/purchased/',
        view=ExporterPurchasedView.as_view(),
        name='export_dashboard_purchased'
    ),

    # Create new product package with QR code generation
    path(
        route='dashboard/create-product-package/',
        view=CreatePackageView.as_view(),
        name='export_dashboard_create_product_package'
    ),

    # Logout and session cleanup
    path(
        route='dashboard/logout/',
        view=CompanyLogoutView.as_view(),
        name='export_dashboard_company_logout'
    ),
]