from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.views import View

class LogoutMethod(View):

	def get(self, request):
		logout(request)
		return redirect("signin")




