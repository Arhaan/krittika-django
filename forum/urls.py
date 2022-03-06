from django.urls import path

from forum import views


app_name = 'forum'  # Specifies the name of the app.

urlpatterns = [
    # For forum posts:
    path('', views.forum_home, name="forum_home"),
    path('create/', views.create_post, name="create_post"),
    path('<slug:slug>', views.detailed_post, name="detailed_post"),
    path('<slug:slug>/edit', views.edit_post, name='edit_post'),
    path('<slug:slug>/delete', views.delete_post, name='delete_post'),

    path('<slug:slug>/comment/<int:id>/delete', views.delete_comment, name='delete_comment'),

    # For forum topics:
    path('topics/', views.all_topics, name='all_topics'),
    path('add_topic/', views.addTopic, name='add_topic'),
    path('topics/<slug:slug>', views.detailed_topic, name='detailed_topic'),
    path('topics/<slug:slug>/edit', views.edit_topic, name='edit_topic'),
    path('topics/<slug:slug>/delete', views.delete_topic, name='delete_topic'),

    path('logout/', views.logout_page, name="logout"),
]
