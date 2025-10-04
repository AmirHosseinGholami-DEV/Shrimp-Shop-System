from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from authentication.models import ShrimpFarmingCompany
from .models import ShrimpProduct, RequestsProduct
from .forms import CompanyEditForm, ShrimpProductForm


# =============================================================================
# SHIMP DASHBOARD: COMPANY PROFILE VIEW
# Displays and allows editing of company information for shrimp farming companies.
# =============================================================================

class ShrimpDashboardView(View):
    """
    Render and handle updates to the shrimp farming company profile.
    Uses session to authenticate and retrieve company data.
    """
    template_name = "admin/Shrimp Panel/Compnay Info.html"

    def get_company_from_session(self, request):
        """Retrieve authenticated shrimp farming company from session."""
        company_id = request.session.get('company_id')
        company_type = request.session.get('company_type')

        if company_id and company_type == 'shrimp':
            try:
                return ShrimpFarmingCompany.objects.get(id=company_id)
            except ShrimpFarmingCompany.DoesNotExist:
                pass
        return None

    def get(self, request):
        """Display company info form with current data."""
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

        return render(request, self.template_name, {
            'company': company,
            'company_form': company_form,
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

        return redirect('shrimp_dashboard_info')


# =============================================================================
# PRODUCT MANAGEMENT: ADD NEW PRODUCT
# Allows farming companies to add new shrimp products to their inventory.
# =============================================================================

class AddProductView(View):
    """
    Handle creation of new shrimp product listings.
    Associates product with the logged-in farming company.
    """
    template_name = "admin/Shrimp Panel/Add Product.html"

    def get_company_from_session(self, request):
        """Reuse session-based company retrieval."""
        company_id = request.session.get('company_id')
        company_type = request.session.get('company_type')

        if company_id and company_type == 'shrimp':
            try:
                return ShrimpFarmingCompany.objects.get(id=company_id)
            except ShrimpFarmingCompany.DoesNotExist:
                pass
        return None

    def get(self, request):
        """Show empty product form."""
        company = self.get_company_from_session(request)
        if not company:
            messages.error(request, "لطفاً ابتدا وارد سیستم شوید.")
            return redirect('login')

        form = ShrimpProductForm()
        return render(request, self.template_name, {
            'form': form,
            'company_logo': company.logo.url if company.logo else None,
        })

    def post(self, request):
        """Process product submission."""
        company = self.get_company_from_session(request)
        if not company:
            messages.error(request, "لطفاً ابتدا وارد سیستم شوید.")
            return redirect('login')

        form = ShrimpProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.company = company
            product.save()
            messages.success(request, "محصول با موفقیت ثبت شد.")
            return redirect('shrimp_dashboard_add_product')
        else:
            messages.error(request, "ثبت محصول با خطا مواجه شد. لطفاً مجدداً تلاش کنید.")
            return render(request, self.template_name, {
                'form': form,
                'company_logo': company.logo.url if company.logo else None,
            })


# =============================================================================
# PRODUCT MANAGEMENT: EDIT EXISTING PRODUCT
# AJAX endpoint to update product details.
# =============================================================================

class EditProductView(View):
    """
    Update product fields via AJAX POST request.
    Returns JSON response for frontend interaction.
    """

    def post(self, request, product_id):
        product = get_object_or_404(ShrimpProduct, id=product_id)
        product.product_name = request.POST.get('product_name', '')
        product.weight = request.POST.get('weight', 0)
        product.price = request.POST.get('price', 0)
        product.save()
        return JsonResponse({'status': 'success'})


# =============================================================================
# PRODUCT MANAGEMENT: DELETE PRODUCT
# AJAX endpoint to delete a product.
# =============================================================================

class DeleteProductView(View):
    """
    Delete a product via AJAX POST request.
    Returns JSON response for frontend confirmation.
    """

    def post(self, request, product_id):
        product = get_object_or_404(ShrimpProduct, id=product_id)
        product.delete()
        return JsonResponse({'status': 'success'})


# =============================================================================
# PRODUCT MANAGEMENT: LIST REGISTERED PRODUCTS
# Displays all products registered by the logged-in farming company.
# =============================================================================

class RegisteredProductsView(View):
    """
    Show list of products owned by the authenticated farming company.
    Used in dashboard for management and tracking.
    """
    template_name = "admin/Shrimp Panel/Product List.html"

    def get_company_from_session(self, request):
        """Centralized company retrieval method."""
        company_id = request.session.get('company_id')
        company_type = request.session.get('company_type')

        if company_id and company_type == 'shrimp':
            try:
                return ShrimpFarmingCompany.objects.get(id=company_id)
            except ShrimpFarmingCompany.DoesNotExist:
                pass
        return None

    def get(self, request):
        """Fetch and display company's products."""
        company = self.get_company_from_session(request)
        if not company:
            messages.error(request, "لطفاً ابتدا وارد سیستم شوید.")
            return redirect('login')

        products = ShrimpProduct.objects.filter(company=company)
        return render(request, self.template_name, {
            'products': products,
            'company_logo': company.logo.url if company.logo else None,
        })


# =============================================================================
# REQUEST MANAGEMENT: LIST PURCHASE REQUESTS
# Displays all requests made by exporters for this company's products.
# =============================================================================

class RequestsListView(View):
    """
    Display list of purchase requests from exporting companies.
    Shows status, buyer info, and product details.
    """
    template_name = "admin/Shrimp Panel/Requests Product.html"

    def get(self, request):
        """Fetch and show all relevant requests."""
        company_id = request.session.get('company_id')
        company_type = request.session.get('company_type')

        if not company_id or company_type != 'shrimp':
            messages.error(request, "لطفاً ابتدا وارد سیستم شوید.")
            return redirect('login')

        try:
            farming_company = ShrimpFarmingCompany.objects.get(id=company_id)
        except ShrimpFarmingCompany.DoesNotExist:
            messages.error(request, "شرکت انتخاب نشده است.")
            return redirect('login')

        requests = RequestsProduct.objects.filter(
            owner_company=farming_company
        ).select_related('buyer_company', 'product').order_by('-operation_date')

        return render(request, self.template_name, {
            'requests': requests,
            'company_logo': farming_company.logo.url if farming_company.logo else None,
        })


# =============================================================================
# REQUEST MANAGEMENT: UPDATE STATUS (AJAX & REDIRECT)
# Generic function to update request status (approve/reject/delete).
# =============================================================================

def update_request_status(request, pk, status):
    """
    Update the status of a product request.
    Can be called via AJAX or regular POST.
    Access-controlled by ownership check.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'درخواست نامعتبر است.'})

    company_id = request.session.get('company_id')
    if not company_id:
        return JsonResponse({'status': 'error', 'message': 'شرکت انتخاب نشده است.'})

    farming_company = get_object_or_404(ShrimpFarmingCompany, id=company_id)
    request_obj = get_object_or_404(RequestsProduct, pk=pk, owner_company=farming_company)

    request_obj.status = status
    request_obj.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'وضعیت درخواست با موفقیت تغییر یافت.'})
    else:
        messages.success(request, 'وضعیت درخواست با موفقیت تغییر یافت.')
        return redirect('shrimp_dashboard_requests_list')


def confirm_request(request, pk):
    """Approve a purchase request."""
    return update_request_status(request, pk, 'approved')


def reject_request(request, pk):
    """Reject a purchase request."""
    return update_request_status(request, pk, 'rejected')


def delete_request(request, pk):
    """Delete a request (approved or rejected)."""
    if request.method != 'POST':
        messages.error(request, 'درخواست نامعتبر است.')
        return redirect('shrimp_dashboard_requests_list')

    company_id = request.session.get('company_id')
    if not company_id:
        messages.error(request, 'شرکت انتخاب نشده است.')
        return redirect('shrimp_dashboard_requests_list')

    farming_company = get_object_or_404(ShrimpFarmingCompany, id=company_id)
    request_obj = get_object_or_404(RequestsProduct, pk=pk, owner_company=farming_company)

    request_obj.delete()
    messages.success(request, 'درخواست با موفقیت حذف شد.')
    return redirect('shrimp_dashboard_requests_list')


# =============================================================================
# AUTHENTICATION: LOGOUT HANDLER
# Clears session and redirects to login page.
# =============================================================================

class CompanyLogoutView(View):
    """
    Log out the currently authenticated company.
    Flushes session and shows success message.
    """
    def get(self, request):
        request.session.flush()
        messages.success(request, "با موفقیت از سیستم خارج شدید.")
        return redirect('login')