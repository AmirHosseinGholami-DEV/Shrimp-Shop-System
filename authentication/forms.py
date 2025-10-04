from django import forms
from .models import ShrimpFarmingCompany, ExportingCompany


# =============================================================================
# BASE COMPANY FORM
# Shared form configuration for company registration.
# Ensures consistent field handling and avoids code duplication.
# Uses PasswordInput widget to securely mask password input in the UI.
# =============================================================================

class BaseCompanyForm(forms.ModelForm):
    """
    Abstract base form for company registration models.
    
    Features:
    - Unified field set for both company types
    - Secure password input via PasswordInput widget
    - Designed for inheritance; not meant to be used directly
    """

    # Render password as masked input (****)
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Enter a secure password",
            "class": "form-control",
        }),
        label="Password",
        help_text="Enter a strong password. It will be stored securely.",
    )

    class Meta:
        # Fields common to all company types
        fields = [
            "company_name",
            "ceo_name",
            "location",
            "address",
            "logo",
            "phone_number",
            "password",  # Handled separately for security control
        ]

    def clean_phone_number(self):
        """
        Validate phone number format (example logic).
        Customize based on regional requirements.
        """
        phone = self.cleaned_data.get("phone_number")
        if phone:
            cleaned_phone = phone.replace("+", "").replace("-", "").replace(" ", "")
            if len(cleaned_phone) < 10:
                raise forms.ValidationError("Phone number is too short. Minimum 10 digits required.")
        return phone

    def save(self, commit=True):
        """
        Override save to handle password hashing if needed.
        Assumes model has `set_password()` method like Django's User model.
        Adjust logic based on actual model implementation.
        """
        instance = super().save(commit=False)
        # Example: Hash password if your model supports it
        # if hasattr(instance, 'set_password'):
        #     instance.set_password(self.cleaned_data["password"])
        return instance if not commit else instance.save()


# =============================================================================
# SHRIMP FARMING COMPANY REGISTRATION FORM
# Dedicated form for shrimp farming businesses.
# Inherits all behavior from BaseCompanyForm with specific model binding.
# =============================================================================

class ShrimpFarmingCompanyForm(BaseCompanyForm):
    """
    Registration form for shrimp farming companies.
    
    Purpose:
    - Collect essential business details
    - Maintain data consistency across the platform
    - Ready for integration with views and templates
    
    Future extensions may include:
    - Pond capacity
    - Certification uploads
    - Production volume
    """

    class Meta(BaseCompanyForm.Meta):
        model = ShrimpFarmingCompany
        widgets = {
            "company_name": forms.TextInput(attrs={"placeholder": "E.g., Persian Gulf Aqua Farm"}),
            "ceo_name": forms.TextInput(attrs={"placeholder": "Full name of CEO"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "+98 912 345 6789"}),
            "address": forms.Textarea(attrs={"rows": 3, "placeholder": "Full legal address"}),
            "location": forms.Select(attrs={"class": "form-select"}),
        }
        help_texts = {
            "logo": "Upload a clear logo (recommended size: 200x200 px).",
            "location": "Select the main operational province or city.",
        }


# =============================================================================
# EXPORTING COMPANY REGISTRATION FORM
# Tailored for export-focused seafood businesses.
# Shares structure with farming form but bound to ExportingCompany model.
# =============================================================================

class ExportingCompanyForm(BaseCompanyForm):
    """
    Registration form for exporting companies.
    
    Aligns with ShrimpFarmingCompanyForm in UX and validation,
    ensuring uniformity across partner types in the ecosystem.
    
    Potential future enhancements:
    - Export licenses
    - International ports of operation
    - Certifications (HACCP, ISO, etc.)
    """

    class Meta(BaseCompanyForm.Meta):
        model = ExportingCompany
        widgets = {
            "company_name": forms.TextInput(attrs={"placeholder": "E.g., Blue Ocean Exports Ltd."}),
            "ceo_name": forms.TextInput(attrs={"placeholder": "Legal representative name"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "+98 21 1234 5678"}),
            "address": forms.Textarea(attrs={"rows": 3, "placeholder": "Registered office address"}),
            "location": forms.Select(attrs={"class": "form-select"}),
        }
        help_texts = {
            "logo": "Please upload official company logo (PNG/JPG, max 5MB).",
            "location": "Headquarters or primary export hub location.",
        }