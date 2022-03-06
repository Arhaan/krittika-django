from django import forms

from blog.models import Post
from forum.models import ForumTopic

from users.models import UserProfile


class ApprovePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['is_approved', ]


class ApproveTopicForm(forms.ModelForm):
    class Meta:
        model = ForumTopic
        fields = ['is_approved', 'is_archived']


class UserProfileForm(forms.ModelForm):
    contact_number = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'pattern': '[0-9]{10}', 'title': 'Please enter a valid mobile number', 'maxlength': '10'}))

    class Meta:
        model = UserProfile
        fields = [
            'profile_picture',
        ]
