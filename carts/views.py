from django.db.models.fields import NullBooleanField
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from store.models import Product
from .models import Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

@login_required(login_url='account/login/')
def _cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)    # Get object product
    print(product)
    if product.stock > 0:
        if current_user.is_authenticated:

            is_exists_cart_item = CartItem.objects.filter(product=product, user=current_user).exists()
            if is_exists_cart_item:
                cart_items = CartItem.objects.filter(
                    product=product,
                    user=current_user
                )
                cartItem = [item.product for item in cart_items]
                if product in cartItem:
                    print(1)
                    cart_item = CartItem.objects.get(
                        product=product, user=current_user)
                    cart_item.quantity += 1
                    # quanStock = product.stock - 1
                    # Product.objects.filter(id=product_id).update(stock = quanStock)
                    # print(product.stock)
                    # messages.info(request, "Added product!!")
                    
                else:
                    print(2)
                    cart_item = CartItem.objects.create(
                        product=product,
                        user=current_user,
                        quantity=1
                    )
                    # quanStock = product.stock - 1
                    # Product.objects.filter(id=product_id).update(stock=quanStock)
                    # print(product.stock)
            else:
                print(3)
                cart_item = CartItem.objects.create(
                    product=product,
                    user=current_user,
                    quantity=1
                )
                # quanStock = product.stock - 1
                # Product.objects.filter(id=product_id).update(stock=quanStock)
                # print(product.stock)
            cart_item.save()
            return redirect('cart')
    else:
        messages.info(request,"Out of stock! Please buy another product!")
        return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(
                id=cart_item_id,
                product=product,
                user=request.user
            )
            # quanStock = product.stock + 1
            # Product.objects.filter(id=product_id).update(stock=quanStock)
            # print(product.stock)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(
                id=cart_item_id,
                product=product,
                cart=cart
            )
            # quanStock = product.stock + 1
            # Product.objects.filter(id=product_id).update(stock=quanStock)
            print(product.stock)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            quanStock = product.stock + 1
            Product.objects.filter(id=product_id).update(stock=quanStock)
            cart_item.save()
        else:
            # quanStock = product.stock + 1
            # Product.objects.filter(id=product_id).update(stock=quanStock)
            cart_item.delete()
    except Exception:
        pass
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(
                id=cart_item_id,
                product=product,
                user=request.user
            )
            # quanStock = product.stock + cart_item.quantity
            # Product.objects.filter(id=product_id).update(stock=quanStock)
            # print(product.stock)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request=request))
            cart_item = CartItem.objects.get(
                id=cart_item_id,
                product=product,
                cart=cart
            )
            # quanStock = product.stock + cart_item.quantity
            # Product.objects.filter(id=product_id).update(stock=quanStock)
            # print(product.stock)
        cart_item.delete()
    except Exception:
        pass
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request=request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity
        tax = total * 2 / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass    # Chỉ bỏ qua
    print(request.user)
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax if "tax" in locals() else "",
        'grand_total': grand_total if "tax" in locals() else 0,
    }
    return render(request, 'cart.html', context=context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        # cart = Cart.objects.get(cart_id=_cart_id(request=request))
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity
        tax = total * 2 / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass    # Chỉ bỏ qua
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax if "tax" in locals() else "",
        'grand_total': grand_total,
    }
    return render(request, 'order/checkout.html', context=context)
