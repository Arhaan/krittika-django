from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.db.models import Q

import datetime

from events.models import Event

from krittika import settings
from krittika.forms import ContactForm
from krittika.scripts import get_apod as apod
from krittika.decorators import check_recaptcha


def home_view(request):
    data = {'apod_url': apod.url, 'apod_title': apod.title,
            'apod_expl': apod.explanation, 'apod_media_type': apod.media_type}
    today = datetime.date.today()

    pinned_events = Event.objects.filter(is_pinned=True)
    side_events = Event.objects.filter(is_pinned=False)

    upcoming_events = side_events.filter(Q(startTime__date__gte=today) | Q(endTime__date__gte=today)).order_by('startTime')
    data['pinned_events'] = pinned_events
    data['upcoming_events'] = upcoming_events
    return render(request, 'home.html', data)


@check_recaptcha
def about_view(request):
    return render(request, 'about.html')


def team_view(request):
    return render(request, 'team.html')


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid() and request.recaptcha_is_valid:
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message'] + \
                '\n\n\n from ' + name + ', Email: ' + email
            subject = 'New enquiry from {} | Krittika website'.format(name)
            email_from = settings.EMAIL_HOST_USER
            recipient_list = settings.MAILING_LIST
            send_mail(subject, message, email_from, recipient_list)
            messages.success(request, "Thanks for contacting us")
            return redirect('about')
        else:
            messages.success(request, "Invalid form, please try again")
            return redirect('about')
    else:
        form = ContactForm()
    return render(request, 'contactUs.html', {'form': form})


def faqs_view(request):
    return render(request, 'frequentlyAskedQuestions.html')


def code_of_conduct(request):
    return render(request, 'codeOfConduct.html')

def googleVerificationView(request):
    return render(request, 'google076b379728b3ef28.html')

def githubSite(request):
    return redirect("https://krittikaiitb.github.io/")

