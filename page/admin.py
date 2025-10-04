from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Admin interface for managing contact form messages.
    
    Displays user-submitted inquiries including name, email, subject, message,
    and status. Allows filtering by read/unread status and date. IP address
    and creation time are read-only for audit purposes.
    """

    # Fields displayed in the admin list view
    list_display = [
        'name',
        'email',
        'subject',
        'status',
        'created_at'
    ]

    # Filters available in the right sidebar
    list_filter = [
        'status',
        'created_at'
    ]

    # Searchable fields using the search bar
    search_fields = [
        'name',
        'email',
        'subject',
        'message'
    ]

    # Prevent editing of auto-generated or sensitive fields
    readonly_fields = [
        'created_at',
        'ip_address'
    ]

    # Default ordering: newest first
    ordering = ['-created_at']

    # Number of items per page
    list_per_page = 25

    # Enable quick edit directly in list view (optional)
    list_editable = ['status']