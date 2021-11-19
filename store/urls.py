from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('', store.as_view(), name="store_page"),
    # path('add-product/',addProduct , name="add-product"),
]
