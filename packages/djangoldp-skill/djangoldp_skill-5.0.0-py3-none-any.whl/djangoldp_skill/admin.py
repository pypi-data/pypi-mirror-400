from django.contrib import admin
from django.db.models import Count
from djangoldp.admin import DjangoLDPAdmin
from djangoldp_i18n.admin import DjangoLDPI18nAdmin
from djangoldp.models import Model
from djangoldp_skill.models import Skill


@admin.register(Skill)
class SkillAdmin(DjangoLDPI18nAdmin, DjangoLDPAdmin):
    list_display = ('urlid', 'name', 'users__count')
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    search_fields = ['urlid', 'name']
    ordering = ['urlid']

    def users__count(self, obj):
        return obj.users_count

    def get_queryset(self, request):
        # Hide distant skills
        queryset = super(SkillAdmin, self).get_queryset(request)
        internal_ids = [x.pk for x in queryset if not Model.is_external(x)]
        queryset = queryset.annotate(users_count=Count("users"))
        return queryset.filter(pk__in=internal_ids)

