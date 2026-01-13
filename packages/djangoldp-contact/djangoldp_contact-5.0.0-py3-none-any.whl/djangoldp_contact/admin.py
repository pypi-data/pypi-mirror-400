from django.contrib import admin
from djangoldp.admin import DjangoLDPAdmin
from djangoldp.models import Model
from .models import Contact


@admin.register(Contact)
class ContactAdmin(DjangoLDPAdmin):
    list_display = ('urlid', 'user', 'contact')
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    search_fields = ['urlid', 'user__urlid', 'contact__urlid']
    ordering = ['urlid']

    def get_queryset(self, request):
        # Hide distant contacts
        queryset = super(ContactAdmin, self).get_queryset(request)
        internal_ids = [x.pk for x in queryset if not Model.is_external(x)]
        return queryset.filter(pk__in=internal_ids)


