from django.shortcuts import render, redirect
from .models import Book, Issue, Fine, Author, Category
from student.models import Student
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.utils import timezone
import datetime
from .utilities import calcFine, getmybooks
from django.contrib.auth import get_user_model

from library import settings

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from .serializers import CustomUserSerializer
from .models import CustomUser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets, permissions
from .serializers import CategorySerializer, AuthorSerializer, BookSerializer, IssueSerializer, FineSerializer

@login_required(login_url='/student/login/')
def dashboard(request):
    print(f'[DASHBOARD] User: {request.user}, Authenticated: {request.user.is_authenticated}')
    # Basic stats for the logged in user
    recent_issues = Issue.objects.filter(student__student_id=request.user).order_by('-issue_date')[:5]
    active_issues_count = Issue.objects.filter(student__student_id=request.user, issued=True, returned=False).count()
    fines_due = Fine.objects.filter(student__student_id=request.user, paid=False).count()
    total_books = Book.objects.count()
    return render(request, 'dashboard.html', {
        'recent_issues': recent_issues,
        'active_issues_count': active_issues_count,
        'fines_due': fines_due,
        'total_books': total_books,
    })

# Book
def allbooks(request):
    requestedbooks, issuedbooks = getmybooks(request.user)
    allbooks = Book.objects.all()

    return render(request, 'library/home.html',
                  {'books': allbooks, 'issuedbooks': issuedbooks, 'requestedbooks': requestedbooks})

def filter_books_by_category(request, category):
    books = Book.objects.filter(category__name=category)
    return render(request, 'library/home.html', {
        'books': books,
        'selected_category': category
    })


@login_required(login_url='/student/login/')
@user_passes_test(lambda u: u.is_superuser, login_url='/student/login/')
def addbook(request):
    authors = Author.objects.all()
    categories = Category.objects.all()
    if request.method == "POST":
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        author_id = request.POST.get('author')
        image = request.FILES.get('book-image')
        try:
            author = Author.objects.get(id=author_id) if author_id else None
        except Author.DoesNotExist:
            author = None
        try:
            category = Category.objects.get(id=category_id) if category_id else None
        except Category.DoesNotExist:
            category = None
        if not name or not category:
            messages.error(request, 'Name and category are required')
            return render(request, 'library/addbook.html', {'authors': authors, 'categories': categories})
        newbook, created = Book.objects.get_or_create(name=name, defaults={'image': image, 'category': category, 'author': author})
        if not created and image:
            newbook.image = image
            newbook.author = author
            newbook.category = category
            newbook.save()
        messages.success(request, f'Book - {newbook.name} added/updated successfully')
        return redirect('home')
    return render(request, 'library/addbook.html', {'authors': authors, 'categories': categories})


@login_required(login_url='/student/login/')
@user_passes_test(lambda u: u.is_superuser, login_url='/student/login/')
def deletebook(request, bookID):
    book = Book.objects.get(id=bookID)
    messages.success(request, 'Book - {} Deleted succesfully '.format(book.name))
    book.delete()
    return redirect('/')


#  ISSUES

@login_required(login_url='/student/login/')
@user_passes_test(lambda u: not u.is_superuser, login_url='/student/login/')
def issuerequest(request, bookID):
    student = Student.objects.filter(student_id=request.user)
    if student:
        book = Book.objects.get(id=bookID)
        issue, created = Issue.objects.get_or_create(book=book, student=student[0])
        messages.success(request, 'Book - {} Requested succesfully '.format(book.name))
        return redirect('home')

    messages.error(request, 'You are Not a Student !')
    return redirect('/')



@login_required(login_url='/student/login/')
@user_passes_test(lambda u: not u.is_superuser, login_url='/student/login/')
def myissues(request):
    if Student.objects.filter(student_id=request.user):
        student = Student.objects.filter(student_id=request.user)[0]

        if request.GET.get('issued') is not None:
            issues = Issue.objects.filter(student=student, issued=True)
        elif request.GET.get('notissued') is not None:
            issues = Issue.objects.filter(student=student, issued=False)
        else:
            issues = Issue.objects.filter(student=student)

        return render(request, 'library/myissues.html', {'issues': issues})

    messages.error(request, 'You are Not a Student !')
    return redirect('/')


@login_required(login_url='/admin/')
@user_passes_test(lambda u: u.is_superuser, login_url='/admin/')
def requestedissues(request):
    if request.GET.get('studentID') is not None and request.GET.get('studentID') != '':
        try:
            User = get_user_model()
            user = User.objects.get(username=request.GET.get('studentID'))
            student = Student.objects.filter(student_id=user)
            if student:
                student = student[0]
                issues = Issue.objects.filter(student=student, issued=False)
                return render(request, 'library/allissues.html', {'issues': issues})
            messages.error(request, 'No Student found')
            return redirect('/all-issues/')
        except User.DoesNotExist:
            messages.error(request, 'No Student found')
            return redirect('/all-issues/')

    else:
        issues = Issue.objects.filter(issued=False)
        return render(request, 'library/allissues.html', {'issues': issues})


