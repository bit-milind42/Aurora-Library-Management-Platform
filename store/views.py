from django.shortcuts import render, redirect
from .models import Book, Issue, Fine
from student.models import Student
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.utils import timezone
import datetime
from .utilities import calcFine, getmybooks
from django.contrib.auth.models import User

from library import settings


# Book
def allbooks(request):
    requestedbooks, issuedbooks = getmybooks(request.user)
    allbooks = Book.objects.all()

    return render(request, 'library/home.html',
                  {'books': allbooks, 'issuedbooks': issuedbooks, 'requestedbooks': requestedbooks})

def filter_books_by_category(request, category):
    books = Book.objects.name(category__name=category)
    context = {
        'books': books,
        'selected_category': category
    }
    return render(request, 'libray/home.html', context)


@login_required(login_url='/student/login/')
@user_passes_test(lambda u: u.is_superuser, login_url='/student/login/')
def addbook(request):
    authors = Author.objects.all()
    if request.method == "POST":
        name = request.POST['name']
        category = request.POST['category']
        author = Author.objects.get(id=request.POST['author'])
        image = request.FILES['book-image']
        if author is not None or author != '':
            newbook, created = Book.objects.get_or_create(name=name, image=image, category=category, author=author)
            messages.success(request, 'Book - {} Added succesfully '.format(newbook.name))
            return render(request, 'library/addbook.html', {'authors': authors, })
        else:
            messages.error(request, 'Author not found !')
            return render(request, 'library/addbook.html', {'authors': authors, })
    else:
        return render(request, 'library/addbook.html', {'authors': authors})


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
