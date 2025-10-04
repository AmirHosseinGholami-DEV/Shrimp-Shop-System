from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

# Import models from respective apps
from authentication.models import ShrimpFarmingCompany, ExportingCompany
from shrimp_panel.models import ShrimpProduct
from .models import ProductPackage


@admin.register(ProductPackage)
class ProductPackageAdmin(admin.ModelAdmin):
    """
    Admin interface for ProductPackage model.
    
    Displays comprehensive information about packaged shrimp products,
    including product details, company information, QR code preview, and
    traceability data. Supports bulk QR code generation.
    """

    # Fields displayed in the admin list view
    list_display = [
        'batch_number',
        'product_name',
        'shrimp_type',
        'farming_company_name',
        'exporting_company_name',
        'package_weight',
        'total_product_weight',
        'production_date',
        'expiration_date',
        'qr_code_preview',
        'created_at',
    ]

    # Filters available in the right sidebar
    list_filter = [
        'production_date',
        'expiration_date',
        'farming_company',
        'exporting_company',
        'shrimp_product__shrimp_type',
        'created_at',
    ]

    # Searchable fields using the search bar
    search_fields = [
        'batch_number',
        'shrimp_product__product_name',
        'shrimp_product__support_code',
        'farming_company__company_name',
        'exporting_company__company_name',
    ]

    # Read-only fields in the edit form
    readonly_fields = [
        'batch_number',
        'qr_code_preview_large',
        'created_at',
        'updated_at',
        'product_details',
        'company_details',
        'total_product_weight_readonly',
    ]

    # Form layout with collapsible sections for better UX
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'batch_number',
                'shrimp_product',
                'package_weight',
                'total_product_weight_readonly',
            )
        }),
        ('Dates', {
            'fields': (
                'production_date',
                'expiration_date',
            )
        }),
        ('Companies', {
            'fields': (
                'farming_company',
                'exporting_company',
            )
        }),
        ('QR Code', {
            'fields': (
                'qr_code_preview_large',
                'qr_code',
            )
        }),
        ('Product Details', {
            'fields': ('product_details',),
            'classes': ('collapse',)
        }),
        ('Company Details', {
            'fields': ('company_details',),
            'classes': ('collapse',)
        }),
        ('System Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Number of items per page in the list view
    list_per_page = 25

    def get_queryset(self, request):
        """
        Optimize database queries by prefetching related objects.
        Prevents N+1 query problem when displaying list or detail views.
        """
        return super().get_queryset(request).select_related(
            'shrimp_product',
            'farming_company',
            'exporting_company'
        )

    # -------------------------------------------------------------------------
    # Custom Display Fields
    # These methods add computed or related fields to the admin interface.
    # -------------------------------------------------------------------------

    def product_name(self, obj):
        """Display the associated shrimp product name."""
        return obj.shrimp_product.product_name
    product_name.short_description = 'Product Name'
    product_name.admin_order_field = 'shrimp_product__product_name'

    def shrimp_type(self, obj):
        """Display the type of shrimp (e.g., Whiteleg, Tiger)."""
        return obj.shrimp_product.shrimp_type
    shrimp_type.short_description = 'Shrimp Type'
    shrimp_type.admin_order_field = 'shrimp_product__shrimp_type'

    def total_product_weight(self, obj):
        """Show total weight of the original product in kilograms."""
        return f"{obj.shrimp_product.weight} Kg"
    total_product_weight.short_description = 'Total Product Weight'
    total_product_weight.admin_order_field = 'shrimp_product__weight'

    def total_product_weight_readonly(self, obj):
        """Read-only version used in the form."""
        return f"{obj.shrimp_product.weight} Kg"
    total_product_weight_readonly.short_description = 'Total Product Weight'

    def farming_company_name(self, obj):
        """Display the name of the farming company."""
        return obj.farming_company.company_name
    farming_company_name.short_description = 'Farming Company'
    farming_company_name.admin_order_field = 'farming_company__company_name'

    def exporting_company_name(self, obj):
        """Display the name of the exporting company."""
        return obj.exporting_company.company_name
    exporting_company_name.short_description = 'Exporting Company'
    exporting_company_name.admin_order_field = 'exporting_company__company_name'

    def qr_code_preview(self, obj):
        """Small QR code preview in the list view."""
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="50" height="50" style="border: 1px solid #ddd; '
                'border-radius: 4px; padding: 2px;" />',
                obj.qr_code.url
            )
        return 'Not Generated'
    qr_code_preview.short_description = 'QR Code'

    def qr_code_preview_large(self, obj):
        """Large QR code preview in the detail view with batch info."""
        if obj.qr_code:
            return format_html(
                '<div style="text-align: center; margin: 15px 0; padding: 10px; '
                'border: 1px solid #e0e0e0; border-radius: 5px; background: #fafafa;">'
                '<img src="{}" width="200" height="200" style="border: 1px solid #ddd; '
                'border-radius: 4px; padding: 5px;" />'
                '<p style="margin-top: 10px; font-size: 12px;">Batch Number: {}</p>'
                '</div>',
                obj.qr_code.url, obj.batch_number
            )
        return 'QR Code will be generated after saving'
    qr_code_preview_large.short_description = 'QR Code Preview'

    def product_details(self, obj):
        """Render a styled table with full product information."""
        details = f"""
        <div style="font-family: system-ui, sans-serif;">
            <table style="width:100%; border-collapse: collapse; margin: 10px 0;">
                <thead>
                    <tr style="background-color: #f8f9fa;">
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: right; font-weight: bold;">Field</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: right; font-weight: bold;">Value</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td style="border: 1px solid #ddd; padding: 8px; text-align: right;">Product Name</td>
                        <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">{obj.shrimp_product.product_name}</td></tr>
                    <tr><td style="border: 1px solid #ddd; padding: 8px; text-align: right;">Shrimp Type</td>
                        <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">{obj.shrimp_product.shrimp_type}</td></tr>
                    <tr><td style="border: 1px solid #ddd; padding: 8px; text-align: right;">Total Weight</td>
                        <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">{obj.shrimp_product.weight} Kg</td></tr>
                    <tr><td style="border: 1px solid #ddd; padding: 8px; text-align: right;">Price</td>
                        <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">{obj.shrimp_product.price}</td></tr>
                    <tr><td style="border: 1px solid #ddd; padding: 8px; text-align: right;">Support Code</td>
                        <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">{obj.shrimp_product.support_code}</td></tr>
                    <tr><td style="border: 1px solid #ddd; padding: 8px; text-align: right;">Package Weight</td>
                        <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">{obj.package_weight} Kg</td></tr>
                </tbody>
            </table>
        </div>
        """
        return mark_safe(details)
    product_details.short_description = 'Product Details'

    def company_details(self, obj):
        """Render a styled table with farming and exporting company information."""
        details = f"""
        <div style="font-family: system-ui, sans-serif;">
            <table style="width:100%; border-collapse: collapse; margin: 10px 0;">
                <thead>
                    <tr style="background-color: #f8f9fa;">
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: right; font-weight: bold;">Company</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: right; font-weight: bold;">Details</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px; text-align: right; vertical-align: top;">Farming</td>
                        <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">
                            <strong>{obj.farming_company.company_name}</strong><br>
                            CEO: {obj.farming_company.ceo_name}<br>
                            Location: {obj.farming_company.location}<br>
                            Phone: {obj.farming_company.phone_number}
                        </td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px; text-align: right; vertical-align: top;">Exporting</td>
                        <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">
                            <strong>{obj.exporting_company.company_name}</strong><br>
                            CEO: {obj.exporting_company.ceo_name}<br>
                            Location: {obj.exporting_company.location}<br>
                            Phone: {obj.exporting_company.phone_number}
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        """
        return mark_safe(details)
    company_details.short_description = 'Company Details'

    # -------------------------------------------------------------------------
    # Actions
    # Custom admin actions that can be applied to selected objects.
    # -------------------------------------------------------------------------

    actions = ['generate_qr_codes']

    def generate_qr_codes(self, request, queryset):
        """
        Action to generate QR codes for selected product packages.
        Calls the model's generate_qr_code() method for each item.
        """
        updated_count = 0
        for package in queryset:
            package.generate_qr_code()
            updated_count += 1
        self.message_user(request, f"QR codes generated for {updated_count} package(s).")
    generate_qr_codes.short_description = "Generate QR Codes for Selected Packages"
