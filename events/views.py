from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect

import bleach
import datetime
import markdown as md

from events.forms import CreateEvent
from events.models import Event
from events.validators import validate_timings


def query_indexing(query, index_start=None, index_end=None):
    count = query.count()
    if not index_start:
        index_start = 0
    if index_start < 0:
        index_start = count + index_start
    if not index_end:
        index_end = count
    if index_end < 0:
        index_end = count + index_end
    excerpt = []
    i = 0
    for object in query:
        if i in range(index_start, index_end):
            excerpt.append(object)
        i += 1
    return excerpt


def all_events(request):
    today = datetime.date.today()

    pinned_events = Event.objects.filter(is_pinned=True)
    side_events = Event.objects.filter(is_pinned=False)

    upcoming_events = side_events.filter(Q(startTime__date__gte=today) | Q(endTime__date__gte=today)).order_by('startTime')
    return render(request, 'events/allEvents.html', {'pinned_events': pinned_events, 'upcoming_events': upcoming_events})


def upcoming_events(request):
    today = datetime.date.today()
    allEvents = Event.objects.all()
    upcoming_events = allEvents.filter(Q(startTime__date__gte=today) | Q(endTime__date__gte=today)).order_by('startTime')

    # Implementing searchbar.
    query = request.GET.get("q")
    if query:
        upcoming_events = upcoming_events.filter(Q(title__icontains=query) |
                                                 Q(body__icontains=query)).distinct()  # Removes duplicate items.

    # Implementing Paginator.
    paginator = Paginator(upcoming_events, 10)  # Shows 10 events per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'events/upcomingEvents.html', {'upcoming_events': upcoming_events, 'page_obj': page_obj})


def past_events(request):
    today = datetime.date.today()
    allEvents = Event.objects.all()
    past_events = allEvents.filter(Q(startTime__date__lt=today) & ~Q(endTime__date__gte=today))

    # Implementing searchbar.
    query = request.GET.get("q")
    if query:
        past_events = past_events.filter(Q(title__icontains=query) |
                                         Q(body__icontains=query)).distinct()  # Removes duplicate items.
    # Implementing Paginator.
    paginator = Paginator(past_events, 10)  # Shows 10 events per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'events/pastEvents.html', {'past_events': past_events, 'page_obj': page_obj})


def detailed_event(request, slug):
    event = Event.objects.get(slug=slug)
    return render(request, 'events/detailedEvent.html', {'event': event})


@login_required()  # Decorator which ensures these functions are available only to logged in users.
def create_event(request):
    if request.user.user_profile.is_moderator:
        if request.method == 'POST':
            form = CreateEvent(request.POST, request.FILES)  # FILES for image files.
            if form.is_valid():
                instance = form.save(commit=False)  # Instance of the event.
                instance.body = bleach.clean(md.markdown(instance.body))
                if validate_timings(instance):
                    instance.save()  # Saving to database.
                    messages.success(request, "Event added successfully.")  # Success message displayed
                    return redirect('events:detailed_event', slug=instance.slug)
                else:
                    messages.success(request, "Start time must not exceed end time")
            else:
                messages.success(request, "Invalid form, the datetime format must be DD/MM/YYYY HH:MM")
                return redirect('events:all_events')
        else:
            form = CreateEvent()
        return render(request, 'events/createEvent.html', {'form': form})
    else:
        messages.success(request, "Only admins are allowed to create events.")
        return redirect('events:all_events')


@login_required()
def edit_event(request, slug):
    if request.user.user_profile.is_moderator:
        event = Event.objects.get(slug=slug)
        if request.method == "POST":
            form = CreateEvent(request.POST, request.FILES, instance=event)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.body = bleach.clean(md.markdown(instance.body))
                if validate_timings(instance):
                    instance.save()
                    messages.success(request, "Event edited successfully.")
                    return redirect('events:detailed_event', slug=instance.slug)
                else:
                    messages.success(request, "Start time must not exceed end time")
            else:
                messages.success(request, "Invalid form")
                return redirect('events:edit_event', slug=event.slug)
        else:
            # Thus, as instance is passed, the form comes preloaded with previous data.
            form = CreateEvent(instance=event)
        return render(request, 'events/editEvent.html', {'form': form})
    else:
        messages.success(request, "Only admins are allowed to edit events.")
        return redirect('events:all_events')


@login_required()
def delete_event(request, slug):
    if request.user.user_profile.is_moderator:
        event_to_delete = Event.objects.get(slug=slug)
        event_to_delete.delete()
        messages.success(request, "Event deleted")  # Event deleted successfully.
        return redirect('events:all_events')
    else:
        messages.success(request, "Only admins are allowed to delete events.")
        return redirect('events:all_events')


@login_required()
def logout_page(request):
    logout(request)
    messages.success(request, "You've been signed out. Come back soon!")
    return redirect('events:all_events')
