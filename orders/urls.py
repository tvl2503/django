from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('pay_on_receipt/', views.pay_on_receipt, name='pay_on_receipt'),
    path('history_detail/', views.history_detail, name='history_detail'),
]