@login_required(login_url='/admin/')
@user_passes_test(lambda u: u.is_superuser, login_url='/student/login/')
def issue_book(request, issueID):
    issue = Issue.objects.get(id=issueID)
    issue.return_date = timezone.now() + datetime.timedelta(days=15)
    issue.issued_at = timezone.now()
    issue.issued = True
    issue.save()
    return redirect('/all-issues/')


@login_required(login_url='/student/login/')
@user_passes_test(lambda u: u.is_superuser, login_url='/admin/')
def return_book(request, issueID):
    issue = Issue.objects.get(id=issueID)
    calcFine(issue)
    issue.returned = True
    issue.save()
    return redirect('/all-issues/')


#  FINES

@login_required(login_url='/student/login/')
@user_passes_test(lambda u: not u.is_superuser, login_url='/student/login/')
def myfines(request):
    if Student.objects.filter(student_id=request.user):
        student = Student.objects.filter(student_id=request.user)[0]
        issues = Issue.objects.filter(student=student)
        for issue in issues:
            calcFine(issue)
        fines = Fine.objects.filter(student=student)
        return render(request, 'library/myfines.html', {'fines': fines})
    messages.error(request, 'You are Not a Student !')
    return redirect('/')


@login_required(login_url='/student/login/')
@user_passes_test(lambda u: u.is_superuser, login_url='/admin/')
def allfines(request):
    issues = Issue.objects.all()
    for issue in issues:
        calcFine(issue)
    return redirect('/admin/library/fine/')


@login_required(login_url='/student/login/')
@user_passes_test(lambda u: u.is_superuser, login_url='/admin/')
def deletefine(request, fineID):
    fine = Fine.objects.get(id=fineID)
    fine.delete()
    return redirect('/all-fines/')


import razorpay

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required(login_url='/student/login/')
@user_passes_test(lambda u: not u.is_superuser, login_url='/student/login/')
def payfine(request, fineID):
    fine = Fine.objects.get(id=fineID)
    order_amount = int(fine.amount) * 100
    order_currency = 'INR'
    order_receipt = fine.order_id

    razorpay_order = razorpay_client.order.create(
        dict(amount=order_amount, currency=order_currency, receipt=order_receipt, ))
    print(razorpay_order)

    return render(request, 'library/payfine.html',

                  {'amount': order_amount, 'razor_id': settings.RAZORPAY_KEY_ID,
                   'reciept': razorpay_order['id'],
                   'amount_displayed': order_amount / 100,
                   'address': 'a custom address',
                   'fine': fine,
                   })


@login_required(login_url='/student/login/')
@user_passes_test(lambda u: not u.is_superuser, login_url='/student/login/')
def pay_status(request, fineID):
    if request.method == 'POST':
        params_dict = {
            'razorpay_payment_id': request.POST['razorpay_payment_id'],
            'razorpay_order_id': request.POST['razorpay_order_id'],
            'razorpay_signature': request.POST['razorpay_signature'],
        }
        try:
            status = razorpay_client.utility.verify_payment_signature(params_dict)
            if status is None:
                fine = Fine.objects.get(id=fineID)
                fine.paid = True
                fine.datetime_of_payment = timezone.now()
                fine.razorpay_payment_id = request.POST['razorpay_payment_id']
                fine.razorpay_signature = request.POST['razorpay_signature']
                fine.razorpay_order_id = request.POST['razorpay_order_id']
                fine.save()

            messages.success(request, 'Payment Succesfull')
        except:
            messages.error(request, 'Payment Failure')
    return redirect('/my-fines/')


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as exc:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        user = serializer.user
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response.data.update({
                'user_id': user.id,
                'username': user.username,
                'email': getattr(user, 'email', ''),
            })
        return response
    # Customize the response if needed


class CustomTokenRefreshView(TokenRefreshView):
    # Customize the response if needed
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            # Refresh token does not embed user object directly; could decode if needed.
            response.data['detail'] = 'Token refreshed'
        return response


class RegistrationView(generics.CreateAPIView):
    serializer_class = CustomUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def user_login(request):
    # Get username and password from the request data
    username = request.data.get('username')
    password = request.data.get('password')

    # Authenticate the user
    user = authenticate(username=username, password=password)

    # If authentication fails, return an error response
    if not user:
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    # If authentication is successful, generate a JWT token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    # Return the token in the response
    return Response({'access_token': access_token}, status=status.HTTP_200_OK)

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer

    def get_object(self):
        return self.request.user


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all().order_by('name')
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAdminUser]


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related('category', 'author').all().order_by('name')
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Issue.objects.select_related('book', 'student').all().order_by('-created_at')
        student = getattr(user, 'student', None)
        if student:
            return Issue.objects.filter(student=student).select_related('book').order_by('-created_at')
        return Issue.objects.none()


class FineViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FineSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Fine.objects.select_related('issue__book', 'student').all().order_by('-datetime_of_payment')
        student = getattr(user, 'student', None)
        if student:
            return Fine.objects.filter(student=student).select_related('issue__book').order_by('-datetime_of_payment')
        return Fine.objects.none()

