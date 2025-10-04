import os
import qrcode
import uuid
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from decimal import Decimal
from authentication.models import ShrimpFarmingCompany, ExportingCompany
from shrimp_panel.models import ShrimpProduct


def qr_code_path(instance, filename):
    """
    Define upload path for QR code images.
    Example: 'qrcodes/BATCH_A1B2C3D4E5_qr.png'
    """
    return os.path.join("qrcodes", f"{instance.batch_number}_{filename}")

def default_expiration_date():
    """
    Default expiration date = today + 365 days
    """
    return timezone.now().date() + timezone.timedelta(days=365)


class ProductPackage(models.Model):
    """
    Represents a packaged batch of shrimp product ready for export.

    Each package is linked to:
        - A shrimp product (type, weight, price)
        - A farming company (origin)
        - An exporting company (distributor)

    Automatically generates a unique batch number and QR code containing
    traceability data upon creation.
    """

    shrimp_product = models.ForeignKey(
        ShrimpProduct,
        on_delete=models.CASCADE,
        related_name="packages"
    )
    farming_company = models.ForeignKey(
        ShrimpFarmingCompany,
        on_delete=models.CASCADE,
        verbose_name="Farming Company"
    )
    exporting_company = models.ForeignKey(
        ExportingCompany,
        on_delete=models.CASCADE,
        verbose_name="Exporting Company"
    )
    package_weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Package Weight (Kg)"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Number of Packages"
    )
    production_date = models.DateField(
        verbose_name="Production Date",
        default=timezone.now
    )
    expiration_date = models.DateField(
        verbose_name="Expiration Date",
        default=default_expiration_date  
    )
    batch_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Batch Number"
    )
    qr_code = models.ImageField(
        upload_to=qr_code_path,
        blank=True,
        verbose_name="QR Code"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product Package"
        verbose_name_plural = "Product Packages"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.batch_number} - {self.shrimp_product.product_name} (Quantity: {self.quantity})"

    def save(self, *args, **kwargs):
        """
        Override save to auto-generate:
            - Batch number (if missing)
            - Production date (if missing)
            - Expiration date (if missing)
            - QR code (if not already generated)
        """
        if not self.batch_number:
            self.batch_number = f"BATCH-{uuid.uuid4().hex[:10].upper()}"

        if not self.production_date:
            self.production_date = timezone.now().date()

        if not self.expiration_date:
            self.expiration_date = self.production_date + timezone.timedelta(days=365)

        super().save(*args, **kwargs)

        # Generate QR code only if it doesn't exist
        if not self.qr_code:
            self.generate_qr_code()

    def generate_qr_code(self):
        """
        Generate a QR code containing full traceability information about this package.
        The QR code is saved to the filesystem and linked to the model instance.
        """
        total_weight = self.package_weight * self.quantity

        qr_data = f"""
        اطلاعات بسته محصول:
        شماره بچ: {self.batch_number}
        محصول: {self.shrimp_product.product_name}
        نوع میگو: {self.shrimp_product.shrimp_type}
        شرکت پرورش‌دهنده: {self.farming_company.company_name}
        شرکت صادرکننده: {self.exporting_company.company_name}
        وزن هر بسته: {self.package_weight} کیلوگرم
        تعداد بسته‌ها: {self.quantity}
        وزن کل: {total_weight} کیلوگرم
        تاریخ تولید: {self.production_date}
        تاریخ انقضا: {self.expiration_date}
        کد پشتیبانی: {self.shrimp_product.support_code}
        """.strip()

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f"qr_code_{self.batch_number}.png"

        # Save image to FileField
        self.qr_code.save(
            name=filename,
            content=ContentFile(buffer.getvalue()),
            save=False  # Prevent infinite loop
        )

        # Final save without triggering QR generation again
        super(ProductPackage, self).save(update_fields=['qr_code'])