from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

# Import models
from authentication.models import ShrimpFarmingCompany, ExportingCompany
from shrimp_panel.models import ShrimpProduct, RequestsProduct
from .models import ContactMessage


# =============================================================================
# PUBLIC HOMEPAGE VIEW
# Displays the main landing page with user session context.
# =============================================================================

class HomeView(TemplateView):
    """
    Render the homepage template with login state context.
    No additional data fetching required.
    """
    template_name = 'page/home.html'

    def get_context_data(self, **kwargs):
        """Add authentication status and company type to context."""
        context = super().get_context_data(**kwargs)
        session = self.request.session

        context['is_logged_in'] = bool(session.get('company_type') and session.get('company_id'))
        context['company_type'] = session.get('company_type')

        return context


# =============================================================================
# PRODUCT LISTING VIEW
# Shows all available shrimp products with request status for exporters.
# =============================================================================

class ProductView(TemplateView):
    """
    Display a list of all shrimp products.
    For logged-in exporting companies, shows pending request statuses.
    """
    template_name = 'page/Product.html'

    def get_context_data(self, **kwargs):
        """Enhance context with products and request tracking."""
        context = super().get_context_data(**kwargs)
        session = self.request.session

        # Fetch all products with related farming company (optimized)
        context['products'] = ShrimpProduct.objects.select_related('company').all()

        # Authentication context
        is_logged_in = bool(session.get('company_type') and session.get('company_id'))
        company_type = session.get('company_type')
        context['is_logged_in'] = is_logged_in
        context['company_type'] = company_type

        # Track pending requests if user is an exporting company
        if is_logged_in and company_type == 'export':
            try:
                buyer_company = ExportingCompany.objects.get(id=session['company_id'])
                pending_product_ids = RequestsProduct.objects.filter(
                    buyer_company=buyer_company,
                    status='pending'
                ).values_list('product_id', flat=True)
                context['pending_requests'] = list(pending_product_ids)
                context['is_export_company'] = True
            except ExportingCompany.DoesNotExist:
                context['pending_requests'] = []
                context['is_export_company'] = False
        else:
            context['pending_requests'] = []
            context['is_export_company'] = False

        return context


# =============================================================================
# PRODUCT REQUEST HANDLER
# Allows exporters to request purchase of a specific product.
# =============================================================================

class RequestProductView(View):
    """
    Handle product purchase requests from exporting companies.
    
    Validates user role, checks product existence, and creates a new
    RequestsProduct entry with status 'pending'.
    """

    def post(self, request, product_id):
        """Process product request submission."""
        session = request.session
        company_type = session.get('company_type')
        company_id = session.get('company_id')

        # Authorization check
        if company_type != 'export' or not company_id:
            messages.error(request, '❌ فقط شرکت‌های صادرکننده می‌توانند درخواست خرید ثبت کنند.')
            return redirect('product')

        # Validate exporter existence
        try:
            buyer_company = ExportingCompany.objects.get(id=company_id)
        except ExportingCompany.DoesNotExist:
            messages.error(request, 'شرکت صادرکننده یافت نشد.')
            return redirect('product')

        # Get target product
        product = get_object_or_404(ShrimpProduct, id=product_id)

        # Create request
        RequestsProduct.objects.create(
            buyer_company=buyer_company,
            product=product,
            owner_company=product.company,
            support_code=product.support_code,
            status='pending'
        )

        messages.success(request, '✅ درخواست خرید شما با موفقیت ثبت شد.')
        return redirect('product')


# =============================================================================
# COMPANY DIRECTORY VIEW
# Lists all shrimp farming companies on the platform.
# =============================================================================

class CompanyView(TemplateView):
    """
    Display a directory of all shrimp farming companies.
    Includes session-based authentication context.
    """
    template_name = 'page/Company.html'

    def get_context_data(self, **kwargs):
        """Add company list and login state to context."""
        context = super().get_context_data(**kwargs)
        session = self.request.session

        context['companies'] = ShrimpFarmingCompany.objects.all()
        context['is_logged_in'] = bool(session.get('company_type') and session.get('company_id'))
        context['company_type'] = session.get('company_type')

        return context


# =============================================================================
# ABOUT US VIEW
# Static about page with same context structure as CompanyView.
# =============================================================================

class AboutView(TemplateView):
    """
    Render the about us page with company list and login context.
    Shares logic with CompanyView but uses different template.
    """
    template_name = 'page/About.html'

    def get_context_data(self, **kwargs):
        """Reuse context logic from CompanyView."""
        context = super().get_context_data(**kwargs)
        session = self.request.session

        context['companies'] = ShrimpFarmingCompany.objects.all()
        context['is_logged_in'] = bool(session.get('company_type') and session.get('company_id'))
        context['company_type'] = session.get('company_type')

        return context


# =============================================================================
# CONTACT FORM VIEW
# Handles display and submission of the contact form.
# Collects visitor info and stores message with IP address.
# =============================================================================

class ContactView(View):
    """
    Handle contact form display and submission.
    
    GET: Show empty or pre-filled form
    POST: Validate input, save message, show success/error
    Stores client IP for spam monitoring.
    """
    template_name = 'page/contact.html'

    def get(self, request):
        """Render blank contact form."""
        return render(request, self.template_name, self._get_base_context())

    def post(self, request):
        """Process submitted contact form."""
        context = self._get_base_context()
        data = {key: request.POST.get(key, '').strip() for key in ['name', 'email', 'subject', 'message', 'phone']}

        # Repopulate form fields
        context.update(data)

        # Validation
        required_fields = ['name', 'email', 'subject', 'message']
        labels = {'name': 'نام', 'email': 'ایمیل', 'subject': 'موضوع', 'message': 'پیام'}

        for field in required_fields:
            if not data[field]:
                messages.error(request, f'❌ لطفاً {labels[field]} خود را وارد کنید.')
                return render(request, self.template_name, context)

        # Save message
        try:
            ContactMessage.objects.create(
                name=data['name'],
                email=data['email'],
                phone=data['phone'],
                subject=data['subject'],
                message=data['message'],
                ip_address=self._get_client_ip(request)
            )
            messages.success(request, '✅ پیام شما با موفقیت ثبت شد. در اسرع وقت با شما تماس خواهیم گرفت.')

            # Clear form on success
            context.update({field: '' for field in data})

        except Exception as e:
            messages.error(request, f'❌ خطایی در ثبت پیام رخ داد: {str(e)}')

        return render(request, self.template_name, context)

    def _get_base_context(self):
        """Generate default context including authentication state."""
        session = self.request.session
        return {
            'is_logged_in': bool(session.get('company_type') and session.get('company_id')),
            'company_type': session.get('company_type'),
            'name': '',
            'email': '',
            'subject': '',
            'message': '',
            'phone': ''
        }

    def _get_client_ip(self, request):
        """Extract client IP address from request headers."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip