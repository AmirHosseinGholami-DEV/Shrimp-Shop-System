from django import forms
from django.core.exceptions import ValidationError

# Import models
from .models import ShrimpProduct, RequestsProduct
from authentication.models import ShrimpFarmingCompany


# =============================================================================
# COMPANY PROFILE VIEW-FORM (READ-ONLY DISPLAY)
# Used to show company details in dashboard with disabled inputs.
# Not for editing; intended for visual consistency in templates.
# =============================================================================

class CompanyEditForm(forms.Form):
    """
    Read-only form for displaying shrimp farming company profile information.
    
    All fields are disabled to prevent editing through this form.
    Used in dashboard templates where visual layout matters.
    """

    name = forms.CharField(
        max_length=255,
        label="نام شرکت",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'disabled': True
        })
    )

    manager_name = forms.CharField(
        max_length=255,
        label="نام مدیرعامل",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'disabled': True
        })
    )

    city = forms.CharField(
        max_length=255,
        label="شهر محل فعالیت",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'disabled': True
        })
    )

    phone = forms.CharField(
        max_length=15,
        label="شماره تلفن",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'disabled': True
        })
    )

    address = forms.CharField(
        label="آدرس دقیق",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'disabled': True,
            'rows': 3
        })
    )

    logo = forms.ImageField(
        required=False,
        label="تغییر لوگوی شرکت",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'disabled': True
        })
    )


# =============================================================================
# PRODUCT CREATION FORM
# For adding new shrimp products by farming companies.
# Includes placeholder hints and proper styling.
# =============================================================================

class ShrimpProductForm(forms.ModelForm):
    """
    Form for creating or updating a shrimp product listing.
    
    Fields:
        - product_name: Name of the product (e.g., "Grade A Tiger Shrimp")
        - weight: Total available weight in kilograms
        - shrimp_type: Species or type (e.g., Whiteleg, Tiger)
        - price: Unit price per kilogram
    """

    class Meta:
        model = ShrimpProduct
        fields = ['product_name', 'weight', 'shrimp_type', 'price']
        widgets = {
            'product_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: میگو ببری درجه یک'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: 500'
            }),
            'shrimp_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: ببری'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: 250000'
            }),
        }


# =============================================================================
# PRODUCT REQUEST FORM
# Validates support_code against existing ShrimpProduct entries.
# Ensures only valid product codes can be requested.
# =============================================================================

class RequestsProductForm(forms.ModelForm):
    """
    Custom form for purchase requests from exporting companies.
    
    Adds validation on 'support_code' to ensure it exists in ShrimpProduct.
    Prevents submission with invalid or non-existent codes.
    """

    support_code = forms.CharField(
        label="کد پشتیبانی محصول",
        help_text="لطفاً یک کد پشتیبانی معتبر وارد کنید.",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'کد 8 رقمی یا حروفی را وارد کنید'
        })
    )

    def clean_support_code(self):
        """
        Validate that the entered support code exists in ShrimpProduct.
        Raises ValidationError if not found.
        """
        support_code = self.cleaned_data['support_code']
        if not ShrimpProduct.objects.filter(support_code=support_code).exists():
            raise ValidationError("کد پشتیبانی وارد شده معتبر نیست.")
        return support_code

    class Meta:
        model = RequestsProduct
        fields = '__all__'
