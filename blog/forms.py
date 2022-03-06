from django import forms

from ckeditor_uploader.widgets import CKEditorUploadingWidget

from blog import models


class CreatePost(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter post heading'
        }
    ))

    subtitle = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter post sub-heading'
        }
    ))

    body = forms.CharField(widget=CKEditorUploadingWidget())

    body_new = forms.CharField(widget=CKEditorUploadingWidget(), required=False)

    multiple_authors = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter comma separated names if this post is contributed by multiple authors'
        }),
        required=False)

    class Meta:
        model = models.Post
        # ADMIN-INTERFACE: is_approved is passed too.
        fields = ['title', 'subtitle', 'body', 'body_new', 'thumbnail', 'tags', 'is_approved', 'multiple_authors']

# ADMIN-INTERFACE: SUGGESTION COMMENTS:


class SuggestionForm(forms.ModelForm):
    # body = forms.CharField(widget = CKEditorUploadingWidget())
    body = forms.CharField(widget=forms.Textarea(
        # The textarea height adjusts according to the content
        attrs={
            'class': 'form-control',
            # 'style' : 'width:80%;',
            'rows': '1',
            'oninput': 'this.style.height = "";this.style.height = this.scrollHeight + 3 + "px"',
        }
    ))

    class Meta:
        model = models.Suggestions
        fields = ['body', ]
