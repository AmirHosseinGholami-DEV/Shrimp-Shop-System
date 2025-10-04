from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from authentication.models import ExportingCompany
from shrimp_panel.models import ShrimpProduct, RequestsProduct
from .models import ProductPackage
from .forms import CompanyEditForm
from django.conf import settings


# =============================================================================
# EXPORT DASHBOARD: COMPANY PROFILE MANAGEMENT
# Handles viewing and editing company information for exporting companies.
# =============================================================================

class ExportDashboardView(View):
    """
    Display and edit profile information for the logged-in exporting company.
    Retrieves data from session and populates form with current details.
    """

    template_name = "admin/Export Panel/Compnay Info.html"

    def get_company_from_session(self, request):
        """
        Retrieve exporting company instance from session.
        Returns None if not authenticated or invalid type.
        """
        company_id = request.session.get('company_id')
        company_type = request.session.get('company_type')

        if company_id and company_type == 'export':
            try:
                return ExportingCompany.objects.get(id=company_id)
            except ExportingCompany.DoesNotExist:
                return None
        return None

    def get(self, request):
        """Render company info page with pre-filled edit form."""
        company = self.get_company_from_session(request)
        if not company:
            messages.error(request, "لطفاً ابتدا وارد سیستم شوید.")
            return redirect('login')

        initial_data = {
            'name': company.company_name,
            'manager_name': company.ceo_name,
            'city': company.location,
            'phone': company.phone_number,
            'address': company.address,
        }
        company_form = CompanyEditForm(initial=initial_data)

        default_logo_url = f"{settings.STATIC_URL}Static Home/images/logo-sample-2.png"

        return render(request, self.template_name, {
            'company': company,
            'company_form': company_form,
            'default_logo_url': default_logo_url,
        })

    def post(self, request):
        """Handle company profile update."""
        company = self.get_company_from_session(request)
        if not company:
            messages.error(request, "لطفاً ابتدا وارد سیستم شوید.")
            return redirect('login')

        if 'edit_company' in request.POST:
            company.company_name = request.POST.get('name', '')
            company.ceo_name = request.POST.get('manager_name', '')
            company.location = request.POST.get('city', '')
            company.phone_number = request.POST.get('phone', '')
            company.address = request.POST.get('address', '')

            if 'logo' in request.FILES:
                company.logo = request.FILES['logo']

            company.save()
            messages.success(request, "اطلاعات شرکت با موفقیت ویرایش شد.")

        return redirect('export_dashboard_info')


# =============================================================================
# EXPORT DASHBOARD: PURCHASED PRODUCTS VIEW
# Displays a list of approved product requests for the exporting company.
# =============================================================================

class ExporterPurchasedView(View):
    """
    Show all approved product requests for the exporting company.
    Used to track purchased inventory before packaging.
    """

    template_name = 'admin/Export Panel/Company Purchased.html'

    def get(self, request):
        """Fetch and display approved product requests."""
        company_id = request.session.get('company_id')
        if not company_id:
            return redirect('login')

        try:
            company = ExportingCompany.objects.get(id=company_id)
        except ExportingCompany.DoesNotExist:
            return redirect('login')

        approved_requests = RequestsProduct.objects.filter(
            buyer_company=company,
            status='approved'
        ).select_related('product', 'owner_company').order_by('-created_at')

        return render(request, self.template_name, {
            'approved_requests': approved_requests,
            'company': company,
            'company_logo': company.logo.url if company.logo else None,
        })


# =============================================================================
# EXPORT DASHBOARD: PRODUCT PACKAGE CREATION
# Allows exporter to split purchased product into packages with QR codes.
# Ensures stock availability and updates inventory atomically.
# =============================================================================

