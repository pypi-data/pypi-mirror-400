from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from djangoldp.admin import DjangoLDPAdmin
from .models import Resource

class ResourceAdmin(DjangoLDPAdmin):
    list_display = ('name', 'shortdesc', 'circle', 'type', 'creationDate', 'get_user_name')
    exclude = ('urlid', 'slug', 'is_backlink', 'allow_create_backlink')
    search_fields = ['urlid', 'name', 'shortdesc', 'longdesc']
    ordering = ['id', 'name', 'type']

    def get_user_name(self, obj):
      if obj.user is not None:
        return obj.user.name()
      else:
        return "None"

    get_user_name.admin_order_field  = 'user'  #Allows column order sorting
    get_user_name.short_description = 'Author Name'  #Renames column head

admin.site.register(Resource, ResourceAdmin)