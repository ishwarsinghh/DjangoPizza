from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100,unique=True)
    slug = models.SlugField(max_length=100,unique=True)
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.name



class Product(models.Model):
    name = models.CharField(max_length=100,unique=True)
    slug = models.SlugField(max_length=100,unique=True)
    short_description = models.TextField(max_length=300,blank=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products',blank=True)
    price = models.DecimalField(max_digits=10,decimal_places=2,default='',blank=True,null=True)    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'product'
        verbose_name_plural = 'products'
    
    def __str__(self):
        return self.name
    
class Cart(models.Model):
    cart_id = models.CharField(max_length=100,blank=True) 
    date_added = models.DateField(auto_now_add=True)  
    
    class Meta:
        db_table = 'Cart'
        ordering = ['date_added']
        
    def __str__(self):
        return self.cart_id 
    
class CartItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE) 
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE) 
    quantity = models.IntegerField() 
    active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'CartItem'
        
    def sub_total(self):
        
        return self.product.price * self.quantity
    
    def __str__(self):
        return self.product.name           
    
    
class Order(models.Model):
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='USD Order Total')
    created = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=250, blank=True)
    last_name = models.CharField(max_length=250, blank=True) 
    emailAddress = models.EmailField(blank=True,null=True)       
    phone = models.CharField(max_length=250, blank=True)
    address = models.CharField(max_length=250, blank=True)
    city = models.CharField(max_length=250, blank=True)
    postal_code = models.CharField(max_length=250, blank=True)
    status = models.CharField(max_length=250, blank=True,null=True,default='Pending')

    class Meta:
        db_table = 'Order'
        ordering = ['-created']

    def __str__(self):
        return str(self.id)


class OrderItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE) 
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='USD Price')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    class Meta:
        db_table = 'OrderItem'

    def sub_total(self):
        return self.quantity * self.price

    def __str__(self):
        return self.product.name
        