from django.db import models


class ContactMessage(models.Model):
    """
    Model to store contact form submissions from website visitors.

    Contains sender information, message content, status tracking,
    IP address for spam monitoring, and creation timestamp.
    Used in the admin panel for support team review.
    """

    # Status choices for message lifecycle tracking
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
    ]

    # Basic contact information
    name = models.CharField(
        max_length=100,
        verbose_name='Name'
    )
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='Phone'
    )

    # Message details
    subject = models.CharField(max_length=200, verbose_name='Subject')
    message = models.TextField(verbose_name='Message')

    # Internal tracking fields
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Status'
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='IP Address'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )

    class Meta:
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),           # Improve filter performance
            models.Index(fields=['created_at']),       # Speed up date-based queries
            models.Index(fields=['email']),            # Useful for user lookup
        ]

    def __str__(self):
        """String representation of the message in admin and logs."""
        return f"{self.name} - {self.subject}"

    def save(self, *args, **kwargs):
        """
        Override save method for future extensibility.
        Currently uses default behavior.

        Example extensions:
        - Trim whitespace from name/subject
        - Log IP geolocation
        - Trigger notification on new message
        """
        super().save(*args, **kwargs)
