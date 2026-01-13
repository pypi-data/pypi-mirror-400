from djangoldp.permissions import LDPBasePermission
from .filters import IPFilterBackend, check_client_ip

class IPOpenPermissions(LDPBasePermission):
    filter_backend = IPFilterBackend
    def has_permission(self, request, view):
        return check_client_ip(request)

    def has_object_permission(self, request, view, obj):
        return check_client_ip(request)
    
    def get_permissions(self, user, model, obj=None):
        #Will always say there is no migrations, not taking the IP into accounts
        return set()