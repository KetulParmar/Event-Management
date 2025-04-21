from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from accounts.models import user_Data
from .models import *
from razorpay.errors import BadRequestError
from core.models import Ticket
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
import razorpay
from .models import Event, Payment
#Email sending
from django.core.mail import send_mail

def send_ticket_email(user, ticket, event):
    subject = f"🎟️ Ticket Confirmation - {event.title}"
    message = f"""
Hi {user.Name},

Thank you for booking a ticket for {event.title}!

📅 Date: {event.start_date} to {event.end_date}
📍 Venue: {event.venue}
🎫 Quantity: {ticket.quantity}
📅 Booked On: {ticket.booking_date.strftime('%Y-%m-%d %H:%M')}
💳 Amount Paid: ₹{event.price * ticket.quantity}

Your ticket has been confirmed. Please show this email at the entry gate.

Thanks,
Event Management Team
"""
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.Email])




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
    razorpay_key = settings.RAZORPAY_KEY_ID
    print(razorpay_key)
    return render(request,'Ticket.html', {"event": event, 'razorpay_key': razorpay_key})



# ✅ Razorpay client initializer
def get_razorpay_client():
    return razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID or "rzp_test_BGAtdn9itwDCse",
        settings.RAZORPAY_SECRET_KEY or "AYZJSM8iDneOC7m66CfOyLFF"
    ))

@csrf_exempt
def create_order(request, event_id):
    if request.method == "POST":
        try:
            print("✅ Step 1: Parsing request data")
            data = json.loads(request.body)
            quantity = int(data.get("quantity", 1))
            if quantity <= 0:
                return JsonResponse({"error": "Invalid quantity"}, status=400)

            print("✅ Step 2: Fetching event and user")
            event = get_object_or_404(Event, id=event_id)
            user = request.user

            if not user.is_authenticated:
                return JsonResponse({"error": "User not authenticated"}, status=401)

            print("✅ Step 3: Seat availability check")
            if event.seat_booked + quantity > event.max_attendees:
                return JsonResponse({"error": "Not enough seats available"}, status=400)

            total_amount = int(event.price * quantity * 100)  # in paise
            print("✅ Step 4: Total amount calculated:", total_amount)

            print("✅ Step 5: Initializing Razorpay client")
            client = get_razorpay_client()

            print("🔐 Using Razorpay Keys -> KEY_ID:", settings.RAZORPAY_KEY_ID, "SECRET:", settings.RAZORPAY_SECRET_KEY)

            order_data = {
                "amount": total_amount,
                "currency": "INR",
                "payment_capture": "1"
            }

            print("✅ Step 6: Creating Razorpay order")
            try:
                order = client.order.create(order_data)
                print("✅ Razorpay order created:", order)
            except Exception as e:
                print("❌ Razorpay order creation failed:", str(e))
                return JsonResponse({"error": "Razorpay order creation failed", "details": str(e)}, status=500)

            print("✅ Step 7: Saving Payment record")
            payment = Payment.objects.create(
                user=user,
                event=event,
                amount=event.price * quantity,
                quantity=quantity,
                razorpay_order_id=order["id"],
                status="pending"
            )

            print("✅ Step 8: Returning JSON response to frontend")
            return JsonResponse({
                "order_id": order["id"],
                "amount": total_amount,
                "currency": "INR",
                "status": "created"
            })

        except Exception as e:
            print("❌ Unexpected error:", str(e))
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        data = json.loads(request.body)
        client = get_razorpay_client()
        try:
            params_dict = {
                'razorpay_order_id': data.get("razorpay_order_id"),
                'razorpay_payment_id': data.get("razorpay_payment_id"),
                'razorpay_signature': data.get("razorpay_signature")
            }
            print("1")
            client.utility.verify_payment_signature(params_dict)
            print("2")
            # Fetch payment record
            try:
                payment = Payment.objects.get(razorpay_order_id=params_dict["razorpay_order_id"])
            except Payment.DoesNotExist:
                return JsonResponse({"status": "failed", "message": "Payment record not found!"})
            print("3")
            # 🔹 Check if enough seats are available before finalizing payment
            event = payment.event
            if event.seat_booked + payment.quantity > event.max_attendees:
                return JsonResponse({"status": "failed", "message": "Not enough seats available!"})
            print("4")
            # Update payment status
            payment.razorpay_payment_id = params_dict["razorpay_payment_id"]
            payment.razorpay_signature = params_dict["razorpay_signature"]
            payment.status = "completed"
            payment.save()
            print("5")
            # 🔹 Update seat_booked count in the Event model
            event.seat_booked += payment.quantity
            event.save()
            print("6")
            # Create ticket after successful payment
            try:
                print("7")
                ticket = Ticket.objects.create(
                    user=payment.user,
                    event=event,
                    quantity=payment.quantity,
                    booking_date=timezone.now(),
                    status="booked"
                )
                print("8")
                send_ticket_email(payment.user, ticket, event)
                print("9")
            except Exception as e:
                print(e)
                return JsonResponse({"status": "failed", "message": f"Ticket creation failed: {str(e)}"})
            print("10")
            # Redirect to success page
            redirect_url = reverse('core:payment_success_page', kwargs={'ticket_id': ticket.id})
            return JsonResponse({"status": "success", "redirect_url": redirect_url, "ticket_id": ticket.id})

        except razorpay.errors.SignatureVerificationError:
            print("11")
            return JsonResponse({"status": "failed", "message": "Signature verification failed!"})
        except Exception as e:
            print("12")
            return JsonResponse({"status": "failed", "message": str(e)})

    return JsonResponse({"error": "Invalid request"}, status=400)



def payment_success_page(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, "payment_success_page.html", {"ticket": ticket})

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

