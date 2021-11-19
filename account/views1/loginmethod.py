from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views import View

class LoginMethod(View):

	def post(self, request):
		name = request.POST.get('name')
		password1 = request.POST.get('password')
		user = authenticate(username = name, password = password1)
		if user is not None:
			login(request, user)
			return redirect("home")
		else:
			return redirect("signin")

	def get(self, request):
		return render(request, 'signin.html')
