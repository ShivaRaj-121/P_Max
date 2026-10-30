# P MAX – Movie Ticket Booking (Django)

Browse movies, pick seats, book tickets and receive an emailed QR-code ticket.

**Stack:** Django 5.2, MySQL, Bootstrap templates, Pillow, qrcode, Gunicorn + WhiteNoise.

## Features
- Sign up / login (hashed passwords), session-based auth
- Movie listing and detail pages with reviews and ratings
- Seat selection with transactional, double-booking-safe checkout
- Email ticket confirmation with embedded QR code
- Django admin for movies, theaters, shows, bookings

## Setup
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # then export the variables (or use your shell/IDE env)
mysql -e "CREATE DATABASE pmax_db CHARACTER SET utf8mb4;"
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Add movies, theaters and shows via `/admin/`.

## Email
Set `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`, `EMAIL_HOST_USER` and a Gmail **app password** in `EMAIL_HOST_PASSWORD`. By default emails print to the console.

## Tests
```bash
python manage.py test
```

## Deployment
`python manage.py collectstatic --noinput` then `gunicorn movie_project.wsgi` (see `Procfile`). Set `DJANGO_DEBUG=False`, a strong `DJANGO_SECRET_KEY`, and `DJANGO_ALLOWED_HOSTS`.
