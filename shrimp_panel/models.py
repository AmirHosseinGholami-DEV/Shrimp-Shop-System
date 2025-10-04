import uuid
from django.db import models

# Import related models
from authentication.models import ShrimpFarmingCompany, ExportingCompany


# =============================================================================
# MODEL: SHRIMP PRODUCT
# Represents a shrimp product listed by a farming company for sale or request.
# Automatically generates a unique support code on first save.
# =============================================================================

class ShrimpProduct(models.Model):
    """
    Model representing a shrimp product offered by a farming company.

    Contains product details such as name, weight, type, price, and a unique
    support code used by exporters to request the product.
    """

    # Link to the farming company that owns this product
    company = models.ForeignKey(
        ShrimpFarmingCompany,
        on_delete=models.CASCADE,
        related_name='products'
    )

    # Product identification and specifications
    product_name = models.CharField(max_length=255, verbose_name="Product Name")
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Weight (Kg)")
    shrimp_type = models.CharField(max_length=255, verbose_name="Shrimp Type")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Price")

    # Unique identifier for tracking and requests
    support_code = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name="Support Code"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Shrimp Product"
        verbose_name_plural = "Shrimp Products"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['support_code']),     # Speed up lookup by code
            models.Index(fields=['shrimp_type']),      # Improve filter performance
            models.Index(fields=['created_at']),       # Optimize date-based queries
        ]

    def save(self, *args, **kwargs):
        """
        Override save to auto-generate an 8-character uppercase UUID
        as support_code if not already set.
        """
        if not self.support_code:
            self.support_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} ({self.support_code})"


# =============================================================================
# MODEL: PRODUCT REQUEST
# Tracks purchase requests made by exporting companies to farming companies.
# Status can be pending, approved, or rejected.
# =============================================================================

class RequestsProduct(models.Model):
    """
    Model to track product purchase requests from exporting companies.

    Each request references a specific product via its support_code and includes
    buyer, owner, status, and timestamp. Used in approval workflows.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # Core request fields
    support_code = models.CharField(max_length=50, verbose_name="Support Code")
    buyer_company = models.ForeignKey(
        ExportingCompany,
        on_delete=models.CASCADE,
        related_name='requests',
        verbose_name="Buyer Company (Exporter)"
    )
    product = models.ForeignKey(
        ShrimpProduct,
        on_delete=models.CASCADE,
        related_name='requests',
        verbose_name="Requested Product"
    )
    owner_company = models.ForeignKey(
        ShrimpFarmingCompany,
        on_delete=models.CASCADE,
        related_name='owned_requests',
        verbose_name="Owner Company (Farming)"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Request Status"
    )
    operation_date = models.DateTimeField(auto_now_add=True, verbose_name="Operation Date")

    class Meta:
        verbose_name = "Product Request"
        verbose_name_plural = "Product Requests"
        ordering = ['-operation_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['support_code']),
            models.Index(fields=['operation_date']),
            models.Index(fields=['buyer_company']),
            models.Index(fields=['owner_company']),
        ]

    def __str__(self):
        return f"Request for {self.product.product_name} from {self.buyer_company.company_name}"