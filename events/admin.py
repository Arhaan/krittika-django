from django.contrib import admin

# Register your models here.
from events.models import Event


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'body', 'startTime', 'endTime', 'venue')
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Event, EventAdmin)
