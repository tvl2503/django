
from django.contrib import admin
from django.urls import path
from .views import *


urlpatterns = [
    path('signin/', loginMethod.as_view(), name="signin"),
    path('register/', registerMethod.as_view(), name="register"),
    path('logout/', logoutMethod.as_view(), name = "logout"),
    path('token' , token_send , name="token_send"),
    path('verify/<auth_token>' , verify , name="verify"),
    path('error' , error_page , name="error"),
    path('forget-password/' , ForgerPassword , name="forget_password"),
    path('change-password/<token>/' , ChangePassword , name="change_password"),
    path('profile/', my_profile ,name='profile'),
    path('profile-setting/', profile_setting ,name='profile_setting'),
    path('profile-update',update,name="update"),

]
