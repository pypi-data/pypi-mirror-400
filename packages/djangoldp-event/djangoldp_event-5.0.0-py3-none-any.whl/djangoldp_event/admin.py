from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from djangoldp.admin import DjangoLDPAdmin
from django.db import models
from .models import Event


class EventAdmin(DjangoLDPAdmin):
    list_display = ('name', 'shortDescription', 'circle', 'startDate', 'endDate', 'get_author_name', 'location')
    exclude = ('urlid', 'slug', 'is_backlink', 'allow_create_backlink')
    search_fields = ['urlid', 'name', 'shortDescription', 'longDescription']
    ordering = ['id', 'circle', 'startDate']

    def get_author_name(self, obj):
      if obj.author is not None:
        return obj.author.name()
      else:
        return "None"

    get_author_name.admin_order_field  = 'user'  #Allows column order sorting
    get_author_name.short_description = 'Author Name'  #Renames column head

admin.site.register(Event, EventAdmin)
    
