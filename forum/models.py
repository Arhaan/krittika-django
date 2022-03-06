from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from uuid import uuid4

from mptt.models import MPTTModel, TreeForeignKey  # For implementing threaded comments
from ckeditor_uploader.fields import RichTextUploadingField

from forum.validators import validate_file_size


class ForumTopic(models.Model):
    name = models.CharField(max_length=255)
    description = RichTextUploadingField(blank=True)
    slug = models.SlugField(unique=True,max_length=255)

    author = models.ForeignKey(User, default=None, on_delete=models.CASCADE)

    is_approved = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def snippet(self):
        bodyText = self.description
        if len(bodyText) > 200:
            return bodyText[:200] + "..."
        else:
            return bodyText

    class Meta:
        ordering = ['name']


class ForumPost(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True,max_length=255)
    body = RichTextUploadingField()
    thumbnail = models.ImageField(upload_to='forumMedia', null=True, blank=True, validators=[validate_file_size])

    author = models.ForeignKey(User, default=None, on_delete=models.CASCADE)

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    topic = models.ManyToManyField(ForumTopic)

    def __str__(self):
        return self.title

    def snippet(self):
        bodyText = self.body
        if len(bodyText) > 400:
            return bodyText[:400] + "..."
        else:
            return bodyText

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title + "-" + str(uuid4()))
        return super().save(*args, **kwargs)

    def isUpdated(self):
        dateEdit = self.updated
        datePublished = self.timestamp
        difference = dateEdit - datePublished
        diffInSeconds = difference.days * 24 * 3600 + difference.seconds
        return (diffInSeconds > 60)

    class Meta:
        ordering = ["-timestamp"]


# Reference: https://stackoverflow.com/questions/48677262/django-proper-way-to-implement-threaded-comments
class Comment(MPTTModel):
    # Post to which the comment is linked:
    post = models.ForeignKey(ForumPost, related_name='comments', on_delete=models.CASCADE)
    # 'Parent' of a Comment, Root node Comments have Parent = None.
    # 'db_index' set to True for faster retrieval of data.
    # By default, the comment will be added as a Root comment.
    parent = TreeForeignKey('self', null=True, blank=True, default=None, db_index=True,
                            related_name='children', on_delete=models.CASCADE)
    # Person who made the comment
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # RichTextUploadingField() # The body of the comment:
    content = models.TextField()

    comment_image = models.ImageField(upload_to='forumMedia/commentMedia', blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    is_deleted = models.BooleanField(default=False)

    class MPTTMeta:
        order_insertion_by = ['timestamp']  # Earlier first, Latest later.

    def __str__(self):  # Not used anywhere
        return self.content[:20]
