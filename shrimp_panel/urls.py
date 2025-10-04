from django.urls import path
from . import views


# URL configuration for the shrimp farming company dashboard
# Handles product management, request handling, and authentication.
# Grouped by functionality for better maintainability.

urlpatterns = [
    # -------------------------------------------------------------------------
    # Dashboard & Profile
    # Main info page and session management
    # -------------------------------------------------------------------------

    path(
        route='dashboard/info/',
        view=views.ShrimpDashboardView.as_view(),
        name='shrimp_dashboard_info'
    ),

    path(
        route='dashboard/logout/',
        view=views.CompanyLogoutView.as_view(),
        name='shrimp_dashboard_company_logout'
    ),


    # -------------------------------------------------------------------------
    # Product Management
    # CRUD operations for shrimp products
    # -------------------------------------------------------------------------

    path(
        route='dashboard/add_product/',
        view=views.AddProductView.as_view(),
        name='shrimp_dashboard_add_product'
    ),

    path(
        route='dashboard/products/',
        view=views.RegisteredProductsView.as_view(),
        name='shrimp_dashboard_registered_products'
    ),

    path(
        route='dashboard/edit-product/<int:product_id>/',
        view=views.EditProductView.as_view(),
        name='shrimp_dashboard_edit_product'
    ),

    path(
        route='dashboard/delete-product/<int:product_id>/',
        view=views.DeleteProductView.as_view(),
        name='shrimp_dashboard_delete_product'
    ),


    # -------------------------------------------------------------------------
    # Request Management
    # Handle purchase requests from exporting companies
    # -------------------------------------------------------------------------

    path(
        route='dashboard/requests/',
        view=views.RequestsListView.as_view(),
        name='shrimp_dashboard_requests_list'
    ),

    path(
        route='dashboard/request/confirm/<int:pk>/',
        view=views.confirm_request,
        name='shrimp_dashboard_request_confirm'
    ),

    path(
        route='dashboard/request/reject/<int:pk>/',
        view=views.reject_request,
        name='shrimp_dashboard_request_reject'
    ),

    path(
        route='dashboard/request/delete/<int:pk>/',
        view=views.delete_request,
        name='shrimp_dashboard_request_delete'
    ),
]