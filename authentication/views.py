from django.views import View
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .forms import ShrimpFarmingCompanyForm, ExportingCompanyForm
from .models import ShrimpFarmingCompany, ExportingCompany


# =============================================================================
# COMPANY REGISTRATION VIEW
# Unified registration endpoint for both shrimp farming and exporting companies.
# Handles multi-form submission on a single page using distinct submit buttons.
# =============================================================================

class CompanyRegisterView(View):
    """
    Handle company registration for both ShrimpFarmingCompany and ExportingCompany.
    
    Features:
    - Single-page dual form support
    - Submission detection via unique button names
    - User-friendly feedback with Django messages
    - File upload support (e.g., logo)
    
    Template: templates/auth/register.html
    """

    template_name = "auth/register.html"

    def get(self, request):
        """Render the registration page with fresh forms."""
        return render(request, self.template_name)

    def post(self, request):
        """
        Process form submission based on which 'submit' button was clicked.
        
        Uses hidden name attributes in submit buttons to determine intent:
            - 'shrimp_submit' → ShrimpFarmingCompanyForm
            - 'export_submit'  → ExportingCompanyForm
        """
        # Handle Shrimp Farming Company Registration
        if "shrimp_submit" in request.POST:
            form = ShrimpFarmingCompanyForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "شرکت پرورش میگو با موفقیت ثبت شد")
                return redirect("register")
            else:
                messages.error(request, "خطا در ثبت اطلاعات. لطفاً موارد را بررسی کنید.")
                return render(request, self.template_name, {"shrimp_form": form})

        # Handle Exporting Company Registration
        elif "export_submit" in request.POST:
            form = ExportingCompanyForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "شرکت صادرکننده میگو با موفقیت ثبت شد")
                return redirect("register")
            else:
                messages.error(request, "خطا در ثبت اطلاعات. لطفاً موارد را بررسی کنید.")
                return render(request, self.template_name, {"export_form": form})

        # No valid submission detected
        messages.error(request, "هیچ فرمی ارسال نشده است")
        return redirect("register")


# =============================================================================
# COMPANY LOGIN VIEW
# Secure authentication for two types of companies using phone & password.
# Stores session data upon successful login for dashboard personalization.
# 
# WARNING: Plain-text password check is insecure. Future upgrade recommended.
# =============================================================================

class CompanyLoginView(View):
    """
    Authenticate companies based on phone number and plain password.
    
    Supports two user types:
        - 'shrimp': Redirects to shrimp_dashboard_info
        - 'export': Redirects to export_dashboard_info
    
    Session stores:
        - company_id
        - company_type
        - company_name
        - optional 'next_url' for post-login redirection
    
    Template: templates/auth/login.html
    """

    template_name = "auth/login.html"

    def get(self, request):
        """Store 'next' URL if provided and render login page."""
        next_url = request.GET.get("next")
        if next_url:
            request.session["next_url"] = next_url  # For post-login redirect
        return render(request, self.template_name)

    def post(self, request):
        """Authenticate company by phone number and password."""
        phone_number = request.POST.get("phone_number")
        password = request.POST.get("password")
        login_type = request.POST.get("login_type")

        # Debug logging (remove in production)
        print(f"Login Attempt - Phone: {phone_number}, Type: {login_type}")

        # Try logging in as Shrimp Farming Company
        if login_type == "shrimp":
            company = ShrimpFarmingCompany.objects.filter(
                phone_number=phone_number, password=password
            ).first()
            if company:
                request.session["company_id"] = company.id
                request.session["company_type"] = "shrimp"
                request.session["company_name"] = company.company_name
                return redirect("shrimp_dashboard_info")

        # Try logging in as Exporting Company
        elif login_type == "export":
            company = ExportingCompany.objects.filter(
                phone_number=phone_number, password=password
            ).first()
            if company:
                request.session["company_id"] = company.id
                request.session["company_type"] = "export"
                request.session["company_name"] = company.company_name
                return redirect("export_dashboard_info")

        # Authentication failed
        print("Failed login attempt with credentials:", phone_number, password)
        print("All Shrimp Companies:", list(ShrimpFarmingCompany.objects.values_list("phone_number", "password")))
        print("All Export Companies:", list(ExportingCompany.objects.values_list("phone_number", "password")))

        return HttpResponse("شماره تلفن یا رمز عبور اشتباه است")