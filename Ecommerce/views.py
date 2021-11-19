from django.shortcuts import render
from store.models import Product, Category
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
def home(request):
    allProducts = Product.objects.all()
    if len(allProducts) > 8:
        products = allProducts[0:8]
    else: products = allProducts
    data = {
        'products' : products,
        # 'categories' : allCategories
    }
    return render(request, 'index.html', data)
def search(request):
    q = request.GET['q']
    data = Product.objects.filter(name__icontains = q).order_by('id')
    return render(request, 'search-result.html', {'data': data})
def detail(request, pk):
    product = Product.objects.get(id = pk)
    context = {'product' :product}
    return render(request, 'product-detail.html', context )

def contact(request):
    return render(request, 'another/contact.html')
