from django.contrib import admin

from forum.models import ForumPost, ForumTopic, Comment


class ForumPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'body',)
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(ForumPost, ForumPostAdmin)
admin.site.register(ForumTopic)
admin.site.register(Comment)
