from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    auth_token = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    def __str__(self):
    	    return "{0} {1}".format(self.first_name, self.last_name)
    def getFullName(self):
        return "{0} {1}".format(self.first_name, self.last_name)

class Category(models.Model):
    category_name = models.CharField(max_length=50, default="Default")

    def __str__(self):
	    return self.category_name

class Product(models.Model):
    name = models.CharField(max_length=50, default="")
    rootPrice = models.PositiveIntegerField(default=0)
    price = models.PositiveIntegerField(default=0)
    desc = models.CharField(max_length=200, default="")
    category = models.ForeignKey(Category, on_delete = models.CASCADE)
    image = models.ImageField(upload_to="uploads/products")
    stock = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default= True)
    upload_date = models.DateTimeField( default= timezone.now)
    

    def __str__(self):
	    return self.name
    @staticmethod
    def getProductByID(id):
	    if id:
		    return Product.objects.filter(category  = id)
	    else:
		    return Product.objects.all()
    @staticmethod
    def getProductByPrice(min,max):
        if min!=max:
            return Product.objects.filter(price__range=(min,max))
        else:
            return Product.objects.all()


class ShippingAddress(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
	address = models.CharField(max_length=200, null=False)
	city = models.CharField(max_length=200, null=False)
	state = models.CharField(max_length=200, null=False)
	zipcode = models.CharField(max_length=200, null=False)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address
