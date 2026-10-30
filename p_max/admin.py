from django.contrib import admin

from p_max.models import User,Movie,Theater,Show,Review,Booking

admin.site.register(User)
admin.site.register(Movie)
admin.site.register(Theater)
admin.site.register(Show)
admin.site.register(Review)
admin.site.register(Booking) 