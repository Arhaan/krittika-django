from django.contrib import messages
from django.contrib.auth import (login, logout)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

import requests

from blog.models import Post
from forum.models import ForumPost, ForumTopic
from krittika import settings

from users.forms import UserProfileForm
from users.models import UserProfile


def signin(request):
    url = settings.SSO_URL
    client = '?client_id=' + settings.SSO_CLIENT_ID
    response_type = '&response_type=' + 'code'
    scope = '&scope=' + settings.SCOPE
    state = '&state=' + 'some_state'
    redirect_uri = '&redirect_uri=' + settings.SSO_REDIRECT_URL

    goto = url + client + response_type + scope + state + redirect_uri
    return HttpResponseRedirect(goto)


def auth(request):
    if 'error' in request.GET or 'code' not in request.GET:
        messages.success(request, "Unable to login. Try again...")
        return HttpResponseRedirect(reverse('home'))

    auth_code = request.GET.get('code')
    redir = settings.SSO_REDIRECT_URL
    post_data = 'code=' + auth_code + '&redirect_uri=' + redir + '&grant_type=authorization_code'

    # Get our access token
    response = requests.post(
        settings.SSO_TOKEN_URL,
        data=post_data,
        headers={
            "Host": "gymkhana.iitb.ac.in",
            "Authorization": "Basic " + settings.SSO_CLIENT_ID_SECRET_BASE64,
            "Content-Type": "application/x-www-form-urlencoded",
            "charset": "UTF-8"
        }
    )
    response_json = response.json()

    if 'access_token' not in response_json:
        messages.success(request, "Unable to login. Try again...")
        return HttpResponseRedirect(reverse('home'))

    # Get the user's profile
    profile_response = requests.get(
        settings.SSO_PROFILE_URL,
        headers={
            "Authorization": "Bearer " + response_json['access_token'],
        })
    profile_json = profile_response.json()

    if 'roll_number' in profile_json and 'first_name' in profile_json and 'last_name' in profile_json and 'email' in profile_json:
        # Find the user from database
        roll_number = profile_json['roll_number']
        query = Q(username=roll_number)
        user = User.objects.filter(query).first()

        # Create a new user if not found
        if not user:
            user = User.objects.create_user(roll_number)

        login(request, user)

        # Retriving the previous profile_json
        current_json = user.user_profile.store_json
        if current_json is None:
            current_json = {
                'roll_number': None,
                'first_name': None,
                'last_name': None,
                'email': None
            }

        # Roll Number
        user.user_profile.roll_number = profile_json['roll_number']

        # is_admin
        if user.user_profile.roll_number in settings.admin_list:
            user.user_profile.is_admin = True
            user.user_profile.is_moderator = True
        else:
            user.user_profile.is_admin = False

        # Name
        if current_json['first_name'] != profile_json['first_name'] or current_json['last_name'] != profile_json['last_name']:
            if profile_json['first_name']:
                user.user_profile.name = profile_json['first_name']
            if profile_json['last_name']:
                user.user_profile.name += ' ' + profile_json['last_name']

        # Email IITB
        if current_json['email'] != profile_json['email']:
            user.user_profile.email = profile_json['email']

        # Store this profile_json
        user.user_profile.store_json = profile_json

        # Capitalize the name
        if user.user_profile.name:
            user.user_profile.name = str(user.user_profile.name).title()

        # Save the User Profile
        user.user_profile.save()

        # Save the User
        user.save()

        return HttpResponseRedirect(reverse('users:profile'))
    else:
        logout(request)
        messages.success(request, "You would have to authorize us to access data if you were to login via SSO...")
        return HttpResponseRedirect(reverse('home'))


@login_required
def profile(request):
    """Display User Profile"""
    profile = request.user.user_profile
    userPosts = Post.objects.filter(author=request.user)
    userForumPosts = ForumPost.objects.filter(author=request.user)
    return render(request, 'users/profile.html', {
        'profile': profile,
        'allPosts': userPosts,
        'allForum': userForumPosts
    })


@login_required
def edit_profile(request):
    user = request.user
    user_profile = get_object_or_404(UserProfile, user=user)
    form = UserProfileForm(instance=user_profile)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated the Profile Successfully!")
            return HttpResponseRedirect(reverse('users:profile'))

    return render(request, 'users/edit_profile.html', {
        'form': form,
        'profile': user_profile
    })


@login_required
def admin_interface(request):
    if not request.user.user_profile.is_moderator:
        messages.success(request, "You don't have access to this page!")
        return HttpResponseRedirect(reverse('users:profile'))

    # Blog:
    allPosts = Post.objects.filter(is_approved=False)
    # Forum Topics:
    allTopics = ForumTopic.objects.filter(is_approved=False)
    return render(request, 'users/admin_interface.html', {'allPosts': allPosts, 'allTopics': allTopics})


@login_required
def admin_only(request):
    if not request.user.user_profile.is_admin:
        messages.success(request, "You don't have access to this page!")
        return HttpResponseRedirect(reverse('users:profile'))

    query_remove = request.GET.get("r")
    query_add = request.GET.get("a")

    if query_remove:
        user = User.objects.filter(Q(username=query_remove)).first()
        if user:
            user.user_profile.is_moderator = False
            user.user_profile.save()
            user.save()
        else:
            messages.success(
                request, "This roll number doesn't exist in database\nUser has to login once to be registered in the database.")

    if query_add:
        user = User.objects.filter(Q(username=query_add)).first()
        if user:
            user.user_profile.is_moderator = True
            user.user_profile.save()
            user.save()
        else:
            messages.success(
                request, "This roll number doesn't exist in database\nUser has to login once to be registered in the database.")

    moderators = User.objects.all().filter(user_profile__is_moderator=True)
    return render(request, 'users/admin_only.html', {'mod': moderators})


@login_required()
def logout_page(request):
    logout(request)
    messages.success(request, "You've been signed out. Come back soon!")
    return HttpResponseRedirect(reverse('home'))
