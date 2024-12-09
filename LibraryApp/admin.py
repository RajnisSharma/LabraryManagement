from django.contrib import admin

from LibraryApp.models import Books, Course, Issue_book, Student

# Register your models here.
admin.site.register(Course)
admin.site.register(Books)
admin.site.register(Student)
admin.site.register(Issue_book)