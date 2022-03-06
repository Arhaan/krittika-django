from django.contrib import admin

from users.models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'roll_number',
        'name',
        'email',
        'profile_picture',
        'store_json',
    )


admin.site.register(UserProfile, UserProfileAdmin)
