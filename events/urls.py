from django.urls import path

from events import views


app_name = 'events'  # Specifies the name of the app.

urlpatterns = [
    path('', views.all_events, name="all_events"),
    path('upcoming/', views.upcoming_events, name="upcoming_events"),
    path('past/', views.past_events, name="past_events"),
    path('create/', views.create_event, name="create_event"),
    path('<slug:slug>', views.detailed_event, name="detailed_event"),
    path('<slug:slug>/edit', views.edit_event, name='edit_event'),
    path('<slug:slug>/delete', views.delete_event, name='delete_event'),
    path('logout/', views.logout_page, name="logout"),
]
