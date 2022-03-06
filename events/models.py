from django.db import models
from django.template.defaultfilters import slugify

from uuid import uuid4

from events.validators import validate_file_size


class Event(models.Model):
    title = models.CharField(max_length=150)  # Title limit set to 150 characters.
    subtitle = models.CharField(max_length=500, blank=True, null=True)
    slug = models.SlugField(unique=True,max_length=255)
    body = models.TextField()  # RichTextUploadingField()
    startTime = models.DateTimeField(blank=True, null=True)
    endTime = models.DateTimeField(blank=True, null=True)
    venue = models.CharField(max_length=150, blank=True)
    # Uploads to the folder named 'blogMedia' inside 'media'.
    thumbnail = models.ImageField(upload_to='eventsMedia', null=True, blank=True, validators=[validate_file_size])

    is_pinned = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def snippet(self):
        bodyText = self.body
        if len(bodyText) > 400:
            return bodyText[:400] + "..."  # Snippet of 400 characters to be displayed at home-page of the blog.
        else:
            return bodyText

    # overriding the save method. SlugField is automatically populated as we enter the title.
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title + "-" + str(uuid4()))
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ["-startTime"]  # Specifies the order in which the posts are displayed, latest first.
