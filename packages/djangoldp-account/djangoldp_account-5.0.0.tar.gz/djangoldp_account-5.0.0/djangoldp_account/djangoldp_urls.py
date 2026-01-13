"""djangoldp project URL Configuration"""

from pydoc import locate
from django.conf import settings
from django.contrib.auth.models import Group
from django.urls import path, re_path, include
from django.views.decorators.csrf import csrf_exempt

from djangoldp.permissions import ACLPermissions
from djangoldp.views.ldp_viewset import LDPViewSet
from djangoldp_account.forms import LDPUserForm
from .models import ChatProfile, Account
from .views import userinfocustom, RPLoginView, RPLoginCallBackView, check_user, LDPAccountLoginView, RedirectView, \
    LDPAccountRegistrationView


user_form_override = getattr(settings, 'REGISTRATION_USER_FORM', None)
user_form = LDPUserForm if user_form_override is None else locate(user_form_override)

urlpatterns = [
    path('auth/register/', LDPAccountRegistrationView.as_view(form_class=user_form), name='django_registration_register'),
    path('auth/login/', LDPAccountLoginView.as_view(),name='login'),
    path('auth/', include('django_registration.backends.activation.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('accounts/', LDPViewSet.urls(model=Account, model_prefix='pk_lookup', lookup_field='pk')),
    path('chat-profile/', LDPViewSet.urls(model=ChatProfile, model_prefix='pk_lookup', lookup_field='pk')),
    re_path(r'^oidc/login/callback/?$', RPLoginCallBackView.as_view(), name='oidc_login_callback'),
    re_path(r'^oidc/login/?$', RPLoginView.as_view(), name='oidc_login'),
    re_path(r'^userinfo/?$', csrf_exempt(userinfocustom)),
    re_path(r'^check-user/?$', csrf_exempt(check_user)),
    path('redirect-default/', RedirectView.as_view(),name='redirect-default'),
    path('', include('oidc_provider.urls', namespace='oidc_provider'))
]
