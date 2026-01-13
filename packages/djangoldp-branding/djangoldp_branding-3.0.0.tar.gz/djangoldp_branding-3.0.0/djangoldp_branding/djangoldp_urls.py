from django.conf import settings
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('auth/password_reset/', auth_views.PasswordResetView.as_view(
        email_template_name='registration/password_reset_email.txt',
        html_email_template_name='registration/password_reset_email.html'
    )),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + [
        path('templates-registry/', views.BrandingViewset),
        path('templates-registry/<parameters>/', views.BrandingViewset)
    ]
