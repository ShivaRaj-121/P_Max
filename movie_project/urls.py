
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from p_max.views import *


urlpatterns = [

    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('signup/', signUp, name='signUp'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('movie_detail/<int:movie_id>/', movie_detail, name='movie_detail'),
    path('book_show/<int:show_id>/', book_show, name='book_show'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)