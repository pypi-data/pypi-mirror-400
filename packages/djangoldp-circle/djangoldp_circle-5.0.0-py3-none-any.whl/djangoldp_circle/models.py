import random
import string
from django.contrib.auth.models import Group
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from djangoldp.models import Model, DynamicNestedField
from djangoldp.permissions import PublicPermission, ACLPermissions, AnonymousReadOnly, InheritPermissions, JoinMembersPermission
from djangoldp_account.models import LDPUser
from djangoldp_account.permissions import IPOpenPermissions
from djangoldp_community.models import Community
import logging

logger = logging.getLogger('djangoldp')

STATUS_CHOICES = [
    ('Public', _('Public')),
    ('Private', _('Private')),
    ('Archived', _('Archived')),
    ('Restricted', _('Restricted')),
]

circle_fields = ["@id", "name", "subtitle", "description", "creationDate", "public", "owner", "jabberID",\
                 "jabberRoom", "members", "admins", "parentCircle", "children"]
circle_nested_fields = ["members", "admins", "children"]
for module, fields in {'community':'community','polls':'polls','resource':'resources','event':'events','fcpe':'space'}.items():
    if f'djangoldp_{module}' in settings.DJANGOLDP_PACKAGES:
        circle_fields += [fields]
        circle_nested_fields += [fields]

class Circle(Model):
    name = models.CharField(max_length=255, blank=True, null=True, default='')
    subtitle = models.CharField(max_length=255, blank=True, null=True, default='')
    description = models.TextField(blank=True, null=True, default='')
    creationDate = models.DateField(auto_now_add=True)
    #TODO: set cascade. For now we allow the deletion of groups while keeping the circles
    community = models.ForeignKey(Community, related_name="circles", on_delete=models.SET_NULL, null=True, blank=True)
    #TODO: remove the status. We keep it for now for the migration
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Public')
    public = models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owned_circles", on_delete=models.SET_NULL,
                              null=True, blank=True)
    #TODO: set cascade. For now we allow the deletion of groups while keeping the circles
    members = models.OneToOneField(Group, related_name="circle", on_delete=models.SET_NULL, null=True, blank=True)
    admins = models.OneToOneField(Group, related_name="admin_circle", on_delete=models.SET_NULL, null=True, blank=True)
    parentCircle = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name='children',
                                     help_text="A circle can optionally be nested within a parent")
    jabberID = models.CharField(max_length=255, blank=True, null=True, unique=True)
    jabberRoom = models.BooleanField(default=True)

    class Meta(Model.Meta):
        ordering = ['pk']
        empty_containers = ["owner"]
        auto_author = 'owner'
        # depth = 1 # Disabled due to owner being serialized
        permission_classes = [IPOpenPermissions|(AnonymousReadOnly&(JoinMembersPermission|PublicPermission|ACLPermissions))]
        permission_roles = {
            'members': {'perms': ['view'], 'add_author': True},
            'admins': {'perms': ['view', 'change', 'control'], 'add_author': True},
        }
        nested_fields = circle_nested_fields
        serializer_fields = circle_fields
        public_field = 'public'
        rdf_type = 'hd:circle'

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

# add circles in groups and users
Group._meta.inherit_permissions += ['circle','admin_circle']
Group._meta.serializer_fields += ['circle', 'admin_circle']
LDPUser._meta.serializer_fields += ['owned_circles', 'circles']
LDPUser.circleContainer = lambda self: {'@id': f'{self.urlid}circles/'}
LDPUser._meta.nested_fields += ['circles', 'owned_circles']
LDPUser.circles = lambda self: Circle.objects.filter(members__user=self)
LDPUser.circles.field = DynamicNestedField(Circle, 'circles')

@receiver(pre_save, sender=Circle)
def set_jabberid(sender, instance, **kwargs):
    if getattr(settings, 'JABBER_DEFAULT_HOST', False) and not instance.jabberID:
        instance.jabberID = '{}@conference.{}'.format(
            ''.join(
                [
                    random.choice(string.ascii_letters + string.digits)
                    for n in range(12)
                ]
            ).lower(),
            settings.JABBER_DEFAULT_HOST
        )
        instance.jabberRoom = True

#TODO: Remove this model. For now we keep it for the migration
class CircleMember(Model):
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='oldmembers')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="oldcircles", null=True, blank=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        try:
            return '{} -> {} ({})'.format(self.circle.urlid, self.user.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        ordering = ['pk']
        container_path = "circle-members/"
        depth = 2
        unique_together = ['user', 'circle']
        rdf_type = 'hd:circlemember'
        permission_classes = [ACLPermissions]
