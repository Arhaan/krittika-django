from django import forms

from events import models


class CreateEvent(forms.ModelForm):

    title = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter event title'
        }))

    subtitle = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter event sub-title'
        }),required=False)

    body = forms.CharField(widget=forms.Textarea(
        # The textarea height adjusts according to the content
        attrs={
            'class': 'form-control',
            'width': '100%',
        }
    ))
    # forms.CharField(widget=CKEditorUploadingWidget())

    venue = forms.CharField(required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter event venue (optional)'
        }))

    startTime = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'],
                                    widget=forms.DateTimeInput(
        format='%d/%m/%Y %H:%M',
        attrs={
            'class': 'form-control',
            'placeholder': 'Select the time when the event starts'
        }))

    endTime = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'], required=False,
                                  widget=forms.DateTimeInput(
        format='%d/%m/%Y %H:%M',
        attrs={
            'class': 'form-control',
            'placeholder': 'Select the time when the event ends (optional)'
        }))

    class Meta:
        model = models.Event
        fields = ['title', 'subtitle', 'startTime', 'endTime', 'body', 'venue', 'thumbnail', 'is_pinned']
