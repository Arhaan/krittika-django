from django.urls import path

from blog import views

app_name = 'blog'  # Specifies the name of the app.

urlpatterns = [
    # Posts:
    path('', views.all_posts, name="all_posts"),
    path('create/', views.create_post, name="create_post"),
    path('<slug:slug>', views.detailed_post, name="detailed_post"),
    path('<slug:slug>/edit', views.edit_post, name='edit_post'),
    path('<slug:slug>/view_edits', views.view_edits, name='view_edits'),
    path('<slug:slug>/approve_edits', views.approve_edits, name='approve_edits'),
    path('<slug:slug>/delete', views.delete_post, name='delete_post'),
    # Comments:
    path('comment/<int:id>/delete', views.delete_comment, name='delete_comment'),
    path('comment/<int:id>/edit', views.edit_comment, name='edit_comment'),
    path('logout/', views.logout_page, name="logout"),
]
