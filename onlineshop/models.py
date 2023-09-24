from django.db import models
from django.db.models import Avg, Count
from django.urls import reverse
from django.utils import timezone

# Create your models here.
class Customer(models.Model):
    first_name=models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    phone=models.CharField(max_length=20)
    image=models.ImageField(blank=True, upload_to="customer_profilePic/")
    password = models.CharField(max_length=200)
    date_join=models.DateTimeField(default=timezone.now)
    last_login=models.DateTimeField(null=True)
    is_active=models.BooleanField(default=False)
    address_line_1 = models.CharField(max_length=50,blank=True)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50,blank=True)
    state = models.CharField(max_length=50,blank=True)
    city = models.CharField(max_length=50,blank=True)
    def __str__(self):
        return self.email
    def full_name(self):
        return self.first_name+" "+self.last_name
    def get_email_field_name(self):
        return self.email
class Category(models.Model):
    category_name=models.CharField(max_length=50)
    description=models.TextField(max_length=250,blank=True)
    image=models.ImageField(upload_to='categories_image/',blank=True)

    def __str__(self):
        return self.category_name
    def get_absolute_category_url(self):      #for individul class view with dynamic link
        return reverse("onlineshop:categoryView",args=[self.category_name])
class Product(models.Model):
    productName = models.CharField(max_length=50)
    description = models.TextField(max_length=250, blank=True)
    price=models.IntegerField()
    images=models.ImageField(upload_to='products_image/')
    stock=models.IntegerField()
    is_available=models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date=models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField()
    def __str__(self):
        return self.productName
    def get_absolute_url(self):      #for individul class view with dynamic link
        return reverse("onlineshop:productview",args=[self.id])
    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count
class product_gallery(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,default=None)
    image=models.ImageField(upload_to='products_image/product_gallery/')
    def __str__(self):
        return self.product.productName

variation_category_choice=(
                              ('color','color'),
                              ('size','size'),
)
class Variation(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category=models.CharField(max_length=100,choices=variation_category_choice)
    variation_value=models.CharField(max_length=100)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.variation_value
class Cart(models.Model):
    cart_id=models.CharField(max_length=250,blank=True)
    date_added=models.DateField(default=timezone.now)

    def __str__(self):
        return self.cart_id
class Cartitem(models.Model):
    user=models.ForeignKey(Customer,on_delete=models.CASCADE,null=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variation=models.ManyToManyField(Variation)
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,null=True)
    quantity=models.IntegerField()
    is_active=models.BooleanField(default=True)
    def total(self):
        return self.product.price*self.quantity
    def __str__(self):
        return self.product.productName

class Payment(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100) # this is the total amount paid
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.payment_id


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Confirm', 'Confirm'),
        ('Picked by courier', 'Picked by courier'),
        ('On the way','On the way'),
        ('Complete','Complete'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS, default='New')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now,null=True)
    updated_at = models.DateTimeField(default=timezone.now,null=True)
    delivery_time=models.DateTimeField(default=timezone.now()+timezone.timedelta(days=7))

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def get_order_url(self):      #for individul class view with dynamic link
        return reverse("onlineshop:order_details",args=[self.order_number])
    def get_track_url(self):      #for individul class view with dynamic link
        return reverse("onlineshop:track_order",args=[self.order_number])
    def __str__(self):
        return self.first_name


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.productName
class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)