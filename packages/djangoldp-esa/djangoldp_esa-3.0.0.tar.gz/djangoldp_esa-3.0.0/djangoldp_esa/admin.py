from django.contrib import admin
from djangoldp.admin import DjangoLDPAdmin
from djangoldp_esa.models import EsaCommunity, EsaCommunityTag, EsaCommunitySpace, EsaCommunitySector, EsaBicLocation, EsaBicPosition, EsaCommunityRole


class EsaCommunityTagInline(admin.TabularInline):
    model = EsaCommunity.tags.through
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0


class EsaCommunitySectorInline(admin.TabularInline):
    model = EsaCommunity.sectors.through
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0


class EsaCommunitySpaceInline(admin.TabularInline):
    model = EsaCommunity.spaces.through
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0


class EsaCommunityInline(admin.StackedInline):
    model = EsaCommunity
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0


class EsaCommunityAdmin(DjangoLDPAdmin):
    list_display = ('community', 'urlid')
    exclude = ('urlid', 'slug', 'is_backlink', 'allow_create_backlink')
    inlines = [EsaCommunityTagInline,
               EsaCommunitySectorInline, EsaCommunitySpaceInline]
    search_fields = ['urlid', 'community', 'name']
    ordering = ['community']


class EsaGenericAdmin(DjangoLDPAdmin):
    list_display = ('name', 'urlid')
    exclude = ('urlid', 'slug', 'is_backlink', 'allow_create_backlink', 'esacommunity')
    search_fields = ['urlid', 'name']
    ordering = ['name']


admin.site.register(EsaCommunity, EsaCommunityAdmin)
admin.site.register(EsaCommunityTag, EsaGenericAdmin)
admin.site.register(EsaCommunityRole, EsaGenericAdmin)
admin.site.register(EsaCommunitySector, EsaGenericAdmin)
admin.site.register(EsaCommunitySpace, EsaGenericAdmin)
admin.site.register(EsaBicLocation, EsaGenericAdmin)
admin.site.register(EsaBicPosition, EsaGenericAdmin)
