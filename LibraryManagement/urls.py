"""
URL configuration for LibraryManagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static 


admin.site.site_header = 'Library Management System Admin'
admin.site.site_title = 'Library Management System Admin pannel'
admin.site.index_title = 'Welcome to Library Management System Admin Pannel'

# ------------------------------------------------------------------------------
# This is for main admin login restriction (only main admin can login to admin pannel)
# -----------------------------------------------------------------------------
def main_admin_only(request):
    user = request.user
    if not user.is_authenticated or not user.is_active:
        return False
    return user.is_superuser and user.username == settings.MAIN_ADMIN_USERNAME

admin.site.has_permission = main_admin_only
# -----------------------------------------------------------------------------

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('LibraryApp.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)