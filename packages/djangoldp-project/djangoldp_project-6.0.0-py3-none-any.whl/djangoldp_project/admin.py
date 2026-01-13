from django.contrib import admin
from djangoldp.admin import DjangoLDPAdmin
from djangoldp.models import Model
from .models import Project, Member, Customer, BusinessProvider


@admin.register(BusinessProvider, Customer, Member)
class EmptyAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        return {}


class TeamInline(admin.TabularInline):
    model = Member
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0


class BusinessProviderInline(admin.TabularInline):
    model = BusinessProvider
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0


@admin.register(Project)
class ProjectAdmin(DjangoLDPAdmin):
    list_display = ('urlid', 'customer', 'name', 'captain', 'status', 'jabberID')
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink', 'jabberID', 'jabberRoom')
    search_fields = ['urlid', 'name', 'members__user__urlid', 'number', 'description',\
        'status', 'captain__urlid', 'customer__urlid', 'customer__name',\
        'businessProvider__urlid', 'businessProvider__name']
    ordering = ['urlid']
    inlines = [BusinessProviderInline, TeamInline]

    def get_queryset(self, request):
        # Hide distant projects
        queryset = super(ProjectAdmin, self).get_queryset(request)
        internal_ids = [x.pk for x in queryset if not Model.is_external(x)]
        return queryset.filter(pk__in=internal_ids)


