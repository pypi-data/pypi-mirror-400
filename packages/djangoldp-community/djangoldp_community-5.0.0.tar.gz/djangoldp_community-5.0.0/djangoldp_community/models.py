import uuid
from importlib import import_module
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from djangoldp.models import Model, DynamicNestedField
from djangoldp.permissions import AnonymousReadOnly, ReadOnly, ReadAndCreate, ACLPermissions, InheritPermissions, JoinMembersPermission
from djangoldp_account.models import LDPUser

djangoldp_modules = list(settings.DJANGOLDP_PACKAGES)
community_fields = ['@id', 'name', 'profile', 'addresses', 'logo', 'allow_self_registration',\
                             'projects', 'members', 'joboffers', 'admins']

for dldp_module in djangoldp_modules:
    try:
        module_settings = import_module(dldp_module + '.settings')
        module_community_nested_fields = module_settings.COMMUNITY_NESTED_FIELDS
        community_fields += module_community_nested_fields
    except:
        pass


class Community(Model):
    name = models.CharField(max_length=255, blank=True, null=True, help_text="Changing a community's name is highly discouraged")
    logo = models.URLField(blank=True, null=True)
    allow_self_registration = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owned_communities", on_delete=models.SET_NULL,
                              null=True, blank=True)
    #TODO: set cascade. For now we allow the deletion of groups while keeping the community
    members = models.OneToOneField(Group, related_name="community", on_delete=models.SET_NULL, null=True, blank=True)
    admins = models.OneToOneField(Group, related_name="admin_community", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('community')
        verbose_name_plural = _("communities")
        empty_containers = ["owner"]
        auto_author = 'owner'
        permission_classes = [AnonymousReadOnly, JoinMembersPermission|ReadAndCreate|ACLPermissions]
        permission_roles = {
            'members': {'perms': ['view'], 'add_author': True},
            'admins': {'perms': ['view', 'change', 'control'], 'add_author': True},
        }
        lookup_field = 'slug'
        container_path = "/communities/"
        ordering = ['slug']
        serializer_fields = community_fields
        nested_fields = ['addresses', 'projects']
        rdf_type = "sib:Community"
        depth = 1

class CommunityProfile(Model):
    community = models.OneToOneField(Community, on_delete=models.CASCADE, related_name='profile', null=True, blank=True)
    shortDescription = models.CharField(max_length=254, blank=True, null=True, default='')
    description = models.TextField(blank=True, null=True, default='')
    phone = models.CharField(max_length=254, blank=True, null=True, default='')
    email = models.EmailField(max_length=254, blank=True, null=True, default='')
    website = models.URLField(blank=True, null=True, default='')
    tweeter = models.URLField(blank=True, null=True, default='')
    facebook = models.URLField(blank=True, null=True, default='')
    linkedin = models.URLField(blank=True, null=True, default='')
    instagram = models.URLField(blank=True, null=True, default='')
    picture1 = models.URLField(blank=True, null=True, default='')
    picture2 = models.URLField(blank=True, null=True, default='')
    picture3 = models.URLField(blank=True, null=True, default='')

    def __str__(self):
        try:
            return '{} ({})'.format(self.community.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('community profile')
        verbose_name_plural = _("community profiles")
        permission_classes = [ReadOnly|InheritPermissions]
        inherit_permissions = ['community']
        container_path = "community-profiles/"
        serializer_fields = ['@id', 'community', 'shortDescription', 'description', 'phone', 'email', 'website', 'tweeter',\
                             'facebook', 'linkedin', 'instagram', 'picture1', 'picture2', 'picture3']
        rdf_type = "sib:CommunityProfile"

class CommunityAddress(Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='addresses', null=True, blank=True)
    address_line1 = models.CharField(max_length=254, blank=True, null=True, default='')
    address_line2 = models.CharField(max_length=254, blank=True, null=True, default='')
    lat = models.DecimalField(max_digits=15, decimal_places=12, blank=True, null=True, verbose_name=_("Latitude"))
    lng = models.DecimalField(max_digits=15, decimal_places=12, blank=True, null=True, verbose_name=_("Longitude"))

    def __str__(self):
        try:
            return '{} ({})'.format(self.community.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('community address')
        verbose_name_plural = _("community addresses")
        permission_classes = [ReadOnly|InheritPermissions]
        inherit_permissions = ['community']
        serializer_fields = ['@id', 'community', 'address_line1', 'address_line2', 'lat', 'lng']
        rdf_type = "sib:CommunityAddress"
        container_path = "community-addresses/"

# add communities in groups and users
Group._meta.inherit_permissions += ['community','admin_community']
Group._meta.serializer_fields += ['community', 'admin_community']
LDPUser._meta.nested_fields.append('communities')
LDPUser._meta.serializer_fields.append('communities')
LDPUser.communities = lambda self: Community.objects.filter(members__user=self)
LDPUser.communities.field = DynamicNestedField(Community, 'communities')
LDPUser._meta.nested_fields.append('admin_communities')
LDPUser._meta.serializer_fields.append('admin_communities')
LDPUser.admin_communities = lambda self: Community.objects.filter(admins__user=self)
LDPUser.admin_communities.field = DynamicNestedField(Community, 'admin_communities')

#TODO: Remove this model. For now we keep it for the migration
class CommunityMember(Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='oldmembers', null=True, blank=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="oldcommunities", null=True, blank=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        try:
            return '{} -> {} ({})'.format(self.user.urlid, self.community.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        ordering = ['pk']
        verbose_name = _('community member')
        verbose_name_plural = _("community members")
        permission_classes = [ACLPermissions]
        container_path = "community-members/"
        serializer_fields = ['@id', 'community', 'user', 'is_admin']
        rdf_type = "as:items"

    def save(self, *args, **kwargs):
        if not self.pk and CommunityMember.objects.filter(community=self.community, user=self.user).exists():
            return

        super(CommunityMember, self).save(*args, **kwargs)

#TODO: Remove this model. For now we keep it for the migration
class CommunityCircle(Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='oldcircles', null=True, blank=True)
    circle = models.OneToOneField('djangoldp_circle.Circle', on_delete=models.CASCADE, related_name="oldcommunity", null=True, blank=True)

    def __str__(self):
        try:
            return '{} -> {} ({})'.format(self.circle.urlid, self.community.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('community circle')
        verbose_name_plural = _("community circles")
        permission_classes = [ReadOnly]
        container_path = "community-circles/"
        serializer_fields = ['@id', 'community', 'circle']
        rdf_type = "as:items"

    def save(self, *args, **kwargs):
        if not self.pk and CommunityCircle.objects.filter(community=self.community, circle=self.circle).exists():
            return

        super(CommunityCircle, self).save(*args, **kwargs)

#TODO: Remove this model. For now we keep it for the migration
class CommunityProject(Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='oldprojects', null=True, blank=True)
    project = models.OneToOneField('djangoldp_project.Project', on_delete=models.CASCADE, related_name="oldcommunity", null=True, blank=True)

    def __str__(self):
        try:
            return '{} -> {} ({})'.format(self.project.urlid, self.community.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('community project')
        verbose_name_plural = _("community projects")
        permission_classes = [ReadOnly]
        container_path = "community-projects/"
        serializer_fields = ['@id', 'community', 'project']
        rdf_type = "as:items"

    def save(self, *args, **kwargs):
        if not self.pk and CommunityProject.objects.filter(community=self.community, project=self.project).exists():
            return

        super(CommunityProject, self).save(*args, **kwargs)

#TODO: Remove this model. For now we keep it for the migration
class CommunityJobOffer(Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='oldjoboffers', null=True, blank=True)
    joboffer = models.OneToOneField('djangoldp_joboffer.JobOffer', on_delete=models.CASCADE, related_name="oldcommunity", null=True, blank=True)

    def __str__(self):
        try:
            return '{} -> {} ({})'.format(self.joboffer.urlid, self.community.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('community job offer')
        verbose_name_plural = _("community job offers")
        permission_classes = [ReadOnly]
        container_path = "community-joboffers/"
        serializer_fields = ['@id', 'community', 'joboffer']
        rdf_type = "as:items"

    def save(self, *args, **kwargs):
        if not self.pk and CommunityJobOffer.objects.filter(community=self.community, joboffer=self.joboffer).exists():
            return

        super(CommunityJobOffer, self).save(*args, **kwargs)

@receiver(pre_save, sender=Community)
def pre_create_account(sender, instance, **kwargs):
    if not instance.urlid or instance.urlid.startswith(settings.SITE_URL):
        if getattr(instance, Model.slug_field(instance)) != slugify(instance.name):
            if Community.objects.local().filter(slug=slugify(instance.name)).count() > 0:
                raise ValidationError(_("Community name must be unique"))
            setattr(instance, Model.slug_field(instance), slugify(instance.name))
            setattr(instance, "urlid", "")
    else:
        # Is a distant object, generate a random slug
        setattr(instance, Model.slug_field(instance), uuid.uuid4().hex.upper()[0:8])

@receiver(post_save, sender=Community)
def create_community_profile(instance, created, **kwargs):
    if not Model.is_external(instance):
        CommunityProfile.objects.get_or_create(community=instance)