from django.http import HttpResponse
from django.shortcuts import render, redirect,  get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import *
from accounts.models import user_Data


def home1(request):
    user_id = request.session.get('user_id')
    if user_id:
        user = user_Data.objects.get(id=user_id)
        print(user.username)  # ✅ Correct way to access user details
    else:
        print("User is not logged in.")

    data = Event.objects.filter(organizer_id=user_id)  # Get events created by this user
    return render(request, 'home.html', {'events': data})

def create_event(request):
    if request.method == "POST":
        print('1')
        # Get the organizer from the form input
        organizer1 = request.POST.get("organizer", "").strip()
        print('2')
        # Check if the organizer exists and matches the current logged-in user
        try:
            print('3')
            us = user_Data.objects.get(username=organizer1)  # Find user by username
        except user_Data.DoesNotExist:
            print('4')
            return HttpResponse("User does not exist", status=404)
        print(us.username)
        print('11')
        print('User authenticated:', request.user.is_authenticated)
        print(request.user.username)
        # Check if the organizer entered matches the logged-in user
        """if us.username != request.user.username:  # Compare organizer's username with logged-in user's username
            print('5')
            return render(request, "create_event.html", {"err": "You cannot create an event for someone else."})"""

        #Get the event data from the form
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        category = request.POST.get("category", "").strip()
        other_category = request.POST.get("other_category", "").strip()  # Fixed duplicate category field
        start_date = request.POST.get("start_date", "").strip()
        end_date = request.POST.get("end_date", "").strip()
        venue = request.POST.get("venue", "").strip()
        venue_address = request.POST.get("venue_address", "").strip()
        contact_number = request.POST.get("contact_number", "").strip()
        social_media = request.POST.get("social_media", "").strip()
        max_attendees = request.POST.get("max_attendees", "").strip()
        price = request.POST.get("price", "").strip()

        # Get uploaded files (PDF & Image)
        event_pdf = request.FILES.get("event_pdf")
        event_image = request.FILES.get("event_image")  # Added image field
        print('6')
        # Validate required fields
        if not title or not start_date or not end_date or not venue:
            print('7')
            messages.error(request, "Title, start date, end date, and venue are required.")
            return redirect("core:create_event")
        print('8')
        # Create and save the Event object
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
            max_attendees=max_attendees or None,
            price=price or None,
            event_pdf=event_pdf,
            event_image=event_image,  # Save image
            organizer=us  # Store the correct organizer
        )
        print('9')
        messages.success(request, "Your event has been created successfully.")
        return redirect("core:Home")

    return render(request, "create_event.html")

def delete(request, id):
    print(id)
    event = get_object_or_404(Event, id=id)  # Safely fetch event or return 404
    print(event.title)
    event.delete()
    return redirect('core:Home')  # Ensure 'home1' is a valid URL name

def details(request, id):
    event = get_object_or_404(Event, id=id)
    return render(request,'details.html', {"event": event})