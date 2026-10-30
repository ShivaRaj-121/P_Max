from django.test import TestCase
from django.urls import reverse
from p_max.models import User, Movie, Theater, Show, Booking


class BookingTests(TestCase):
    def setUp(self):
        self.client.post(reverse("signUp"), {"username": "u", "email": "u@x.com", "password": "pw12345!"})
        self.client.post(reverse("login"), {"username": "u", "password": "pw12345!"})
        m = Movie.objects.create(name="M", language="en", duration=100, image="movie/x.jpg")
        t = Theater.objects.create(name="T", location="L")
        self.show = Show.objects.create(movie=m, theater=t, show_time="10:00", price=100, avilable_seats=100)

    def test_password_is_hashed(self):
        self.assertNotEqual(User.objects.get(username="u").password, "pw12345!")

    def test_booking_and_double_booking_blocked(self):
        url = reverse("book_show", args=[self.show.id])
        self.assertEqual(self.client.post(url, {"selected_seats": "A1,A2"}).status_code, 200)
        self.assertEqual(Booking.objects.count(), 1)
        self.client.post(url, {"selected_seats": "A2"})
        self.assertEqual(Booking.objects.count(), 1)
        self.show.refresh_from_db()
        self.assertEqual(self.show.avilable_seats, 98)

    def test_dashboard_requires_login(self):
        self.client.logout()
        self.client.session.flush()
        self.assertEqual(self.client.get(reverse("logout")).status_code, 302)
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 302)
