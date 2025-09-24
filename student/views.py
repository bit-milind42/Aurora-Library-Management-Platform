from django.shortcuts import render, redirect
from .models import Student, Department
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib import messages



def logout(request):
    username = request.user.first_name or request.user.username if request.user.is_authenticated else "User"
    auth.logout(request)
    messages.success(request, f'👋 Goodbye {username}! You have been logged out successfully. Come back soon!')
    return redirect('home')


def login(request):
    if request.method == 'POST':
        print('[LOGIN] Attempt for', request.POST.get('studentID'))
        user = auth.authenticate(request,
                                 username=request.POST['studentID'],
                                 password=request.POST['password'])
        print('[LOGIN] Auth result:', user)
        if user is None:
            messages.error(request, '❌ Invalid credentials. Please check your Student ID and password.')
            return render(request, 'student/login.html', {
                'last_student_id': request.POST.get('studentID'),
                'login_error': True
            })
        else:
            auth.login(request, user)
            print('[LOGIN] Session key after login:', request.session.session_key)
            print('[LOGIN] User authenticated:', request.user.is_authenticated)
            # Check if user is admin
            if user.is_superuser:
                messages.success(request, f'🔐 Welcome back, Administrator {user.username}!')
            else:
                messages.success(request, f'🎉 Welcome back, {user.first_name or user.username}! Happy reading!')
            
            if 'next' in request.POST:
                next_url = request.POST['next']
                print(f'[LOGIN] Redirecting to next: {next_url}')
                return redirect(next_url)
            print('[LOGIN] Redirecting to dashboard')
            return redirect('dashboard')
    else:
        return render(request, 'student/login.html')


def signup(request):
    print(f'[SIGNUP] Method: {request.method}')
    if request.method == 'POST':
        print(f'[SIGNUP] POST data: {dict(request.POST)}')
        try:
            User = get_user_model()
            user = User.objects.get(username=request.POST['studentID'])
            print(f'[SIGNUP] User already exists: {user.username}')
            messages.error(request, 'A user with this Student ID already exists. Please try logging in instead.')
            return redirect('student-login')

        except User.DoesNotExist:
            try:
                User = get_user_model()
                # Create user account
                user = User.objects.create_user(
                    username=request.POST['studentID'], 
                    password=request.POST['password'],
                    email=request.POST.get('emailID', ''),
                    first_name=request.POST.get('firstname', '').split()[0] if request.POST.get('firstname') else '',
                    last_name=' '.join(request.POST.get('firstname', '').split()[1:]) if len(request.POST.get('firstname', '').split()) > 1 else ''
                )

                # Create student profile
                # For now, we'll use a default department or create one if none exists
                try:
                    department = Department.objects.first()
                    if not department:
                        department = Department.objects.create(name="General")
                except:
                    department = Department.objects.create(name="General")

                newstudent = Student.objects.create(
                    first_name=request.POST['firstname'],
                    last_name='',  # We'll use the full name in first_name for now
                    department=department,
                    student_id=user
                )

                # Success message and redirect to login
                print(f'[SIGNUP] User created successfully: {user.username}')
                messages.success(request, f'🎉 Account created successfully! Welcome {request.POST["firstname"]}! Please log in with your credentials.')
                return redirect('student-login')

            except Exception as e:
                print(f'[SIGNUP] Error creating account: {str(e)}')
                messages.error(request, f'Error creating account: {str(e)}. Please try again.')
                return redirect('student-signup')

    else:
        User = get_user_model()
        return render(request, 'student/signup.html', {
            "departments": Department.objects.all(),
            "users": list(User.objects.values_list('username', flat=True))
        })

