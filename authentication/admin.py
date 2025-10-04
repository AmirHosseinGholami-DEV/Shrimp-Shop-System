from django.contrib import admin
from .models import ShrimpFarmingCompany, ExportingCompany


# =============================================================================
# BASE ADMIN CONFIGURATION FOR COMPANY MODELS
# Shared functionality for company-related admin panels to ensure consistency
# and reduce code duplication.
# =============================================================================

class BaseCompanyAdmin(admin.ModelAdmin):
    """
    Abstract base admin class to standardize the display and behavior
    of company models in the Django admin interface.

    Features:
    - Search by key fields
    - Filter by location and timestamps
    - Read-only access to auto-generated timestamps
    - Organized field layout with collapsible metadata section
    """

    # Fields displayed in the admin list view
    list_display = (
        "company_name",
        "ceo_name",
        "location",
        "phone_number",
        "created_at",
        "updated_at",
    )

    # Enable search across critical business fields
    search_fields = ("company_name", "ceo_name", "location", "phone_number")

    # Add filtering sidebar for location and date-based fields
    list_filter = ("location", "created_at", "updated_at")

    # Prevent manual editing of auto-managed timestamp fields
    readonly_fields = ("created_at", "updated_at")

    # Structured form layout with logical grouping
    fieldsets = (
        (
            "Company Information",
            {
                "fields": (
                    "company_name",
                    "ceo_name",
                    "location",
                    "address",
                    "logo",
                    "phone_number",
                    "password",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),  # Hide by default for cleaner UI
            },
        ),
    )


# =============================================================================
# SPECIFIC ADMIN CLASSES
# Reuse shared configuration while maintaining model-specific customization.
# Currently identical, but easily extensible if future needs diverge.
# =============================================================================

@admin.register(ShrimpFarmingCompany)
class ShrimpFarmingCompanyAdmin(BaseCompanyAdmin):
    """
    Admin interface for ShrimpFarmingCompany model.
    Inherits all configurations from BaseCompanyAdmin for consistency.
    Can be extended later for farming-specific features (e.g., pond count, yield).
    """
    pass  # Using inherited behavior; no overrides needed yet


@admin.register(ExportingCompany)
class ExportingCompanyAdmin(BaseCompanyAdmin):
    """
    Admin interface for ExportingCompany model.
    Shares the same core structure as ShrimpFarmingCompany, ensuring uniform UX.
    Ready for export-specific enhancements like certifications or partner regions.
    """
    pass  # Using inherited behavior; no overrides needed yet