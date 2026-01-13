from django.db import models
from djangoldp.models import Model
from djangoldp.permissions import AuthenticatedOnly, OwnerPermissions
from djangoldp_account.models import LDPUser


# a resource in which only the owner has permissions
class OwnedResource(Model):
    description = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(LDPUser, blank=True, null=True, related_name="owned_resources",
                             on_delete=models.CASCADE)

    class Meta(Model.Meta):
        owner_field = 'user'
        permission_classes = [AuthenticatedOnly, OwnerPermissions]
        serializer_fields = ['@id', 'description', 'user']
        depth = 1
