"""
URL configuration for accthreads project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include, re_path
from rest_framework import permissions

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from comments.views import AnonymousLoginView, GoogleLogin, CustomConfirmEmailView

from allauth.account.views import EmailVerificationSentView



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('dj_rest_auth.urls')),

    path(
        'api/auth/registration/account-confirm-email/<key>/',
        CustomConfirmEmailView.as_view(),
        name='account_confirm_email',
    ),

    # 👇 override the "verification sent" placeholder
    path(
        'api/auth/registration/account-email-verification-sent/',
        EmailVerificationSentView.as_view(),
        name='account_email_verification_sent',
    ),

    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),

    path('api/auth/social/', include('allauth.socialaccount.urls')),
    path('api/comments/', include('comments.urls')),
    path('api/auth/anonymous/', AnonymousLoginView.as_view(), name='anonymous_login'),
    path('api/auth/google/', GoogleLogin.as_view(), name='google-login'),

    # Schema endpoint (OpenAPI JSON)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # ReDoc UI (optional)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
