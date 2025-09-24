from django.db import models
from student.models import Student
import datetime
from django.utils import timezone
from rest_framework import serializers
# from .models import CustomUser
from django.contrib.auth.models import AbstractUser,Group, Permission


class Category(models.Model):
    name = models.CharField(max_length=50)

    #
    def __str__(self):
        return self.name

class Book(models.Model):
    name = models.CharField(max_length=350)
    author = models.ForeignKey('Author', on_delete=models.PROTECT, null=True, blank=True)
    image = models.ImageField(upload_to='books/', blank=True, null=True)
    category =  models.ForeignKey(Category, on_delete=models.CASCADE)


    def __str__(self):
        return self.name


class Issue(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    issued = models.BooleanField(default=False)
    issued_at = models.DateTimeField(auto_now=False, null=True, blank=True)
    returned = models.BooleanField(default=False)
    return_date = models.DateTimeField(auto_now=False, auto_created=False, auto_now_add=False, null=True, blank=True)

    def __str__(self):
        return "{}_{} book issue request".format(self.student, self.book)

    def days_no(self):
        "Returns the no. of days before returning / after return_date."
        if self.issued:
            y, m, d = str(timezone.now().date()).split('-')
            today = datetime.date(int(y), int(m), int(d))
            y2, m2, d2 = str(self.return_date.date()).split('-')
            lastdate = datetime.date(int(y2), int(m2), int(d2))
            print(lastdate - today, lastdate > today)
            if lastdate > today:
                return "{} left".format(str(lastdate - today).split(',')[0])
            else:
                return "{} passed".format(str(today - lastdate).split(',')[0])
        else:
            return ""

    @property
    def status(self):
        if self.returned:
            return 'returned'
        if self.issued:
            return 'issued'
        return 'requested'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'book'], condition=models.Q(returned=False), name='unique_active_issue')
        ]


class Fine(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    amount = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    order_id = models.CharField(unique=True, max_length=500, null=True, blank=True, default=None)
    datetime_of_payment = models.DateTimeField(auto_now=False, null=True, blank=True)

    # related to razorpay
    razorpay_order_id = models.CharField(max_length=500, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=500, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=500, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id is None:
            self.order_id = "{}_{}_{}".format(self.student.department, self.student.student_id.username,
                                              timezone.now().strftime('%H%M%S'))
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{} fine->{}".format(self.issue, self.amount)


# class CustomUser(AbstractUser):
#     # Add custom user fields if needed
#     pass
class CustomUser(AbstractUser):
    # Your custom fields and logic here

    # Add related_name to groups and user_permissions
    groups = models.ManyToManyField(
        Group,
        verbose_name=('groups'),
        blank=True,
        related_name='custom_user_set'  # You can use any name you prefer
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=('user permissions'),
        blank=True,
        related_name='custom_user_set_permissions'  # You can use any name you prefer
    )


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class Author(models.Model):
    name = models.CharField(max_length=120, unique=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name




