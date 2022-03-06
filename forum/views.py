from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect

import bleach
from collections import Counter
import markdown as md

from users.forms import ApproveTopicForm

from forum.forms import AddTopic, CommentForm, CreatePost
from forum.models import ForumPost, ForumTopic, Comment


def forum_home(request):

    # allPosts = ForumPost.objects.filter(Q(topic__is_approved=True)).distinct()

    # Exclude all posts containing an un-approved topic:
    allPosts = ForumPost.objects.exclude(topic__is_approved=False)

    # Implementing searchbar
    query = request.GET.get("q")
    if query:
        allPosts = allPosts.filter(Q(title__icontains=query) |
                                   Q(body__icontains=query) |
                                   Q(topic__name__icontains=query) |  # This works great evn though topic is a m2m relationship
                                   Q(author__user_profile__name__icontains=query)).distinct()  # Removes duplicate items.

    # Implementing Paginator.
    paginator = Paginator(allPosts, 10)  # Shows 10 posts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Most common topics, may contain duplicates:
    topics_list = []

    posts = ForumPost.objects.all()  # Seperate queryset is required as the allPosts queryset gets modified during search queries

    # TODO: Make efficient
    for post in posts:
        topics = post.topic.all()
        for topic in topics:
            if topic.is_approved:
                topics_list.append(topic)

    # topics_list = [post.topic for post in posts if post.topic.is_approved]
    trending = dict(Counter(topics_list).most_common()[:7]).keys()  # Shows 7 most common topics
    return render(request, 'forum/forumHome.html', {'page_obj': page_obj, 'trending': trending})


def detailed_post(request, slug):

    post = ForumPost.objects.get(slug=slug)

    topics = post.topic.all()

    all_topics_valid = True
    for topic in topics:
        if not topic.is_approved:
            all_topics_valid = False
            break

    if all_topics_valid:
        # Fetching all the comments related to a particular post.
        comments = post.comments.all()
        if request.method == 'POST':
            form = CommentForm(request.POST, request.FILES)
            try:
                parent_id = request.POST['comment_id']
            except ...:
                parent_id = None
                pass
            if form.is_valid():
                instance = form.save(commit=False)
                instance.post = post
                instance.user = request.user
                instance.content = bleach.clean(md.markdown(instance.content))
                if parent_id is not None:
                    instance.parent = comments.get(id=parent_id)
                else:
                    # Root comment
                    instance.parent = None
                instance.save()
                messages.success(request, "Comment added successfully")
                return redirect('forum:detailed_post', slug=post.slug)
        else:
            form = CommentForm()
        return render(request, 'forum/detailedPost.html', {'post': post, 'form': form, 'comments': comments, 'topics': topics})
    else:
        messages.success(
            request, "This post belongs to a topic which isn't approved")
        return redirect('forum:forum_home')


