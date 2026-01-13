import random
import string
from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save
from djangoldp.models import Model, DynamicNestedField
from djangoldp.permissions import AuthenticatedOnly, AnonymousReadOnly, CreateOnly, ReadAndCreate, \
    PublicPermission, OwnerPermissions, InheritPermissions, ACLPermissions
from djangoldp_account.models import LDPUser
from djangoldp_account.permissions import IPOpenPermissions
from djangoldp_community.models import Community

import logging
logger = logging.getLogger('djangoldp')


class Customer(Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    postcode = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    logo = models.URLField(blank=True, null=True)
    companyRegister = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owned_customers", null=True, blank=True, on_delete=models.SET_NULL)
    role = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)

    class Meta(Model.Meta):
        ordering = ['pk']
        auto_author = 'owner'
        owner_field = 'owner'
        permission_classes = [AuthenticatedOnly, CreateOnly|OwnerPermissions|InheritPermissions]
        inherit_permissions = ['projects']

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid


def auto_increment_project_number():
  last_inc = Project.objects.all().order_by('id').last()
  if not last_inc:
    return 1
  return last_inc.number + 1


STATUS_CHOICES = [
    ('Public', 'Public'),
    ('Private', 'Private'),
    ('Archived', 'Archived'),
]

project_fields = ["@id", "name", "description", "status", "number", "creationDate", "customer", "captain", "driveID", "businessProvider", "jabberID", "jabberRoom", "members", 'community']


class Project(Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    #TODO: set cascade. For now we allow the deletion of groups while keeping the circles
    community = models.ForeignKey(Community, related_name="projects", on_delete=models.SET_NULL, null=True, blank=True)
    #TODO: remove the status. We keep it for now for the migration
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='Private', null=True, blank=True)
    public = models.BooleanField(default=False)
    number = models.PositiveIntegerField(default=auto_increment_project_number, editable=False)
    creationDate = models.DateField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, related_name='projects', null=True, blank=True)
    captain = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True,
                                related_name='+')
    #TODO: set cascade. For now we allow the deletion of groups while keeping the circles
    members = models.OneToOneField(Group, related_name="project", on_delete=models.SET_NULL, null=True, blank=True)
    admins = models.OneToOneField(Group, related_name="admin_project", on_delete=models.SET_NULL, null=True, blank=True)
    driveID = models.TextField(null=True, blank=True)
    jabberID = models.CharField(max_length=255, blank=True, null=True)
    jabberRoom = models.BooleanField(default=True)

    class Meta(Model.Meta):
        ordering = ['pk']
        empty_containers = ["captain"]
        auto_author = 'captain'
        public_field = 'public'
        permission_classes = [IPOpenPermissions|(AuthenticatedOnly&InheritPermissions&(PublicPermission|ACLPermissions))]
        inherit_permissions = ['community']
        permission_roles = {
            'members': {'perms': ['view'], 'add_author': True},
            'admins': {'perms': ['view', 'change', 'control'], 'add_author': True},
        }
        rdf_type = 'hd:project'

    def __str__(self):
        try:
            return '{} {} ({})'.format(self.customer.name, self.name, self.urlid)
        except:
            return self.urlid

    def get_admins(self):
        return self.members.filter(is_admin=True)

# add projects in groups and users
Group._meta.inherit_permissions += ['project','admin_project']
Group._meta.serializer_fields += ['project', 'admin_project']
LDPUser._meta.serializer_fields.append('projects')
LDPUser.projectContainer = lambda self: {'@id': f'{self.urlid}projects/'}
LDPUser._meta.nested_fields.append('projects')
LDPUser.projects = lambda self: Project.objects.filter(members__user=self)
LDPUser.projects.field = DynamicNestedField(Project, 'projects')

class BusinessProvider(Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='businessprovider', null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    fee = models.PositiveIntegerField(default='0', null=True, blank=True)

    class Meta(Model.Meta):
        permission_classes = [AnonymousReadOnly, ReadAndCreate]

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid


#TODO: Remove this model. For now we keep it for the migration
class Member(Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='oldmembers', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects', null=True, blank=True)
    is_admin = models.BooleanField(default=False)

    class Meta(Model.Meta):
        container_path = "project-members/"
        permission_classes = [ACLPermissions]
        unique_together = ['user', 'project']
        rdf_type = 'hd:projectmember'

    def __str__(self):
        try:
            return '{} -> {} ({})'.format(self.project.urlid, self.user.urlid, self.urlid)
        except:
            return self.urlid


@receiver(pre_save, sender=Project)
def set_jabberid(sender, instance, **kwargs):
    if isinstance(getattr(settings, 'JABBER_DEFAULT_HOST', False), str) and not instance.jabberID:
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