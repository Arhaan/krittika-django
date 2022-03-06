from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect

import bleach
from collections import Counter
from lxml.html.diff import htmldiff
import markdown as md

from users.forms import ApprovePostForm

from blog.forms import SuggestionForm, CreatePost
from blog.models import Post, Suggestions


def all_posts(request):
    """ADMIN-APPROVAL:
       Only approved posts will be shown to everyone, the post waiting for approval
       shall be shown to the author at his profile page, under the tab: 'waiting for approval'
       And to the admin on his interface.
    """
    allPosts = Post.objects.filter(is_approved=True)
    # Implementing searchbar: To be finalized once the users model is fianlized.
    query = request.GET.get("q")
    if query:
        allPosts = allPosts.filter(Q(title__icontains=query) |
                                   Q(body__icontains=query) |
                                   Q(multiple_authors__icontains=query) |
                                   Q(tags__name__icontains=query)).distinct()  # Removes duplicate items.
        # Q(author__username__icontains=query)|
        # Q(author__first_name__icontains=query)|
        # Q(author__last_name__icontains=query))
    # Implementing Paginator.
    paginator = Paginator(allPosts, 3)  # Shows 3 posts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Most common tags:
    tags_list = []
    # Seperate queryset is required as the allPosts queryset gets modified during search queries
    posts = Post.objects.filter(is_approved=True)
    for post in posts:
        tags_list_i = [tag.name for tag in list(post.tags.all())]
        tags_list += tags_list_i
    trending = dict(Counter(tags_list).most_common()[:7]).keys()
    return render(request, 'blog/allPosts.html', {'allPosts': allPosts, 'page_obj': page_obj, 'trending': trending})


def detailed_post(request, slug):
    post = Post.objects.get(slug=slug)
    suggestions = Suggestions.objects.filter(post=post).order_by('timestamp')
    tags = post.tags.all()

    post_is_edited = (post.body != post.body_new)

    if post.is_approved or request.user == post.author or request.user.user_profile.is_moderator:
        if request.method == 'POST':
            suggestionsForm = SuggestionForm(request.POST, request.FILES)
            approvalForm = ApprovePostForm(request.POST, request.FILES, instance=post)
            if suggestionsForm.is_valid():
                # We get all the necessary data and create a comment:
                is_suggestion = not(post.is_approved)
                body = bleach.clean(md.markdown(request.POST.get('body')))
                suggestion = Suggestions.objects.create(
                    post=post, user=request.user, body=body, is_suggestion=is_suggestion)
                suggestion.save()
                messages.success(request, "Comment added")  # Success message displayed.
                return redirect('blog:detailed_post', slug=post.slug)
            if approvalForm.is_valid():
                instance = approvalForm.save(commit=False)  # Instance of the post.
                instance.save()  # Saving to database.
                messages.success(request, "Post visibility successfully changed.")  # Success message displayed.
                return redirect('users:admin_interface')
        else:
            suggestionsForm = SuggestionForm()
            approvalForm = ApprovePostForm(instance=post)
        return render(request, 'blog/detailedPost.html',
                      {'post': post, 'suggestions': suggestions, 'suggestionsForm': suggestionsForm,
                       'approvalForm': approvalForm, 'tags': tags, 'is_edited': post_is_edited})


@login_required()  # Decorator which ensures these functions are available only to logged in users.
def create_post(request):
    if request.method == 'POST':
        form = CreatePost(request.POST, request.FILES)  # FILES for image files.
        if form.is_valid():
            instance = form.save(commit=False)  # Instance of the post.
            instance.author = request.user

            # Initialize body_new with body
            instance.body_new = instance.body

            # "a,b,c,d" --> a, b, c and d

            if instance.multiple_authors:
                authors = instance.multiple_authors  # CSV of author names
                # Pre-process:
                authors = authors.split(',')
                if len(authors) > 1:
                    authors = [author.strip() for author in authors]
                    string_to_be_stored = ', '.join(authors[:len(authors) - 1])
                    string_to_be_stored = string_to_be_stored + " and " + authors[-1]
                    instance.multiple_authors = string_to_be_stored
                else:
                    instance.multiple_authors = authors[0]
            else:
                instance.multiple_authors = instance.author.user_profile.name

            instance.save()  # Saving to database.
            # Without this next line the tags won't be saved.
            form.save_m2m()
            if not request.user.user_profile.is_moderator:
                # Success message displayed.
                messages.success(request, "Your post has been sent to the admins for approval.")
            elif instance.is_approved is False:
                messages.success(request, "Your post has been added, but not approved.")
            else:
                messages.success(request, "Your post has been approved and added.")
            return redirect('blog:all_posts')
    else:
        form = CreatePost()
    return render(request, 'blog/createPost.html', {'form': form})


