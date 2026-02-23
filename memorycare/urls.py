from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect


def home_redirect(request):
    # If user is already authenticated, send them to dashboard home
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return redirect('accounts:login')

urlpatterns = [
    path('', home_redirect, name='home'),  # redirect root to login
    path('admin/', admin.site.urls),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
