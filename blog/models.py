from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from uuid import uuid4  # Unique slugs

from ckeditor_uploader.fields import RichTextUploadingField  # RichText interface for admin interface.
from taggit.managers import TaggableManager  # For managing tags

from blog.validators import validate_file_size


class Post(models.Model):
    title = models.CharField(max_length=150)  # Title limit set to 150 characters.
    subtitle = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique=True,max_length=255)

    body = RichTextUploadingField()
    body_new = RichTextUploadingField(blank=True, null=True)

    # Uploads to the folder named 'blogMedia' inside 'media'.
    thumbnail = models.ImageField(upload_to='blogMedia', null=True, blank=True, validators=[validate_file_size])

    # Automatically populate this with date and time at the time of posting.
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)  # To be updated when we edit the posts.

    author = models.ForeignKey(User, default=None, on_delete=models.DO_NOTHING,)

    multiple_authors = models.CharField(max_length=500, blank=True)

    # ADMIN-INTERFACE:
    is_approved = models.BooleanField(default=False)

    # TAGS
    tags = TaggableManager(blank=True)

    def __str__(self):
        return self.title

    def snippet(self):
        bodyText = self.body
        if len(bodyText) > 400:
            return bodyText[:400] + "..."  # Snippet of 400 characters to be displayed at home-page of the blog.
        else:
            return bodyText

    def isUpdated(self):
        dateEdit = self.updated
        datePublished = self.date
        difference = dateEdit - datePublished
        diffInSeconds = difference.days * 24 * 3600 + difference.seconds
        return (diffInSeconds > 60)

    # overriding the save method. SlugField is automatically populated as we enter the title.
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title + "-" + str(uuid4()))
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ["-date", "-updated"]  # Specifies the order in which the posts are displayed, latest first.


class Suggestions(models.Model):
    # 'on_delete' set to CASACDE, if not, then we won't be able to delete posts having comments.
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()  # RichTextUploadingField()

    timestamp = models.DateTimeField(auto_now_add=True)

    is_suggestion = models.BooleanField(default=False)  # Specifies whether a comment is a suggestion or not.

    def __str__(self):
        return '{}-{}'.format(self.post.title, self.user.username)