class CreatePackageView(View):
    """
    Handle creation of product packages from purchased shrimp products.
    
    Features:
    - Validates available weight
    - Creates ProductPackage instance
    - Updates remaining product weight
    - Generates QR code automatically
    - Shows summary after creation
    """

    template_name = 'admin/Export Panel/Company QR Code.html'

    def get_company_from_session(self, request):
        """
        Retrieve exporting company from session.
        Centralized method used across multiple views.
        """
        company_id = request.session.get('company_id')
        company_type = request.session.get('company_type')

        if company_id and company_type == 'export':
            try:
                return ExportingCompany.objects.get(id=company_id)
            except ExportingCompany.DoesNotExist:
                return None
        return None

    def get(self, request):
        """Display available products for packaging."""
        company = self.get_company_from_session(request)
        if not company:
            messages.error(request, "لطفاً ابتدا وارد سیستم شوید.")
            return redirect('login')

        purchased_products = ShrimpProduct.objects.filter(
            requests__buyer_company=company,
            requests__status='approved'
        ).distinct()

        return render(request, self.template_name, {
            'purchased_products': purchased_products,
            'show_results': False,
            'company_logo': company.logo.url if company.logo else None,
        })

    def post(self, request):
        """Process package creation with validation and atomic update."""
        company = self.get_company_from_session(request)
        if not company:
            messages.error(request, "لطفاً ابتدا وارد سیستم شوید.")
            return redirect('login')

        shrimp_product_id = request.POST.get('shrimp_product')
        if not shrimp_product_id:
            messages.error(request, "محصولی انتخاب نشده است.")
            return redirect('export_dashboard_create_product_package')

        try:
            package_weight = Decimal(request.POST.get('package_weight', '0'))
            package_count = int(request.POST.get('package_count', '0'))

            if package_weight <= 0 or package_count <= 0:
                messages.error(request, "وزن یا تعداد بسته‌ها باید بیشتر از صفر باشد.")
                return redirect('export_dashboard_create_product_package')

            shrimp_product = ShrimpProduct.objects.get(id=shrimp_product_id)
            total_weight_needed = package_weight * Decimal(package_count)

            if total_weight_needed > shrimp_product.weight:
                messages.error(
                    request,
                    f"موجودی محصول کافی نیست. موجودی فعلی: {shrimp_product.weight} Kg"
                )
                return redirect('export_dashboard_create_product_package')

            original_weight = shrimp_product.weight

            with transaction.atomic():
                # Create the package
                package = ProductPackage.objects.create(
                    shrimp_product=shrimp_product,
                    farming_company=shrimp_product.company,
                    exporting_company=company,
                    package_weight=package_weight,
                    quantity=package_count,
                    production_date=timezone.now().date(),
                    expiration_date=timezone.now().date() + timezone.timedelta(days=365),
                )

                # Deduct used weight
                shrimp_product.weight -= total_weight_needed
                shrimp_product.save()

            remaining_weight = shrimp_product.weight

            # Re-fetch updated product list
            updated_products = ShrimpProduct.objects.filter(
                requests__buyer_company=company,
                requests__status='approved'
            ).distinct()

            return render(request, self.template_name, {
                'show_results': True,
                'package': package,
                'package_count': package_count,
                'package_weight': package_weight,
                'total_weight': total_weight_needed,
                'original_weight': original_weight,
                'remaining_weight': remaining_weight,
                'purchased_products': updated_products,
                'company_logo': company.logo.url if company.logo else None,
            })

        except ShrimpProduct.DoesNotExist:
            messages.error(request, "محصول انتخاب شده یافت نشد.")
        except (ValueError, Decimal.InvalidOperation):
            messages.error(request, "مقادیر وارد شده نامعتبر هستند.")
        except Exception as e:
            messages.error(request, f"خطا در ایجاد بسته‌ها: {str(e)}")

        return redirect('export_dashboard_create_product_package')


# =============================================================================
# AUTHENTICATION: LOGOUT HANDLER
# Clears session and redirects to login page.
# =============================================================================

class CompanyLogoutView(View):
    """
    Log out the currently authenticated company.
    Clears all session data and shows success message.
    """

    def get(self, request):
        """Flush session and redirect to login."""
        request.session.flush()
        messages.success(request, "با موفقیت از سیستم خارج شدید.")
        return redirect('login')