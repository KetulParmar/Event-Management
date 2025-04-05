import razorpay
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from accounts.models import user_Data
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from razorpay.errors import BadRequestError
from core.models import Ticket
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.utils import timezone
from django.shortcuts import render


def home1(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = user_Data.objects.get(id=user_id)  # Fetch the user
            if user.User_type == 'organizer':  # Check if the user is an organizer
                events = Event.objects.filter(organizer=user)
            else:
                events = []
        except user_Data.DoesNotExist:
            user = None
            events = []
            print("User does not exist")

    else:
        user = None
        events = []
        print("No user logged in")

    return render(request, 'home.html', {'events': events})

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

@login_required
def details(request, id):
    event = get_object_or_404(Event, id=id)
    seat = event.max_attendees - event.seat_booked
    print(request.user, "2")
    return render(request, 'details.html', {"event": event, "seat":seat})

def ticket1(request, id):
    event = get_object_or_404(Event, id=id)

    return render(request,'Ticket.html', {"event": event})


# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

@csrf_exempt
def create_order(request, event_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            quantity = int(data.get("quantity", 1))
            if quantity <= 0:
                return JsonResponse({"error": "Invalid quantity"}, status=400)

            event = get_object_or_404(Event, id=event_id)
            user = request.user

            if not user.is_authenticated:
                return JsonResponse({"error": "User not authenticated"}, status=401)


            if event.seat_booked + quantity > event.max_attendees:
                return JsonResponse({"error": "Not enough seats available"}, status=400)

            total_amount = int(event.price * quantity * 100)  # Convert to paise

            # Create Razorpay order
            order_data = {
                "amount": total_amount,
                "currency": "INR",
                "payment_capture": "1"
            }

            order = client.order.create(order_data)

            # Save order details in Payment model
            payment = Payment.objects.create(
                user=user,
                event=event,
                amount=event.price * quantity,
                quantity=quantity,
                razorpay_order_id=order["id"],
                status="pending"
            )

            return JsonResponse({
                "order_id": order["id"],
                "amount": total_amount,
                "currency": "INR",
                "status": "created"
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        data = json.loads(request.body)

        try:
            params_dict = {
                'razorpay_order_id': data.get("razorpay_order_id"),
                'razorpay_payment_id': data.get("razorpay_payment_id"),
                'razorpay_signature': data.get("razorpay_signature")
            }

            client.utility.verify_payment_signature(params_dict)

            # Fetch payment record
            try:
                payment = Payment.objects.get(razorpay_order_id=params_dict["razorpay_order_id"])
            except Payment.DoesNotExist:
                return JsonResponse({"status": "failed", "message": "Payment record not found!"})

            # 🔹 Check if enough seats are available before finalizing payment
            event = payment.event
            if event.seat_booked + payment.quantity > event.max_attendees:
                return JsonResponse({"status": "failed", "message": "Not enough seats available!"})

            # Update payment status
            payment.razorpay_payment_id = params_dict["razorpay_payment_id"]
            payment.razorpay_signature = params_dict["razorpay_signature"]
            payment.status = "completed"
            payment.save()

            # 🔹 Update seat_booked count in the Event model
            event.seat_booked += payment.quantity
            event.save()

            # Create ticket after successful payment
            try:
                ticket = Ticket.objects.create(
                    user=payment.user,
                    event=event,
                    quantity=payment.quantity,
                    booking_date=timezone.now(),
                    status="booked"
                )
            except Exception as e:
                return JsonResponse({"status": "failed", "message": f"Ticket creation failed: {str(e)}"})

            # Redirect to success page
            redirect_url = reverse('core:payment_success_page', kwargs={'ticket_id': ticket.id})
            return JsonResponse({"status": "success", "redirect_url": redirect_url, "ticket_id": ticket.id})

        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({"status": "failed", "message": "Signature verification failed!"})
        except Exception as e:
            return JsonResponse({"status": "failed", "message": str(e)})

    return JsonResponse({"error": "Invalid request"}, status=400)



def payment_success_page(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, "payment_success_page.html", {"ticket": ticket})


def dashboard(request):
    return render(request, "dashboard.html")

@login_required
def organizer_dashboard(request):
    user = request.user  # Currently logged-in organizer

    # Fetch all events organized by the user
    my_events = Event.objects.filter(organizer=user)

    # Count of events organized
    total_organized_events = my_events.count()

    # Total tickets sold (booked or used) for organizer's events
    tickets_sold = Ticket.objects.filter(
        event__organizer=user,
        status__in=['booked', 'used']
    ).aggregate(total=Sum('quantity'))['total'] or 0

    # Total revenue from completed payments
    total_revenue = Payment.objects.filter(
        event__organizer=user,
        status="completed"
    ).aggregate(total=Sum("amount"))["total"] or 0

    # Count of upcoming events
    upcoming_events = my_events.filter(start_date__gte=timezone.now().date()).count()

    # Detailed data per event
    event_data = []
    for event in my_events:
        total_tickets = Ticket.objects.filter(
            event=event,
            status__in=['booked', 'used']
        ).aggregate(total=Sum('quantity'))['total'] or 0

        revenue = Payment.objects.filter(
            event=event,
            status="completed"
        ).aggregate(total=Sum("amount"))["total"] or 0

        event_data.append({
            "title": event.title,
            "start_date": event.start_date,
            "total_tickets": total_tickets,
            "revenue": revenue
        })

    context = {
        "total_organized_events": total_organized_events,
        "tickets_sold": tickets_sold,
        "total_revenue": total_revenue,
        "upcoming_events": upcoming_events,
        "my_events": event_data,
    }

    return render(request, "organizer_dashboard.html", context)

