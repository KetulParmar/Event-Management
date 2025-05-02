from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from accounts.models import user_Data
from .models import *
from razorpay.errors import BadRequestError
from core.models import Ticket
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import razorpay
from .models import Event, Payment
from .utils.pdf_generator import generate_invoice_pdf
from django.core.mail import EmailMessage, send_mail
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone
from django.db.models.functions import TruncMonth
import json
from rest_framework import viewsets
from .models import Event
from .serializers import EventSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


#Email sending
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

Your ticket has been confirmed. Please find your ticket invoice attached.

Thanks,
Event Management Team
"""
    context = {

        "name": user.Name,
        "email": user.Email,
        "event": event.title,
        "venue": event.venue,
        "transaction_id": ticket.id,
        "price": event.price,
        "amount": event.price * ticket.quantity,
        "quantity": ticket.quantity,
        "start_date": event.start_date,
        "end_date": event.end_date,
        "start_time": event.start_time,
        "end_time": event.end_time,
    }

    pdf_file = generate_invoice_pdf(context)
    if not pdf_file:
        return False

    email = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.Email]
    )
    email.attach(f"Ticket_{ticket.id}.pdf", pdf_file.getvalue(), "application/pdf")
    email.send()




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
    else:
        user = None
        events = []
    return render(request, 'home.html', {'events': events})


#Event creation view
def create_event(request):
    if request.method == "POST":
        organizer_username = request.POST.get("organizer", "").strip()

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
        event_pdf = request.FILES.get("event_pdf")
        event_image = request.FILES.get("event_image")

        if not title or not start_date or not end_date or not venue:
            messages.error(request, "Title, start date, end date, and venue are required.")
            return redirect("core:create_event")

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

#Delete Event
def delete(request, id):
    event = get_object_or_404(Event, id=id)
    event.delete()
    messages.success(request, "Event deleted successfully.")
    return redirect('core:Home')

#Event details
@login_required
def details(request, id):
    event = get_object_or_404(Event, id=id)
    seat = event.max_attendees - event.seat_booked
    print(request.user, "2")
    return render(request, 'details.html', {"event": event, "seat":seat})

#Ticket booking
def ticket1(request, id):
    event = get_object_or_404(Event, id=id)
    razorpay_key = settings.RAZORPAY_KEY_ID
    return render(request,'Ticket.html', {"event": event, 'razorpay_key': razorpay_key})


@csrf_exempt
def create_order(request, event_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print(data)
            quantity = int(data.get("quantity", 1))
            if quantity <= 0:
                return JsonResponse({"error": "Invalid quantity"}, status=400)
            event = get_object_or_404(Event, id=event_id)
            user = request.user
            print(user)
            if not user.is_authenticated:
                return JsonResponse({"error": "User not authenticated"}, status=401)
            if event.seat_booked + quantity > event.max_attendees:
                return JsonResponse({"error": "Not enough seats available"}, status=400)
            total_amount = int(event.price * quantity * 100)
            print(settings.RAZORPAY_KEY_ID, " ", settings.RAZORPAY_SECRET_KEY)
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
            print(client)
            print("10")
            order_data = {
                        "amount": total_amount,
                        "currency": "INR",
                        "payment_capture": "1"
                    }
            try:
                print("here")
                order = client.order.create(order_data)
                print("order:", order)
            except Exception as e:
                print("razorpay error: ", e)
                return JsonResponse({"error": "Razorpay order creation failed", "details": str(e)}, status=500)
            print("11")
            payment = Payment.objects.create(
                user=user,
                event=event,
                amount=event.price * quantity,
                quantity=quantity,
                razorpay_order_id=order["id"],
                status="pending"
            )
            print("12")
            return JsonResponse({
                "order_id": order["id"],
                "amount": total_amount,
                "currency": "INR",
                "status": "created"
            })

        except Exception as e:
            print("13")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        data = json.loads(request.body)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
        try:
            params_dict = {
                'razorpay_order_id': data.get("razorpay_order_id"),
                'razorpay_payment_id': data.get("razorpay_payment_id"),
                'razorpay_signature': data.get("razorpay_signature")
            }

            client.utility.verify_payment_signature(params_dict)

            try:
                payment = Payment.objects.get(razorpay_order_id=params_dict["razorpay_order_id"])
            except Payment.DoesNotExist:
                return JsonResponse({"status": "failed", "message": "Payment record not found!"})

            event = payment.event
            if event.seat_booked + payment.quantity > event.max_attendees:
                return JsonResponse({"status": "failed", "message": "Not enough seats available!"})

            payment.razorpay_payment_id = params_dict["razorpay_payment_id"]
            payment.razorpay_signature = params_dict["razorpay_signature"]
            payment.status = "completed"
            payment.save()

            event.seat_booked += payment.quantity
            event.save()

            try:
                ticket = Ticket.objects.create(
                    user=payment.user,
                    event=event,
                    quantity=payment.quantity,
                    booking_date=timezone.now(),
                    status="booked"
                )
                send_ticket_email(payment.user, ticket, event)
            except Exception as e:
                return JsonResponse({"status": "failed", "message": f"Ticket creation failed: {str(e)}"})

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


@login_required
def organizer_dashboard(request):
    user = request.user
    my_events = Event.objects.filter(organizer=user)
    total_organized_events = my_events.count()

    # Total Tickets Sold
    tickets_sold = Ticket.objects.filter(
        event__organizer=user,
        status__in=['booked', 'used']
    ).aggregate(total=Sum('quantity'))['total'] or 0

    # Total Revenue
    total_revenue = Payment.objects.filter(
        event__organizer=user,
        status="completed"
    ).aggregate(total=Sum("amount"))["total"] or 0

    # Upcoming Events
    upcoming_events = my_events.filter(start_date__gte=timezone.now().date()).count()

    # Event Data for Table
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

    # Revenue Per Month Chart
    monthly_revenue_data = Payment.objects.filter(
        event__organizer=user,
        status="completed"
    ).annotate(month=TruncMonth('created_at')).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')

    revenue_months = [entry['month'].strftime("%b %Y") for entry in monthly_revenue_data]
    revenue_values = [entry['total'] for entry in monthly_revenue_data]

    # Tickets Sold Per Month Chart
    monthly_tickets = Ticket.objects.filter(
        event__organizer=user,
        status__in=['booked', 'used']
    ).annotate(month=TruncMonth('booking_date')).values('month').annotate(
        total=Sum('quantity')
    ).order_by('month')

    ticket_months = [entry['month'].strftime('%b') for entry in monthly_tickets]
    ticket_counts = [entry['total'] for entry in monthly_tickets]

    # Ticket Status Count for Pie Chart
    status_counts = Ticket.objects.filter(event__organizer=user).values('status').annotate(
        count=Sum('quantity')
    )

    ticket_status_map = {'booked': 0, 'cancelled': 0, 'used': 0}
    for entry in status_counts:
        status = entry['status']
        count = entry['count'] or 0
        if status in ticket_status_map:
            ticket_status_map[status] = count

    ticket_status_counts = list(ticket_status_map.values())

    # Recent Payments
    recent_payments = Payment.objects.filter(
        event__organizer=user
    ).select_related('event', 'user').order_by('-created_at')[:10]

    context = {
        "total_organized_events": total_organized_events,
        "tickets_sold": tickets_sold,
        "total_revenue": total_revenue,
        "upcoming_events": upcoming_events,
        "my_events": event_data,
        "recent_payments": recent_payments,

        # Chart Data
        "revenue_months": json.dumps(revenue_months),
        "revenue_values": json.dumps([float(val) for val in revenue_values]),
        "ticket_months": json.dumps(ticket_months),
        "ticket_counts": json.dumps([float(val) for val in ticket_counts]),
        "ticket_status_counts": json.dumps(ticket_status_counts),
    }

    return render(request, "organizer_dashboard.html", context)

@login_required
def my_ticket(request):
    user = request.user
    tickets = Ticket.objects.filter(user=user, status='booked').select_related('event')

    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        ticket = get_object_or_404(Ticket, id=ticket_id, user=user)
        ticket.status = 'cancelled'
        ticket.save()
        messages.success(request, 'Your ticket has been cancelled successfully.')

        # Send cancellation email
        subject = 'Event Ticket Cancellation Confirmation'
        message = f'''
Dear {user.Name},

Your ticket for the event **{ticket.event.title}** scheduled on {ticket.event.start_date} at {ticket.event.venue} has been successfully cancelled.
Money will be refunded within 3 working days.

If you have any questions, feel free to contact us.

Thank you,  
EventHere Team
        '''
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.Email],
            fail_silently=False,
        )

        return redirect('core:my_ticket')

    return render(request, 'my_ticket.html', {'tickets': tickets})

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]