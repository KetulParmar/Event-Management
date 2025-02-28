from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.models import user_Data
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from razorpay.errors import BadRequestError, ServerError

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

def Ticket(request, id):
    event = get_object_or_404(Event, id=id)
    return render(request,'Ticket.html', {"event": event})



# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

@login_required
@csrf_exempt
def create_order(request, event_id):
    print('yes')
    if request.method == "POST":
        print('no')
        try:
            data = json.loads(request.body)
            quantity = int(data.get("quantity", 1))
            print('1')
            if quantity <= 0:
                return JsonResponse({"error": "Invalid quantity"}, status=400)
            print('2')
            event = Event.objects.get(id=event_id)
            user = request.user
            print('3')
            print(user)
            # Ensure the user is authenticated
            if not user.is_authenticated:
                print('4')
                return JsonResponse({"error": "User not authenticated"}, status=401)
            print('5')
            total_amount = int(event.price * quantity * 100)  # Convert to paise
            print("Total Amount in paise:", total_amount)

            # Create Razorpay order
            order_data = {
                "amount": total_amount,
                "currency": "INR",
                "payment_capture": "1"
            }
            print("Order Data:", order_data)

            order = client.order.create(order_data)
            print("Created Order:", order)

            # Prevent duplicate orders
            if Payment.objects.filter(razorpay_order_id=order["id"]).exists():
                return JsonResponse({"error": "Duplicate order ID"}, status=400)

            # Save order in database
            payment = Payment.objects.create(
                user=user,
                event=event,
                amount=event.price * quantity,
                razorpay_order_id=order["id"],
                status="pending"
            )
            print("Saved payment:", payment)

            return JsonResponse({
                "order_id": order["id"],
                "amount": total_amount,
                "currency": "INR",
                "status": "created"
            })

        except Event.DoesNotExist:
            return JsonResponse({"error": "Event not found"}, status=404)
        except ValueError:
            return JsonResponse({"error": "Invalid quantity format"}, status=400)
        except Exception as e:
            print("Unexpected error:", e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"message": "Order endpoint is working!"})




@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        data = request.POST
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

        try:
            params_dict = {
                'razorpay_order_id': data.get("razorpay_order_id"),
                'razorpay_payment_id': data.get("razorpay_payment_id"),
                'razorpay_signature': data.get("razorpay_signature")
            }

            client.utility.verify_payment_signature(params_dict)

            # Update payment status
            payment = Payment.objects.get(razorpay_order_id=params_dict["razorpay_order_id"])
            payment.razorpay_payment_id = params_dict["razorpay_payment_id"]
            payment.razorpay_signature = params_dict["razorpay_signature"]
            payment.status = "completed"
            payment.save()

            return render(request, "payment_success.html", {"payment": payment})
        except razorpay.errors.SignatureVerificationError:
            return render(request, "payment_failed.html", {"error": "Signature verification failed"})
        except Payment.DoesNotExist:
            return render(request, "payment_failed.html", {"error": "Payment record not found"})
        except Exception as e:
            return render(request, "payment_failed.html", {"error": str(e)})

    return JsonResponse({"error": "Invalid request"}, status=400)