@login_required()
def edit_post(request, slug):
    post = Post.objects.get(slug=slug)
    # Enabling superusers to edit and delete all posts:
    # If admin edits it, he becomes the author of the post. Thus, 'instance.author=request.user' is commented out.
    if request.user == post.author:  # or request.user.user_profile.is_admin:
        if request.method == "POST":
            form = CreatePost(request.POST, request.FILES, instance=post)
            if form.is_valid():
                instance = form.save(commit=False)
                if request.user.user_profile.is_admin:  # If post is made by/edited by an admin
                    instance.body = instance.body_new  # Save changes directly if admin
                # instance.author = request.user
                instance.save()
                # Without this next line the tags won't be saved.
                form.save_m2m()
                if request.user.user_profile.is_admin:  # If post is made by/edited by an admin
                    messages.success(request, "Edited successfully!")
                else:
                    messages.success(request, "Edits successful, changes sent for approval.")
                return redirect('blog:detailed_post', slug=instance.slug)
            else:
                messages.success(request, "Invalid form")
                return redirect('blog:detailed_post', slug=instance.slug)
        else:
            # Thus, as instance is passed, the form comes preloaded with previous data.
            form = CreatePost(instance=post)
        return render(request, 'blog/editPost.html', {'form': form, 'tags': post.tags.all()})
    else:
        messages.success(request, "You aren't allowed to edit this post.")
        return redirect('blog:detailed_post', slug=post.slug)


@login_required
def approve_edits(request, slug):
    post = Post.objects.get(slug=slug)
    if request.user.user_profile.is_admin:
        if post.body == post.body_new:
            messages.success(request, "No changes found.")
            return redirect('blog:detailed_post', slug=post.slug)
        else:
            post.body = post.body_new
            post.save()
            messages.success(request, "Changes approved successfully")
            return redirect('blog:detailed_post', slug=post.slug)
    else:
        messages.success(request, "You aren't allowed to approve changes.")
        return redirect('blog:detailed_post', slug=post.slug)


def view_edits(request, slug):
    post = Post.objects.get(slug=slug)
    if request.user.user_profile.is_admin:
        if post.body == post.body_new:
            messages.success(request, "No changes found.")
            return redirect('blog:detailed_post', slug=post.slug)
        else:
            # See here: https://lxml.de/api/lxml.html.diff-module.html#htmldiff
            changes = htmldiff(post.body, post.body_new)
            return render(request, 'blog/viewEdits.html', {'post': post, 'changes': changes})
    else:
        messages.success(request, "You aren't allowed to view the edits.")
        return redirect('blog:detailed_post', slug=post.slug)


@login_required()
def delete_post(request, slug):
    post_to_delete = Post.objects.get(slug=slug)
    # Allowing superusers to delete posts:
    if request.user == post_to_delete.author or request.user.user_profile.is_admin:
        post_to_delete.delete()
        messages.success(request, "Post deleted")  # Post deleted successfully.
        return redirect('blog:all_posts')
    else:
        messages.success(request, "You aren't allowed to delete posts.")
        return redirect('blog:detailed_post', slug=post_to_delete.slug)


@login_required()
def logout_page(request):
    logout(request)
    messages.success(request, "You've been signed out. Come back soon!")
    return redirect('blog:all_posts')


@login_required()
def delete_comment(request, id):
    comment_to_delete = Suggestions.objects.get(pk=id)
    slug = comment_to_delete.post.slug
    if request.user == comment_to_delete.user or request.user.user_profile.is_admin:
        comment_to_delete.delete()
        messages.success(request, 'Comment deleted successfully')
        return redirect('blog:detailed_post', slug=slug)
    else:
        messages.success(request, "You aren't allowed to delete comments.")
        return redirect('blog:detailed_post', slug=slug)

# Inplace editing of the blog comments:


@login_required()
def edit_comment(request, id):
    comment = Suggestions.objects.get(pk=id)
    post = comment.post
    suggestions = Suggestions.objects.filter(post=post).order_by('timestamp')
    tags = post.tags.all()
    edit_mode = True

    if post.is_approved or request.user == post.author or request.user.user_profile.is_moderator:
        if request.method == 'POST':
            post_keys = request.POST
            editForm = SuggestionForm(request.POST, request.FILES, instance=comment)
            approvalForm = ApprovePostForm(request.POST, request.FILES, instance=post)
            if approvalForm.is_valid():
                if 'approve_button' in post_keys or 'remove_button' in post_keys:
                    instance = approvalForm.save(commit=False)
                    instance.save()  # Saving to database.
                    messages.success(request, "Post visibility successfully changed.")  # Success message displayed.
                    return redirect('users:admin_interface')
            if editForm.is_valid():
                if 'edit_suggestion' in post_keys:
                    instance = editForm.save(commit=False)
                    instance.save()
                    messages.success(request, "Comment edited successfully")
                    return redirect('blog:detailed_post', slug=post.slug)
        else:
            # suggestionsForm = SuggestionForm()
            approvalForm = ApprovePostForm(instance=post)
            editForm = SuggestionForm(instance=comment)
        return render(request, 'blog/detailedPost.html',
                      {'post': post, 'suggestions': suggestions,
                       'approvalForm': approvalForm, 'editForm': editForm,
                       'tags': tags, 'edit_mode': edit_mode, 'id': id})
