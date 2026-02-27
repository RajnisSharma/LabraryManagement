from django.contrib import admin

from LibraryApp.models import Books, Course, IssueBook, Student, AdminProfile

# Register your models here.
admin.site.register(Course)
admin.site.register(Books)
admin.site.register(Student)
admin.site.register(IssueBook)
admin.site.register(AdminProfile)