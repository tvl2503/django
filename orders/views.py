from django.contrib.auth.models import User
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from store.models import Customer
from django.contrib import messages
import random


def sendEmail(request, order):
    cus = Customer.objects.get(user=request.user)
    mail_subject = 'Thank you for your order!'
    message = render_to_string('order/order_recieved_email.html', {
        'user': request.user,
        'order': order
    })
    to_email = cus.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()


def payments(request):
    if request.is_ajax and request.method == 'POST':
        data = request.POST
        order_id = data['orderID']
        trans_id = data['transID']
        payment_method = data['payment_method']
        status = data['status']

            # Lấy bản ghi order
        order = Order.objects.get(
            user=request.user, is_ordered=False, order_number=order_id)
            # Tạo 1 bản ghi payment
        payment = Payment(
            user=request.user,
            payment_id=trans_id,
            payment_method=payment_method,
            amount_paid=order.order_total,
            status=status,
        )
        payment.save()

        order.payment = payment
        order.is_ordered = True
        order.save()

            # Chuyển hết cart_item thành order_product
        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            order_product = OrderProduct()
            order_product.order_id = order.id
            order_product.payment = payment
            order_product.user_id = request.user.id
            order_product.product_id = item.product.id
            order_product.quantity = item.quantity
            order_product.product_price = item.product.price
            order_product.ordered = True
            order_product.save()

            cart_item = CartItem.objects.get(id=item.id)
            order_product = OrderProduct.objects.get(id=order_product.id)
            order_product.save()

                # Reduce the quantity of the sold products
            product = Product.objects.get(id=item.product.id)
            product.stock -= item.quantity
            product.save()

            # Xóa hết cart_item
        CartItem.objects.filter(user=request.user).delete()
        order = Order.objects.get(
            user=request.user, is_ordered=True, order_number=order_id)
            # Gửi thư cảm ơn
        sendEmail(request=request, order=order)

            # Phản hồi lại ajax
        data = {
            'order_number': order.order_number,
            'transID': payment.payment_id,
        }
        return JsonResponse({'data':data} , status=200)
    # except Exception as e:
    return HttpResponse("Loi")


def place_order(request, total=0, quantity=0,):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user).order_by('-quantity')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store_page')
    # print(cart_items)
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            cus = Customer.objects.get(user=current_user)
            data = Order()
            data.user = current_user
            data.first_name = cus.first_name
            data.last_name = cus.last_name
            data.phone = cus.phone
            data.email = cus.email
            data.address = form.cleaned_data['address']
            data.country = form.cleaned_data['country']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt) 
            current_date = d.strftime("%Y%m%d")     # 20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(
                user=current_user, is_ordered=False, order_number=order_number)
            
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'order/payments.html', context)
    else:
        return HttpResponse('checkout')


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True,user = request.user)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity
        
        payment = Payment.objects.get(payment_id=transID)
        grand_total = order.order_total
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
            'grand_total':grand_total,
        }
        return render(request, 'order/order_complete.html', context)
    except Exception:
        return redirect('home')

def pay_on_receipt(request):
    val1 = random.randint(1e11,1e12)
    # Lấy bản ghi order
    order = Order.objects.filter(
            user=request.user, is_ordered=False).first()
        # Tạo 1 bản ghi payment
    payment = Payment(
        user=request.user,
        payment_id=str(val1),
        payment_method='Pay on receipt',
        amount_paid=order.order_total,
        status='COMPLETED',
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

        # Chuyển hết cart_item thành order_product
    ordered_pro =[]
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product.id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()
        ordered_pro.append(order_product)

        cart_item = CartItem.objects.get(id=item.id)
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.save()

            # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product.id)
        product.stock -= item.quantity
        product.save()

            # Xóa hết cart_item
    CartItem.objects.filter(user=request.user).delete()
        # Gửi thư cảm ơn
    sendEmail(request=request, order=order)

    order = Order.objects.filter(is_ordered=True, user=request.user).first()
    ordered_products = OrderProduct.objects.filter(order_id=order.id)
    print(ordered_products)
    subtotal = 0
    for i in ordered_pro:
        subtotal += i.product_price * i.quantity
    tax = (2 * subtotal) / 100
    grand_total = subtotal + tax
    context = {
        'order': order,
        'ordered_products': ordered_pro,
        'order_number': order.order_number,
        'transID': payment.payment_id,
        'payment': payment,
        'subtotal': subtotal,
        'grand_total': grand_total,
    }
    return render(request, 'order/order_complete.html', context)

def history_detail(request):
    odered = OrderProduct.objects.filter(user=request.user).order_by('-created_at')
    page = request.GET.get('page')

    data = {
        'order':odered,
    }
    return render(request, 'order/order_detail.html', data)
