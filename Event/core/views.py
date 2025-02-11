from django.http import HttpResponse
from django.shortcuts import render, redirect,  get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import Event
import os
from accounts.models import user_Data

def home1(request):
    data = Event.objects.all()
    return render(request, 'home.html',{'events':data})

def create_event(request):
    if request.method == "POST":
        """username1 = request.POST.get("username", "").strip()
        print(f"Searching for username: {username1}")
        try:
            us = user_Data.objects.get(username=username1)
        except user_Data.DoesNotExist:
            return HttpResponse("User does not exist", status=404)
        if us is None and username1 != us.username :
            return render(request,'create_event.html',{'err':'Username is incorrect'})"""
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        category = request.POST.get("category", "").strip()
        other_category = request.POST.get("category", "").strip()
        start_date = request.POST.get("start_date", "").strip()
        end_date = request.POST.get("end_date", "").strip()
        venue = request.POST.get("venue", "").strip()
        venue_address = request.POST.get("venue_address", "").strip()
        contact_number = request.POST.get("contact_number", "").strip()
        social_media = request.POST.get("social_media", "").strip()
        max_attendees = request.POST.get("max_attendees", "").strip()
        price = request.POST.get("price", "").strip()
        event_pdf = request.FILES.get("event_pdf")

        # Validate required fields
        if not title or not start_date or not end_date or not venue:
            messages.error(request, "Title, start date, end date, and venue are required.")
            return redirect("core:create_event")

        # Create Event object and save it to the database
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
            event_pdf=event_pdf
        )

        messages.success(request, "Your event has been created successfully.")
        return redirect("core:Home")

    return render(request, "create_event.html")

def delete(request, id):
    print(id)
    event = get_object_or_404(Event, id=id)  # Safely fetch event or return 404
    print(event.title)
    event.delete()
    return redirect('core:Home')  # Ensure 'home1' is a valid URL name