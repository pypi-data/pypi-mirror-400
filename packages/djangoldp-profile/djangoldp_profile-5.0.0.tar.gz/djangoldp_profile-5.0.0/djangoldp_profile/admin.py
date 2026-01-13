from django.contrib import admin
from djangoldp.admin import DjangoLDPAdmin
from djangoldp.models import Model
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(DjangoLDPAdmin):
    list_display = ('urlid', 'user')
    exclude = ('urlid', 'user', 'is_backlink', 'allow_create_backlink', 'slug')
    search_fields = ['urlid', 'user__urlid', 'available', 'job', 'city', 'phone', 'website']
    ordering = ['urlid']

    def get_queryset(self, request):
        # Hide distant profiles
        queryset = super(ProfileAdmin, self).get_queryset(request)
        internal_ids = [x.pk for x in queryset if not Model.is_external(x)]
        return queryset.filter(pk__in=internal_ids)


