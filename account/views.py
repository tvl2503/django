from store.models import Customer
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
import uuid
from django.views import View
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from orders.models import Payment
from account.forms import CustomerForm
from .helpers import send_forget_password_mail
# Create your views here.



class logoutMethod(View):
	def get(self, request):
		logout(request)
		return redirect("signin")

class loginMethod(View):
    def post(self, request):
            username1 = request.POST.get('username')
            password1 = request.POST.get('password')
            print(f"{username1} {password1}")
            try:
                user_obj = User.objects.filter(username = username1).first()
                if user_obj is None:
                    messages.success(request, 'User not found.')
                    return redirect('/account/signin')
                
                
                profile_obj = Customer.objects.filter(user = user_obj ).first()

                if not profile_obj.is_verified:
                    messages.success(request, 'Profile is not verified check your mail.')
                    return redirect('/account/signin')

                user = authenticate(username = username1 , password = password1)
                if user is None:
                    messages.warning(request, 'Wrong password!!.')
                    return redirect('/account/signin')
                login(request , user)
                return redirect('/')
            except Exception as e:
                print(e)

    def get(self, request):
    	return render(request, 'signin.html')

class registerMethod(View):

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')
        firstName = request.POST.get('firstName')
        lastName = request.POST.get('lastName')
        phone = request.POST.get('phone')
        
        try:
            
            if User.objects.filter(username = username).first():
                messages.success(request, 'Username is taken.')
                print("ten trung nhau")
                return redirect('/account/register')

            if User.objects.filter(email = email).first():
                messages.success(request, 'Email is taken.')
                print("email trung nhau")
                return redirect('/account/register')
            if confirmpassword != password:
                messages.success(request, 'The password does not match')
                return redirect('/account/register')
            print("OK")
            user_obj = User(username = username , email = email,first_name = firstName ,last_name =lastName)
            user_obj.set_password(password)
            user_obj.save()
            auth_token = str(uuid.uuid4())
            profile_obj = Customer.objects.create(user = user_obj, phone = phone, first_name = firstName ,last_name =lastName ,email = email, auth_token = auth_token)
            profile_obj.save()
            print("1")
            send_mail_after_registration(email , auth_token)
            print("143")
            return redirect('/account/token')

        except Exception as e:
            print(e)


    def get(self, request):
            return render(request, 'register.html')


# def success(request):
#     return render(request , 'success.html')


def token_send(request):
    return render(request , 'token_send.html')



def verify(request , auth_token):
    try:
        profile_obj = Customer.objects.filter(auth_token = auth_token).first()
    

        if profile_obj:
            if profile_obj.is_verified:
                messages.success(request, 'Your account is already verified.')
                return redirect('/account/sigin')
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, 'Your account has been verified.')
            return redirect('/account/signin')
        else:
            return redirect('/account/error')
    except Exception as e:
        print(e)
        return redirect('/')

def error_page(request):
    return  render(request , 'error.html')

def ChangePassword(request , token):
    context = {}
    try:
        profile_obj = Customer.objects.filter(auth_token = token).first()
        context = {'user_id': profile_obj.user.id}
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('reconfirm_password')
            user_id = request.POST.get('user_id')
            if user_id is None:
                messages.success(request, 'No user found.')
                return redirect(f'/account/change-password/{token}')
            if  new_password != confirm_password:
                messages.success(request, 'both should be equal.')
                return redirect(f'/account/change-password/{token}/')
            messages.success(request, 'Password has been changed')
            user_obj = User.objects.get(id = user_id)
            user_obj.set_password(new_password)
            user_obj.save()
            return redirect('/account/signin')
    except Exception as e:
        print(e)
    return render(request , 'password/change-password.html' , context)
def ForgerPassword(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            
            if not User.objects.filter(username=username).first():
                messages.success(request, 'Not user found with this username.')
                return redirect('/account/forget-password/')
            
            user_obj = User.objects.get(username = username)
            profile_obj= Customer.objects.get(user = user_obj)
            token = profile_obj.auth_token
            send_forget_password_mail(user_obj.email , token)
            messages.success(request, 'An email is sent.')
            return redirect('/account/forget-password/')
    except Exception as e:
        print(e)
    return render(request , 'password/forget-password.html')   
def send_mail_after_registration(email , token):
    subject = 'Your accounts need to be verified'
    message = f"Hello, Hi paste the link to verify your account http://django-btl.herokuapp.com/account/verify/{token}"
    email_from = settings.EMAIL_HOST_USER 
    recipient_list = [email]
    send_mail(subject, message , email_from ,recipient_list)
    
def my_profile(request):
    pro_cus = Customer.objects.filter(user=request.user).first()
    payment = Payment.objects.filter(user=request.user).order_by('-created_at')
    context = {
		'profile': pro_cus,
		'payment':payment,
	}

    return render(request, "dashboard.html", context)

def profile_setting(request):
	pro_cus = Customer.objects.filter(user=request.user).first()
	data = {
		'profile': pro_cus,
	}
	return render(request, 'profile_setting.html',data)

def update(request):
    pro_cus = Customer.objects.filter(user=request.user).first()
    userx = request.user
    payment = Payment.objects.filter(user=request.user).order_by('-created_at')
    if request.method == 'POST':
	    form = CustomerForm(request.POST)
	    if form.is_valid():
		    pro_cus.first_name = form.cleaned_data['first_name']
		    pro_cus.last_name = form.cleaned_data['last_name']
		    pro_cus.email = form.cleaned_data['email']
		    pro_cus.phone = form.cleaned_data['phone']

		    userx.first_name = form.cleaned_data['first_name']
		    userx.last_name = form.cleaned_data['last_name']
		    userx.email = form.cleaned_data['email']
		    userx.phone = form.cleaned_data['phone']
    pro_cus.save()
    userx.save()
    messages.info(request, "Updated successfully!")
    context = {
	    'profile': pro_cus,
	    'payment': payment,
    }

    return render(request, "dashboard.html", context)