# Decorator which ensures these functions are available only to logged in users.
@login_required()
def create_post(request):
    if request.method == 'POST':
        form = CreatePost(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            instance.save()
            # for sub in instance.topic.subscribers.all():
            #     instance.followers.add(sub)
            # instance.save()
            # Save the Many-to-Many relationships:
            form.save_m2m()
            messages.success(request, "Created successfully")
            return redirect('forum:detailed_post', slug=instance.slug)
    else:
        form = CreatePost()
    return render(request, 'forum/createPost.html', {'form': form})


@login_required()
def edit_post(request, slug):
    post = ForumPost.objects.get(slug=slug)
    # Enabling moderators to edit and delete all posts:
    if request.user == post.author or request.user.user_profile.is_moderator:
        if request.method == "POST":
            form = CreatePost(request.POST, request.FILES, instance=post)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                form.save_m2m()
                messages.success(request, "Edited successfully")
                return redirect('forum:detailed_post', slug=instance.slug)
            else:
                print(form.errors)
                messages.success(request, "Invalid form")
                return redirect('forum:detailed_post', slug=post.slug)
        else:
            # Thus, as instance is passed, the form comes preloaded with previous data.
            form = CreatePost(instance=post)
        return render(request, 'forum/editPost.html', {'form': form})
    else:
        messages.success(request, "You aren't allowed to edit this post.")
        return redirect('forum:detailed_post', slug=post.slug)


@login_required()
def delete_post(request, slug):
    post_to_delete = ForumPost.objects.get(slug=slug)
    # Allowing superusers to delete posts:
    if request.user == post_to_delete.author or request.user.user_profile.is_moderator:
        post_to_delete.delete()
        messages.success(request, "Post deleted")  # Post deleted successfully.
        return redirect('forum:forum_home')
    else:
        messages.success(request, "You aren't allowed to delete posts.")
        return redirect('forum:detailed_post', slug=post_to_delete.slug)


# FOR FORUM TOPICS:
def all_topics(request):
    allTopics = ForumTopic.objects.filter(is_approved=True)
    # Implementing searchbar: To be finalized once the users model is fianlized.
    query = request.GET.get("q")
    if query:
        allTopics = allTopics.filter(Q(name__icontains=query) |
                                     Q(description__icontains=query)).distinct()  # Removes duplicate items.
    # Implementing Paginator.
    paginator = Paginator(allTopics, 20)  # Shows 20 topics per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'forum/allTopics.html', {'page_obj': page_obj})


@login_required()
def addTopic(request):
    if request.user.user_profile.is_moderator:
        if request.method == 'POST':
            form = AddTopic(request.POST, request.FILES)
            if form.is_valid():
                instance = form.save(commit=False)  # Instance of the post.
                instance.author = request.user
                instance.save()  # Saving to database.
                if request.user.user_profile.is_moderator:
                    if instance.is_approved:
                        messages.success(request, "Topic added successfully")
                    else:
                        messages.success(
                            request, "Topic added, but not approved")
                else:
                    messages.success(
                        request, "Topic suggestion sent to the admins for approval")
                return redirect('forum:forum_home')
            else:
                messages.success(request, "Invalid form")
                return redirect('forum:forum_home')
        else:
            form = AddTopic()
        return render(request, 'forum/addTopic.html', {'form': form})
    else:
        messages.success(request, "You aren't allowed to add topics.")
        return redirect('forum:forum_home')


def detailed_topic(request, slug):
    topic = ForumTopic.objects.get(slug=slug)

    # These will be used later
    temp = topic.__dict__
    original_approval_status = temp['is_approved']
    original_archival_status = temp['is_archived']

    # Posts related to that topic:
    posts = ForumPost.objects.filter(Q(topic__name__contains=topic))

    # Implementing Paginator.
    paginator = Paginator(posts, 10)  # Shows 10 posts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if topic.is_approved or request.user.user_profile.is_moderator or request.user == topic.author:
        if request.method == 'POST':
            post_keys = request.POST
            approvalForm = ApproveTopicForm(request.POST, request.FILES, instance=topic)
            if approvalForm.is_valid():
                # Instance of the post.
                if 'approve_button' in post_keys or 'remove_button' in post_keys:
                    instance = approvalForm.save(commit=False)
                    instance.is_archived = original_archival_status  # Don't change the other field
                    instance.save()  # Saving to database.
                    if instance.is_approved:
                        # Success message displayed.
                        messages.success(request, "Approval status: True")
                    else:
                        messages.success(request, "Approval status: False")
                elif 'archive_button' in post_keys or 'unarchive_button' in post_keys:
                    instance = approvalForm.save(commit=False)
                    print('instance: {}'.format(instance.is_approved), 'topic: {}'.format(original_approval_status))
                    instance.is_approved = original_approval_status  # Don't change the other field
                    instance.save()  # Saving to database.
                    if instance.is_archived:
                        messages.success(request, "Archival status: True")
                    else:
                        messages.success(request, "Archival status: False")

                return redirect('forum:detailed_topic', slug=topic.slug)
        else:
            approvalForm = ApproveTopicForm(instance=topic)
        return render(request, 'forum/detailedTopic.html', {'topic': topic, 'form': approvalForm, 'page_obj': page_obj})
    else:
        messages.success(request, "This topic has not been approved yet")
        return redirect('forum:forum_home')


@login_required()
def edit_topic(request, slug):
    topic = ForumTopic.objects.get(slug=slug)
    # Enabling mods to edit and delete all topics:
    if request.user.user_profile.is_moderator:
        if request.method == "POST":
            form = AddTopic(request.POST, request.FILES, instance=topic)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, "Topic edited successfully")
                return redirect('forum:detailed_topic', slug=instance.slug)
            else:
                messages.success(request, "Invalid form")
                return redirect('forum:detailed_topic', slug=instance.slug)
        else:
            form = AddTopic(instance=topic)
        return render(request, 'forum/editTopic.html', {'form': form})
    else:
        messages.success(request, "You aren't allowed to edit topics.")
        return redirect('forum:detailed_topic', slug=topic.slug)


@login_required()
def delete_topic(request, slug):
    topic_to_delete = ForumTopic.objects.get(slug=slug)
    # Allowing mods to delete posts:
    if request.user.user_profile.is_moderator:
        topic_to_delete.delete()
        # Topic deleted successfully.
        messages.success(request, "Topic deleted")
        return redirect('forum:forum_home')
    else:
        messages.success(request, "You aren't allowed to delete topics.")
        return redirect('forum:detailed_topic', slug=topic_to_delete.slug)


@login_required()
def logout_page(request):
    logout(request)
    messages.success(request, "You've been signed out. Come back soon!")
    return redirect('forum:forum_home')


@login_required()
def delete_comment(request, slug, id):
    comment = Comment.objects.get(pk=id)
    # We don't delete the comment, just change it's content
    # Else it'll interfere in the tree structure
    if request.user == comment.user or request.user.user_profile.is_moderator:
        comment.content = '<em>This comment has been deleted</em>'
        comment.is_deleted = True
        comment.save()
        messages.success(request, 'Comment removed successfully')
        return redirect('forum:detailed_post', slug=slug)
    else:
        messages.success(request, "You aren't allowed to delete comments.")
        return redirect('forum:detailed_post', slug=slug)
