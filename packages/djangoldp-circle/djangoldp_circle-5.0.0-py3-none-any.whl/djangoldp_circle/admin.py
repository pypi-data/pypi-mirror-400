from django.contrib import admin
from django.contrib.auth.models import Group
from djangoldp.admin import DjangoLDPAdmin
from djangoldp.models import Model
from .models import Circle

@admin.register(Circle)
class CircleAdmin(DjangoLDPAdmin):
    list_display = ('urlid', 'name', 'owner', 'public', 'jabberID')
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink', 'jabberID', 'jabberRoom')
    search_fields = ['urlid', 'name', 'members__user__urlid', 'subtitle', 'description', 'public', 'owner__urlid']
    ordering = ['urlid']

    def get_queryset(self, request):
        # Hide distant circles
        queryset = super(CircleAdmin, self).get_queryset(request)
        internal_ids = [x.pk for x in queryset if not Model.is_external(x)]
        return queryset.filter(pk__in=internal_ids)