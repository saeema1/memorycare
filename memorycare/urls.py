from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect, render


def home_redirect(request):
    # If user is already authenticated, send them to the appropriate dashboard
    if request.user.is_authenticated:
        role = getattr(request.user, 'role', '')
        if role and isinstance(role, str):
            r = role.upper()
            if r == 'DOCTOR':
                return redirect('dashboard:doctor_dashboard')
            if r == 'CAREGIVER':
                return redirect('dashboard:caregiver_dashboard')
            if r == 'PATIENT':
                return redirect('dashboard:patient_dashboard')
        # Fallback to dashboard home which will perform its own routing
        return redirect('dashboard:home')
    # If not authenticated, render the public landing/homepage (do not force-login)
    return render(request, 'accounts/landing.html')

urlpatterns = [
    path('', home_redirect, name='home'),  # redirect root to login
    path('admin/', admin.site.urls),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
