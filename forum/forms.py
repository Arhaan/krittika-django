from django import forms

from ckeditor_uploader.widgets import CKEditorUploadingWidget

from forum import models


class CreatePost(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter post title'
        }
    ))
    body = forms.CharField(widget=CKEditorUploadingWidget())
    # Only approved topics to be shown as choices
    # topic = forms.ModelChoiceField(queryset=models.ForumTopic.objects.filter(is_approved=True, is_archived=False))

    topic = forms.ModelMultipleChoiceField(queryset=models.ForumTopic.objects.filter(is_approved=True, is_archived=False))
    # widget = forms.CheckboxSelectMultiple

    class Meta:
        model = models.ForumPost
        fields = ['title', 'topic', 'body', 'thumbnail']


class AddTopic(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter topic name'
        }
    ))
    description = forms.CharField(widget=CKEditorUploadingWidget(), required=False)

    class Meta:
        model = models.ForumTopic
        fields = ['name', 'description', 'is_approved', 'is_archived']


class CommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(
        # The textarea height adjusts according to the content
        attrs={
            'class': 'form-control',
            'style': 'width:80%;',
            'rows': '1',
            'oninput': 'this.style.height = "";this.style.height = this.scrollHeight + 3 + "px"',
        }
    ))

    class Meta:
        model = models.Comment
        fields = ['content', 'comment_image']
