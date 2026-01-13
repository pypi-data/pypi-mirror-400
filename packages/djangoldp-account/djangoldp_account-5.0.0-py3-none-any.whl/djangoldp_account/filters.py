from django.conf import settings
from rest_framework.filters import BaseFilterBackend

PASSTHROUGH_IPS = getattr(settings, 'PASSTHROUGH_IPS', '')

def check_client_ip(request):
    x_forwarded_for = request.headers.get('x-forwarded-for')
    if x_forwarded_for:
        if any(ip in x_forwarded_for.replace(' ', '').split(',') for ip in PASSTHROUGH_IPS):
            return True
    elif request.META.get('REMOTE_ADDR') in PASSTHROUGH_IPS:
        return True
    return False

class IPFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if check_client_ip(request):
            return queryset
        else:
            return queryset.none()