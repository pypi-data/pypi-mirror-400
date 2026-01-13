from django.contrib import admin
from djangoldp.admin import DjangoLDPAdmin
from djangoldp.models import Model
from djangoldp_community.models import Community, CommunityProfile, CommunityAddress


@admin.register(CommunityAddress, CommunityProfile)
class EmptyAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        return {}

class ProfileInline(admin.StackedInline):
    model = CommunityProfile
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0

class AddressInline(admin.TabularInline):
    model = CommunityAddress
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0


@admin.register(Community)
class CommunityAdmin(DjangoLDPAdmin):
    list_display = ('urlid', 'name', 'allow_self_registration')
    exclude = ('urlid', 'slug', 'is_backlink', 'allow_create_backlink')
    inlines = [ProfileInline, AddressInline]
    search_fields = ['urlid', 'name', 'members__user__urlid']
    ordering = ['urlid']

    def get_queryset(self, request):
        # Hide distant communities
        queryset = super(CommunityAdmin, self).get_queryset(request)
        internal_ids = [x.pk for x in queryset if not Model.is_external(x)]
        return queryset.filter(pk__in=internal_ids)


