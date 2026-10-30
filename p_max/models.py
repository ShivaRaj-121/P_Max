from django.db import models

class User(models.Model):
    username=models.CharField(max_length=200,unique=True)
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=200)

    def __str__(self):
        return self.username
    
class Movie(models.Model):
    name=models.CharField(max_length=200)
    language=models.CharField(max_length=200)
    duration=models.PositiveBigIntegerField()
    image=models.ImageField(upload_to="movie/")
    hero=models.CharField(max_length=200, default="Unknown")
    heroine=models.CharField(max_length=200, default="Unknown")

    
    def __str__(self):
        return self.name

class Theater(models.Model):
    name=models.CharField(max_length=200)
    location=models.CharField(max_length=200)

    
    def __str__(self):
        return self.name
    

class Show(models.Model):
    movie=models.ForeignKey(Movie,on_delete=models.CASCADE)
    theater=models.ForeignKey(Theater,on_delete=models.CASCADE)
    show_time=models.TimeField()
    price=models.DecimalField(max_digits=10,decimal_places=2)
    avilable_seats=models.IntegerField()

    def __str__(self):
        return f"{self.movie.name} -- {self.theater.name}"
    

class Review(models.Model):
    movie=models.ForeignKey(Movie,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    comment=models.TextField()
    rating=models.IntegerField()
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    

class Booking(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    show=models.ForeignKey(Show,on_delete=models.CASCADE)
    seats=models.CharField(max_length=100)
    total_price=models.DecimalField(max_digits=10,decimal_places=2)
    booking_time=models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'{self.user.username} booked'










