from django.urls import path

from users import views


app_name = 'users'

urlpatterns = [
    path('login/', views.signin, name='login'),
    path('authorization/', views.auth, name='authorization'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('logout/', views.logout_page, name='logout'),
    path('profile/admin_interface/', views.admin_interface, name='admin_interface'),
    path('admin_only/', views.admin_only, name='admin_only')
]
