from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from ckeditor_uploader import views as ckeditor_views

from krittika.views import home_view, about_view, team_view, contact_view, faqs_view, code_of_conduct, googleVerificationView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', home_view, name='home'),
    # path('about/', about_view, name='about'),
    path('about/team/', team_view, name='team'),
    path('google076b379728b3ef28.html', googleVerificationView, name='google')
    # path('about/contact-us/', contact_view, name='contact'),
    # path('faqs/', faqs_view, name='faqs'),
    # path('code-of-conduct/', code_of_conduct, name='code_of_conduct'),

    # Our Apps:
    # path('blog/', include('blog.urls')),
    # path('', include('users.urls')),
    # path('events/', include('events.urls')),
    # path('discussion-forum/', include('forum.urls')),

    # path('inbox/notifications/', include('notifications.urls')),

    # For CKEditor:
    # path('ckeditor/', include('ckeditor_uploader.urls')),
    path('ckeditor/upload/', login_required(ckeditor_views.upload), name='ckeditor_upload'),
    path('ckeditor/browse/', never_cache(login_required(ckeditor_views.browse)), name='ckeditor_browse')
]

urlpatterns += staticfiles_urlpatterns()  # Serves static files.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
