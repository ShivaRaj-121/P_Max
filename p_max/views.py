from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from p_max.models import *
import qrcode
import base64
from io import BytesIO
import logging
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from email.mime.image import MIMEImage

logger = logging.getLogger(__name__)

@never_cache
def home(request):
    movies = Movie.objects.all()
    return render(request,'./p_max/home.html',{'movies':movies})


def signUp(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request,'./p_max/signup.html',{
                "error":"Username already exists"
            })

        User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )

        return redirect("login")

    return render(request,"./p_max/signup.html")


def login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = User.objects.filter(username=username).first()
        valid = False
        if user and password:
            if check_password(password, user.password):
                valid = True
            elif user.password == password:  # legacy plaintext row: upgrade to hash
                user.password = make_password(password)
                user.save(update_fields=["password"])
                valid = True

        if valid:
            request.session.cycle_key()
            request.session["user-id"] = user.id
            request.session["user-name"] = user.username
            return redirect("dashboard")

        return render(request,"./p_max/login.html",{"error":"Invalid Credentials"})

    return render(request,"./p_max/login.html")


@never_cache
def dashboard(request):

    user_id = request.session.get("user-id")

    if not user_id:
        return redirect('login')

    movies = Movie.objects.all()

    return render(request,"./p_max/dashboard.html",{"movies":movies})


def logout(request):
    request.session.flush()
    return redirect('login')


from django.shortcuts import render, redirect, get_object_or_404

def movie_detail(request, movie_id):

    user_id = request.session.get('user-id')

    if not user_id:
        return redirect('login')

    movie = get_object_or_404(Movie, id=movie_id)

    # 👇 Fetch only this movie's shows
    shows = Show.objects.filter(movie=movie)

    reviews = Review.objects.filter(movie=movie)

    if request.method == 'POST':
        comment = request.POST.get('comment')
        rating = request.POST.get('rating')

        user = User.objects.get(id=user_id)

        Review.objects.create(
            movie=movie,
            user=user,
            comment=comment,
            rating=rating
        )

        return redirect(f'/movie_detail/{movie_id}')

    return render(request, "./p_max/movie_detail.html", {
        'movie': movie,
        'shows': shows,
        'reviews': reviews
    })


def book_show(request, show_id):

    user_id = request.session.get('user-id')

    if not user_id:
        return redirect('login')

    show = get_object_or_404(Show, id=show_id)

    rows = ['A','B','C','D','E','F','G','H','I','J','K']
    seats = []
    seats_per_row = 10

    for row in rows:
        for num in range(1, seats_per_row + 1):
            seats.append(row + str(num))

    bookings = Booking.objects.filter(show=show)

    booked_seats = []
    for b in bookings:
        booked_seats.extend(b.seats.split(','))

    if request.method == "POST":

        selected_seat = request.POST.get('selected_seats')

        if not selected_seat:
            return render(request,'./p_max/seat_selection.html',{
                'show': show,
                'booked_seats': booked_seats,
                'seats': seats,
                'error': 'Please select at least one seat'
            })

        seat_list = selected_seat.split(',')

        # ✔ correct price calculation
        seat_count = len(seat_list)
        total_price = seat_count * show.price

        user = User.objects.get(id=user_id)

        with transaction.atomic():
            show = Show.objects.select_for_update().get(id=show_id)
            taken = set()
            for b in Booking.objects.filter(show=show):
                taken.update(b.seats.split(','))
            valid = set(seats)
            if (len(set(seat_list)) != seat_count or not set(seat_list) <= valid
                    or taken & set(seat_list) or show.avilable_seats < seat_count):
                return render(request,'./p_max/seat_selection.html',{
                    'show': show,
                    'booked_seats': list(taken),
                    'seats': seats,
                    'error': 'Some seats are invalid or already booked'
                })
            booking = Booking.objects.create(
                user=user, show=show, seats=selected_seat, total_price=total_price
            )
            show.avilable_seats -= seat_count
            show.save(update_fields=["avilable_seats"])

        send_ticket_email(user, show, booking)

        return render(request,'./p_max/success.html',{
            'show': show,
            'seats': selected_seat,
            'total_price': total_price
        })

    return render(request,'./p_max/seat_selection.html',{
        'show': show,
        'booked_seats': booked_seats,
        'seats': seats
    })

def send_ticket_email(user, show, booking):
    seats = booking.seats
    total_price = booking.total_price
    qr_data = (f"Movie: {show.movie.name}\nTheatre: {show.theater.name}\n"
               f"Show Time: {show.show_time}\nSeats: {seats}\n"
               f"Total Price: Rs{total_price}\nUser: {user.username}")

    qr = qrcode.make(qr_data)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    subject = "Movie Ticket Confirmation"

    body = f"""
<html>
<body style="font-family:Arial;background:#0b0b0b;padding:30px;color:white;">

<div style="border:1px solid green;max-width:700px;margin:auto;background:#111;border-radius:12px;padding:20px">

<h2 style="color:#00ff9d;text-align:center;">🎬 P MAX MOVIE TICKET</h2>

<table style="width:100%;margin-top:20px;">

<tr>

<td style="width:40%;text-align:center;">
<img src="cid:qrcode" width="200">
<p style="color:#aaa;font-size:12px;">Scan at theatre entry</p>
</td>

<td style="width:60%;padding-left:20px;">

<p>Hello <b>{user.username}</b></p>

<p>Your ticket has been successfully booked.</p>

<p><b>Movie:</b> {show.movie.name}</p>
<p><b>Theatre:</b> {show.theater.name}</p>
<p><b>Show Time:</b> {show.show_time}</p>
<p><b>Seats:</b> {seats}</p>
<p><b>Total Price:</b> ₹{total_price}</p>

</td>

</tr>

</table>

</div>

</body>
</html>
"""

    msg = EmailMultiAlternatives(subject, f"Your tickets: {seats}", settings.DEFAULT_FROM_EMAIL, [user.email])
    msg.attach_alternative(body, "text/html")
    msg.mixed_subtype = "related"
    img = MIMEImage(buffer.getvalue())
    img.add_header('Content-ID', '<qrcode>')
    msg.attach(img)

    try:
        msg.send()
    except Exception:
        logger.exception("Ticket email failed for booking %s", booking.pk)
