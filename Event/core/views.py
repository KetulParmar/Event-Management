from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import Event
from django.contrib.auth.decorators import login_required
from accounts.models import user_Data

def home1(request):
    user_id = request.session.get('user_id')
    if user_id:
        user = user_Data.objects.get(id=user_id)
    else:
        user = None

    data = Event.objects.filter(organizer_id=user_id) if user else []
    return render(request, 'home.html', {'events': data})

def create_event(request):
    if request.method == "POST":
        organizer_username = request.POST.get("organizer", "").strip()

        # Validate organizer exists
        try:
            organizer = user_Data.objects.get(username=organizer_username)
        except user_Data.DoesNotExist:
            messages.error(request, "Organizer does not exist.")
            return redirect("core:create_event")

        # Get form data
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        category = request.POST.get("category", "").strip()
        other_category = request.POST.get("other_category", "").strip()
        start_date = request.POST.get("start_date", "").strip()
        end_date = request.POST.get("end_date", "").strip()
        venue = request.POST.get("venue", "").strip()
        venue_address = request.POST.get("venue_address", "").strip()
        contact_number = request.POST.get("contact_number", "").strip()
        social_media = request.POST.get("social_media", "").strip()
        max_attendees = request.POST.get("max_attendees", "").strip() or 0
        price = request.POST.get("price", "").strip() or 0.00

        # Handle file uploads to Cloudinary
        event_pdf = request.FILES.get("event_pdf")
        event_image = request.FILES.get("event_image")

        # Validate required fields
        if not title or not start_date or not end_date or not venue:
            messages.error(request, "Title, start date, end date, and venue are required.")
            return redirect("core:create_event")

        # Create and save the event
        Event.objects.create(
            title=title,
            description=description,
            category=category,
            other_category=other_category,
            start_date=start_date,
            end_date=end_date,
            venue=venue,
            venue_address=venue_address,
            contact_number=contact_number,
            social_media=social_media,
            max_attendees=max_attendees,
            price=price,
            event_pdf=event_pdf,
            event_image=event_image,
            organizer=organizer
        )

        messages.success(request, "Your event has been created successfully.")
        return redirect("core:Home")

    return render(request, "create_event.html")

def delete(request, id):
    event = get_object_or_404(Event, id=id)
    event.delete()
    messages.success(request, "Event deleted successfully.")
    return redirect('core:Home')


def details(request, id):
    event = get_object_or_404(Event, id=id)
    return render(request, 'details.html', {"event": event})
