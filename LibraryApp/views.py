from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from LibraryApp.models import Books, Course, IssueBook, Student, AdminProfile
from django.views.decorators.cache import cache_control, never_cache
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from functools import wraps



# Create your views here.
def student_login_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if request.session.get('S_name'):
            return view_func(request, *args, **kwargs)
        messages.info(request, 'Please login to continue')
        return redirect('login')

    return _wrapped


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def Public_LMS(request):
    return render(request, 'public_lms.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def login_fun(request):
    if request.method == 'POST':
        userName = request.POST.get('userName')
        userPassword = request.POST.get('userPassword')
        admin_key = (request.POST.get('adminKey') or '').strip()
        user = authenticate(username=userName, password=userPassword)
        if user is not None:
            if user.is_superuser:
                if not settings.ADMIN_SECURITY_KEY:
                    messages.error(request, 'Admin security key is not configured')
                    return render(request, 'login.html', {'data': 'Admin security key is not configured'})
                if admin_key != settings.ADMIN_SECURITY_KEY:
                    messages.error(request, 'invalid admin security key')
                    return render(request, 'login.html', {'data': 'invalid admin security key'})
                request.session.pop('S_name', None)
                login(request, user)
                request.session['uid'] = request.POST.get('userName')
                return redirect('home')
            else:
                messages.success(request, 'invalid credentials')
                return render(request, 'login.html', {'data': 'invalid credentials'})
        elif Student.objects.filter(Q(stud_name=userName) & Q(stud_password=userPassword)).exists():
            if request.user.is_authenticated:
                logout(request)
            request.session['S_name'] = request.POST['userName']
            return redirect('studhome')
        else:
            messages.success(request, 'invalid credentials')
            return render(request, 'login.html', {'data': 'invalid credentials'})
    else:
        return render(request, 'login.html', {'data': ''})


# -------------------------------------------------------------------------------------------------------------
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def reg_fun(request):
    if request.method == 'POST':
        username = request.POST.get('txtUserName')
        password = request.POST.get('txtPswd')
        email = request.POST.get('txtEmail')
        admin_key = (request.POST.get('txtAdminKey') or '').strip()
        profile_image = request.FILES.get('txtProfileImage')

        if not settings.ADMIN_SECURITY_KEY:
            return render(request, 'register.html', {'data': 'Admin security key is not configured'})
        if admin_key != settings.ADMIN_SECURITY_KEY:
            return render(request, 'register.html', {'data': 'invalid admin security key'})

        if User.objects.filter(Q(username=username) | Q(email=email)).exists():
            return render(request, 'register.html', {'data': 'invalid credentials'})
        else:
            u1 = User.objects.create_superuser(username=username, password=password, email=email)
            u1.save()
            admin_profile, _created = AdminProfile.objects.get_or_create(user=u1)
            if profile_image:
                admin_profile.profile_image = profile_image
                admin_profile.save()
            messages.success(request, 'Admin/Staff account created successfully. Please login.')
            return redirect(f"{reverse('login')}?role=admin")
    else:
        return render(request, 'register.html', {'data': ''})


# -----------------------------------------------------------------------------------------------------
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def add_stud_fun(request):
    c1 = Course.objects.all() 

    if request.method == 'POST':
        s1 = Student()
        s1.stud_name = request.POST.get('txtName')
        s1.stud_course = Course.objects.get(course_name=request.POST['ddlCourse'])
        s1.stud_phno = request.POST.get('txtPhno')
        s1.stud_semester = request.POST.get('txtSem')
        s1.stud_password = request.POST.get('txtPswd')
        if 'txtfile' in request.FILES:
            s1.stud_image = request.FILES['txtfile']
        else:
            s1.stud_image = 'stud_profile/default.png'
        if Student.objects.filter(stud_name=s1.stud_name).exists():
            return render(request, 'student_template/add_student.html', {'course': c1, 'msg': 'Student already exists', 'res': False})
        s1.save()
        return render(request, 'student_template/add_student.html', {'course': c1, 'msg': 'Student added successfully', 'res': True})
    return render(request, 'student_template/add_student.html', {'course': c1})


# ------------------------------------------------------------------------------------------
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def home_fun(request):
    return render(request, 'books_template/home.html')

# ------------------------------------------------------------------------------------------
# Admin Profile Views
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def admin_profile_fun(request):
    admin_user = request.user
    # Get or create admin profile
    admin_profile, created = AdminProfile.objects.get_or_create(user=admin_user)
    return render(request, 'books_template/admin_profile.html', {'admin': admin_user, 'admin_profile': admin_profile})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def update_admin_fun(request):
    admin_user = request.user
    # Get or create admin profile
    admin_profile, created = AdminProfile.objects.get_or_create(user=admin_user)
    
    if request.method == 'POST':
        admin_user.first_name = request.POST.get('txtFirstName', '')
        admin_user.last_name = request.POST.get('txtLastName', '')
        admin_user.email = request.POST.get('txtEmail', '')
        
        # Update admin profile
        admin_profile.phone = request.POST.get('txtPhone', '')
        admin_profile.department = request.POST.get('txtDepartment', '')
        admin_profile.bio = request.POST.get('txtBio', '')
        
        # Handle profile image upload
        if 'txtProfileImage' in request.FILES:
            admin_profile.profile_image = request.FILES['txtProfileImage']
        
        # Check if password change is requested
        new_password = request.POST.get('txtNewPassword', '')
        if new_password:
            admin_user.set_password(new_password)
        
        admin_user.save()
        admin_profile.save()
        return redirect('admin_profile')
    
    return render(request, 'books_template/update_admin.html', {'admin': admin_user, 'admin_profile': admin_profile})

# -------------------------------------------------------------------------------------------
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def addbook_func(request):
    if request.method == 'POST':
        c1 = Course.objects.all()
        b1 = Books()
        b1.book_name = request.POST.get('txtBookName')
        b1.author_name = request.POST.get('txtAuthorName')
        b1.course_name = Course.objects.get(course_name=request.POST.get('ddlCourseName'))
        b1.save()
        return render(request, 'books_template/add_book.html', {'course': c1, 'msg': 'added successfully', 'res': True})
    else:
        c1 = Course.objects.all()
        return render(request, 'books_template/add_book.html', {'course': c1, 'msg': '', 'res': False})


# -------------------------------------------------------------------------------------------
@login_required
@cache_control(no_cache=True, must_revalidaste=True, no_store=True)
@never_cache
def displaybook_func(request):
    books = Books.objects.all()
    return render(request, 'books_template/display_book.html', {'books': books})


# --------------------------------------------------------------------------------------------
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def update_book_fun(request,id):
    book = Books.objects.get(id=id)
    c1 = Course.objects.all()
    if request.method == 'POST':
        book.book_name = request.POST.get('txtBookName')
        book.author_name = request.POST.get('txtAuthorName')
        book.course_name = Course.objects.get(course_name = request.POST.get('ddlCourseName'))
        book.save()
        return redirect('displaybook')
    return render(request,'books_template/update_book.html',{'books':book,'course':c1})

#---------------------------------------------------------------------------------------------
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def delete_book_fun(request, id):
    book = Books.objects.get(id=id)
    book.delete()
    return redirect('displaybook')

#-----------------------------------------------------------------------------------------------
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def get_Student_fun(request):
    if request.method == 'POST':
        ph = request.POST.get('txtPhno', '').strip()
        if not ph:
            books = Books.objects.all()
            return render(request, 'books_template/assign_book.html', {'Books': books, 'Stud': '', 'msg': 'Please provide a mobile number', 'res': False})
        try:
            s1 = Student.objects.get(stud_phno=ph)
            books = Books.objects.filter(course_name=s1.stud_course).all()
            return render(request, 'books_template/assign_book.html', {'Books': books, 'Stud': s1})
        except Student.DoesNotExist:
            books = Books.objects.all()
            return render(request, 'books_template/assign_book.html', {'Books': books, 'Stud': '', 'msg': 'Student not found', 'res': False})
    books = Books.objects.all()
    return render(request, 'books_template/assign_book.html', {'Books': books, 'Stud': '', 'msg': '', 'res': False})

#------------------------------------------------------------------------------------------------
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def assignbook_fun(request):
    if request.method == 'POST':
        name = request.POST.get('txtName', '').strip()
        book_name = request.POST.get('ddlBookName', '').strip()
        start = request.POST.get('txtStartDate', '').strip()
        end = request.POST.get('txtEndDate', '').strip()

        books = Books.objects.all()

        if not (name and book_name and start and end):
            return render(request, 'books_template/assign_book.html',
                          {'Books': books, 'Stud': '', 'msg': 'All fields are required to assign a book', 'res': False})

        try:
            student = Student.objects.get(stud_name=name)
        except Student.DoesNotExist:
            return render(request, 'books_template/assign_book.html',
                          {'Books': books, 'Stud': '', 'msg': 'Student not found', 'res': False})

        try:
            book = Books.objects.get(book_name=book_name)
        except Books.DoesNotExist:
            return render(request, 'books_template/assign_book.html',
                          {'Books': books, 'Stud': '', 'msg': 'Selected book not found', 'res': False})

        # Create issue record
        i1 = IssueBook()
        i1.stud_name = student
        i1.book_name = book
        i1.start_date = start
        i1.end_date = end
        i1.save()

        return render(request, 'books_template/assign_book.html',
                      {'Books': books, 'Stud': '', 'msg': 'assigned successfully', 'res': True})

    books = Books.objects.all()
    return render(request, 'books_template/assign_book.html',
                  {'Books': books, 'Stud': '', 'msg': '', 'res': False})

#-----------------------------------------------------------------------------------------------
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def display_assign_fun(request):
    i1 = IssueBook.objects.all()
    return render(request,'books_template/display_assign.html',{'issue_list':i1})


#-----------------------------------------------------------------------------------------------
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def delete_issue_fun(request,id):
    i1 = IssueBook.objects.get(id=id)
    i1.delete()
    return redirect('displayassign')

#-----------------------------------------------------------------------------------------------
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def updt_issue_fun(request,id):
    i1 = IssueBook.objects.get(id=id)
    s1 = Student.objects.get(id=i1.stud_name_id)
    books = Books.objects.filter(course_name=s1.stud_course)
    print(i1.start_date)
    if request.method == 'POST':
        # i1.stud_name = Student.objects.get(stud_name=request.POST['txtName'])
        i1.book_name = Books.objects.get(book_name=request.POST['ddlBookName'])
        i1.start_date = request.POST['txtStartDate']
        i1.end_date = request.POST['txtEndDate']
        i1.save()
        return redirect('displayassign')
    return render(request,'books_template/updt_issue.html',{'Issue':i1,'Stud':s1,'Book':books})


#-----------------------------------------------------------------------------------------------
# Student profile views code

@student_login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def stud_home_fun(request):
    return render(request,'student_template/stud_home.html',{'Name':request.session['S_name']})


@student_login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def stud_books_fun(request):
    s1 = Student.objects.get(stud_name=request.session['S_name'])
    i1 = IssueBook.objects.filter(stud_name=s1)
    return render(request,'student_template/stud_books.html',{'data':i1})


@student_login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def get_prof_fun(request):
    s1 = Student.objects.get(stud_name=request.session['S_name'])
    return render(request,'student_template/stud_profile.html',{'data':s1})


@student_login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def update_prof_fun(request,id):
    s1 = Student.objects.get(id=id)
    if request.method == 'POST':
        s1.stud_name = request.POST.get('txtName')
        s1.stud_phno = request.POST.get('txtPhno')
        s1.stud_semester = request.POST.get('txtSem')
        s1.stud_password = request.POST.get('txtPswd')
        file = request.FILES.get('txtfile')
        if file:
            s1.stud_image = file
        s1.save()
        return redirect('getprof')
    return render(request,'student_template/update_prof.html',{'data':s1})

#------------------------------------------------------------------------------------------------
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def log_out_fun(request):
    role = "admin" if request.user.is_staff else "student"
    logout(request)
    return redirect(f"{reverse('login')}?role={role}")

#------------------------------------------------------------------------------------------------
# Book Search Feature for Students
@student_login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def search_books_fun(request):
    search_results = []
    search_query = ''
    
    if request.method == 'POST':
        search_query = request.POST.get('search_query', '').strip()
        
        if search_query:
            # Search by book name or author name
            search_results = Books.objects.filter(
                Q(book_name__icontains=search_query) | 
                Q(author_name__icontains=search_query)
            ).distinct()
            
            # Add availability count for each book
            for book in search_results:
                # Count how many copies are issued
                issued_count = IssueBook.objects.filter(book_name=book).count()
                # You can assume 5 copies per book, adjust as needed
                book.available_copies = max(0, 5 - issued_count)
                book.total_copies = 5
                book.issued_count = issued_count
    
    return render(request, 'student_template/search_books.html', {
        'search_results': search_results,
        'search_query': search_query,
        'student_name': request.session.get('S_name', '')
    })
