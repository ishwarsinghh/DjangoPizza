from django.shortcuts import get_object_or_404, redirect, render

from .models import Cart, CartItem, Category, Order, OrderItem, Product
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.contrib.auth.models import Group,User
from .forms import SignUpForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    products = Product.objects.order_by('-category')

    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,

    }
    return render(request,'product/index.html',context)

def products_by_category(request,category_slug=None):
    category_product = None
    products = None
    
    if category_slug!=None:
        category_product= get_object_or_404(Category,slug=category_slug)
        products = Product.objects.filter(category=category_product)

    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,

    }
    return render(request,'product/index.html',context)

def product_detail(request,pk):
    product_detail = get_object_or_404(Product,pk=pk)
    
    context = {
        'product_detail':product_detail,
    }
    return render(request,'product/product_detail.html',context)

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart    
    
def add_cart(request,product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
        cart.save()  
    try:
        cart_item = CartItem.objects.get(product=product,cart=cart) 
        cart_item.quantity += 1 
        cart_item.save() 
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
        ) 
        cart_item.save() 
    return redirect('cart_detail')   

def cart_detail(request,total=0,counter=0,cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) 
        cart_items = CartItem.objects.filter(cart=cart,active=True) 
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity) 
            counter += cart_item.quantity  
    except ObjectDoesNotExist:
        pass
        
                
    return render(request,'product/cart.html', dict(cart_items=cart_items,total=total,counter=counter))

def cart_remove_minus(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_detail')


def cart_remove_product(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart_detail') 


def checkout(request,total=0,counter=0,cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) 
        cart_items = CartItem.objects.filter(cart=cart,active=True) 
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity) 
            counter += cart_item.quantity  
    except ObjectDoesNotExist:
        pass
    
    if request.method == 'POST':
        # Creating the order
        try:
            order_details = Order.objects.create(
    total=total,
    first_name=request.POST.get('first_name', ''),
    last_name=request.POST.get('last_name', ''),                              
    phone=request.POST.get('phone', ''),
    emailAddress=request.user.email,              
    address=request.POST.get('address', ''),
    city=request.POST.get('city', ''),
    postal_code=request.POST.get('postal_code', ''), 
)
            order_details.save()
            for order_item in cart_items:
                or_item = OrderItem.objects.create(
                    product=order_item.product,
                    quantity=order_item.quantity,
                    price=order_item.product.price,
                    order=order_details
                    )
                or_item.save()
                order_item.delete()
                
            return redirect('thankyou', order_details.id)
        
        except ObjectDoesNotExist:
            pass        
                
    return render(request,'product/checkout.html', dict(cart_items=cart_items,total=total,counter=counter))
                
def thankyou(request, order_id):
    if order_id:
        customer_order = get_object_or_404(Order, id=order_id)
    return render(request, 'product/thankyou.html', {'customer_order': customer_order})

def signupView(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            signup_user = User.objects.get(username=username)
            customer_group = Group.objects.get(name='Customer')
            customer_group.user_set.add(signup_user)
    else:
        form = SignUpForm() 

    return render(request,'product/signup.html',{'form':form})   


def signinView(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request,user)
                return redirect('home')
            else:
                return redirect('signup')
    else:
        form = AuthenticationForm()  
    return render(request,'product/signin.html',{'form':form})      

def signoutView(request):
    logout(request)
    return redirect('signin')  

def search(request):
    products = Product.objects.filter(name__contains=request.GET['title'])
    return render(request, 'product/index.html', {'products': products})

@login_required(redirect_field_name='next',login_url='signin')
def orderHistory(request):
    order_details = [] # This prevents an error if the user isn't authenticated
    if request.user.is_authenticated and request.user.email:
        # 1. Clean the user's email of any hidden spaces
        email = str(request.user.email).strip() 
        
        # 2. Search the database ignoring capital letters (__iexact)
        order_details = Order.objects.filter(emailAddress__iexact=email)
        
    return render(request,'product/order_list.html',{'order_details':order_details})

@login_required(redirect_field_name='next', login_url='signin')
def viewOrder(request, order_id):
    if request.user.is_authenticated:
        email = str(request.user.email).strip()
        order = Order.objects.get(id=order_id, emailAddress__iexact=email)
        order_items = OrderItem.objects.filter(order=order)
    return render(request, 'product/order_detail.html', {'order': order, 'order_items': order_items})   

@login_required(redirect_field_name='next', login_url='signin')
def status_complete(request,order_id):
    if request.user.is_authenticated:
        email = str(request.user.email).strip()
        order = Order.objects.get(id=order_id, emailAddress__iexact=email)
        if request.user.username == 'ishwarsingh' and request.user.email == 'ishwarsinghh26@gmail.com':
            order.status = 'Complete'
            order.save()
            
    return redirect('my_dashboard')

             