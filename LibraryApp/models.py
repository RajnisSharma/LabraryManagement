from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# Create your models here.
class Course(models.Model):
    course_name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['course_name']
        verbose_name_plural = 'Courses'

    def __str__(self):
        return f'{self.course_name}'

class Books(models.Model):
    book_name = models.CharField(max_length=100, null=False, blank=False)
    author_name = models.CharField(max_length=100, null=False, blank=False)
    course_name = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='books')
    total_copies = models.IntegerField(default=5, validators=[MinValueValidator(1)])
    available_copies = models.IntegerField(default=5, validators=[MinValueValidator(0)])
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['book_name']
        unique_together = ['book_name', 'author_name']

    def __str__(self):
        return f'{self.book_name} - {self.author_name} ({self.available_copies}/{self.total_copies})'

class Student(models.Model):
    SEMESTER_CHOICES = [(i, f'Semester {i}') for i in range(1, 9)]
    
    stud_name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    stud_email = models.EmailField(unique=True, null=True, blank=True)
    stud_password = models.CharField(max_length=255, default="1234")
    stud_phno = models.CharField(max_length=20, null=True, blank=True, unique=True)
    stud_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='students')
    stud_semester = models.IntegerField(choices=SEMESTER_CHOICES, default=1)
    stud_image = models.ImageField(upload_to='stud_profile/', default='stud_profile/default.png', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['stud_name']

    def __str__(self):
        return f'{self.stud_name} ({self.stud_course.course_name})'

class IssueBook(models.Model):
    STATUS_CHOICES = [
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue')
    ]
    
    stud_name = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='issued_books')
    book_name = models.ForeignKey(Books, on_delete=models.CASCADE, related_name='issues')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='issued')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = 'Issue Books'

    def __str__(self):
        return f'{self.stud_name.stud_name} - {self.book_name.book_name}'

    def is_overdue(self):
        if self.status == 'issued' and timezone.now().date() > self.end_date:
            return True
        return False

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    profile_image = models.ImageField(upload_to='admin_profile/', default='admin_profile/default.png', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True, default='Library Administration')
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Admin Profiles'

    def __str__(self):
        return f'{self.user.username} - Admin Profile'