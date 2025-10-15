import uuid
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.utils import timezone

# Import models
from .models import ShrimpProduct, RequestsProduct
from authentication.models import ShrimpFarmingCompany, ExportingCompany
from .forms import RequestsProductForm


# =============================================================================
# ADMIN: SHRIMP PRODUCT MANAGEMENT
# Handles display and management of shrimp product listings.
# Automatically generates support code on creation.
# =============================================================================

@admin.register(ShrimpProduct)
class ShrimpProductAdmin(admin.ModelAdmin):
    """
    Admin interface for ShrimpProduct model.
    
    Features:
    - Displays key product details including company, weight, price
    - Filters by company, shrimp type, and date
    - Searchable by name, company, and support code
    - Auto-generates 8-character UUID as support_code if missing
    """

    # Fields shown in the list view
    list_display = [
        'product_name',
        'company',
        'weight',
        'shrimp_type',
        'price',
        'support_code',
        'created_at'
    ]

    # Sidebar filters
    list_filter = [
        'company',
        'shrimp_type',
        'created_at'
    ]

    # Search across critical fields
    search_fields = [
        'product_name',
        'company__company_name',
        'support_code'
    ]

    # Default ordering: newest first
    ordering = ['-created_at']

    # Prevent manual editing of auto-generated fields
    readonly_fields = ['support_code', 'created_at']

    # Form layout with collapsible system section
    fieldsets = (
        (None, {
            'fields': ('company', 'product_name', 'weight', 'shrimp_type', 'price')
        }),
        ('System Information', {
            'fields': ('support_code', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        Generate a unique support code before saving if not already set.
        Uses first 8 characters of a UUID4.
        """
        if not obj.support_code:
            obj.support_code = str(uuid.uuid4())[:8].upper()
        super().save_model(request, obj, form, change)


# =============================================================================
# ADMIN: PRODUCT REQUESTS MANAGEMENT
# Manages purchase requests from exporters to farming companies.
# Displays related data via custom methods and uses autocomplete for FKs.
# =============================================================================

@admin.register(RequestsProduct)
class RequestsProductAdmin(admin.ModelAdmin):
    """
    Admin interface for RequestsProduct model.
    
    Shows purchase requests made by exporting companies.
    Includes product details, buyer/seller info, and status tracking.
    Supports filtering, searching, and inline editing.
    """

    form = RequestsProductForm  # Use custom form for validation and UX

    # Display fields in admin list
    list_display = [
        'support_code',
        'buyer_company_name',
        'product_name',
        'weight',
        'owner_company_name',
        'status',
        'operation_date',
    ]

    # Filters for quick navigation
    list_filter = [
        'status',
        'operation_date',
        'buyer_company',
        'owner_company',
    ]

    # Search across names, codes, and relationships
    search_fields = [
        'support_code',
        'buyer_company__company_name',
        'product__product_name',
        'owner_company__company_name',
    ]

    # Prevent direct edit of timestamp
    readonly_fields = ['operation_date']

    # Enable autocomplete for foreign key fields
    autocomplete_fields = [
        'buyer_company',
        'product',
        'owner_company',
    ]

    def buyer_company_name(self, obj):
        """Display the name of the buying company."""
        return obj.buyer_company.company_name
    buyer_company_name.short_description = 'شرکت خریدار'
    buyer_company_name.admin_order_field = 'buyer_company__company_name'

    def product_name(self, obj):
        """Display the requested product's name."""
        return obj.product.product_name
    product_name.short_description = 'نام محصول'
    product_name.admin_order_field = 'product__product_name'

    def weight(self, obj):
        """Display the weight of the requested product."""
        return f"{obj.product.weight} Kg"
    weight.short_description = 'وزن محصول (کیلوگرم)'
    weight.admin_order_field = 'product__weight'

    def owner_company_name(self, obj):
        """Display the name of the product owner (farming) company."""
        return obj.owner_company.company_name
    owner_company_name.short_description = 'شرکت صاحب محصول'
    owner_company_name.admin_order_field = 'owner_company__company_name'

    def save_model(self, request, obj, form, change):
        """
        Ensure support_code is preserved or inherited during save.
        Uses cleaned data from the custom form.
        """
        obj.support_code = form.cleaned_data.get('support_code', obj.support_code)
        super().save_model(request, obj, form, change)
