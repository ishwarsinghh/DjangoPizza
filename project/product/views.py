from django.shortcuts import get_object_or_404, redirect, render
import os
from rapidfuzz import process,fuzz
from .models import Cart, CartItem, Category, Order, OrderItem, Product,FAQ
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.contrib.auth.models import Group,User
from .forms import SignUpForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.decorators import login_required
import json
# import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
# from dotenv import load_dotenv
from django.db.models import Q,Sum
from openai import OpenAI 
# 1. Configure the Gemini Brain
# load_dotenv()
# my_secret_key=os.getenv("GEMINI_API_KEY")

# genai.configure(api_key=my_secret_key)
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

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

def search_pizza_products(query: str) -> str:
    query_lower = query.lower().strip()
    words = query_lower.split()
    
    if query_lower in ['hi', 'hello', 'hey', 'help', 'test']:
        return "No items searched."

    menu_keywords = ['menu', 'all', 'pizzas', 'pizza', 'list', 'show', 'everything', 'price', 'cost', 'items']
    cheap_keywords = ['cheap', 'cheapest', 'lowest', 'affordable', 'min', 'budget']
    expensive_keywords = ['expensive', 'highest', 'priciest', 'max', 'premium']
    trending_keywords = ['trending', 'popular', 'famous', 'best seller', 'top seller']

    def is_fuzzy_match(user_words, target_list, score_cutoff=65):
        for word in user_words:
            match = process.extractOne(word, target_list, scorer=fuzz.ratio)
            if match and match[1] >= score_cutoff:
                return True
        return False

    if is_fuzzy_match(words, trending_keywords):
        products = Product.objects.filter(orderitem__isnull=False).annotate(
            total_sold=Sum('orderitem__quantity')
        ).order_by('-total_sold')[:3]
        context_header = "Top trending items based on order volume:"
        if not products.exists():
            products = Product.objects.all().order_by('-created')[:3]
            context_header = "Trending items (Our newest additions):"
            
    elif is_fuzzy_match(words, expensive_keywords):
        products = Product.objects.all().order_by('-price')[:3]
        context_header = "Most expensive items:"
        
    elif is_fuzzy_match(words, cheap_keywords):
        products = Product.objects.all().order_by('price')[:3]
        context_header = "Most affordable items:"
        
    elif is_fuzzy_match(words, menu_keywords) or "piza" in query_lower:
        products = Product.objects.all()
        context_header = "General menu items and their prices:"
        
    else:
        products = Product.objects.filter(
            Q(name__icontains=query_lower) | Q(short_description__icontains=query_lower)
        )[:3]
        
        if not products.exists():
            all_products = Product.objects.all()
            product_names = [p.name.lower() for p in all_products]
            match = process.extractOne(query_lower, product_names, scorer=fuzz.WRatio)
            if match and match[1] >= 65:
                matched_name = match[0]
                products = Product.objects.filter(name__icontains=matched_name)[:3]
                
        context_header = f"Search results for '{query_lower}':"
    
    if not products.exists():
        return f"No items found matching '{query_lower}'."
        
    results = [context_header]
    for prod in products:
        results.append(f"- {prod.name}: ₹{prod.price} ({prod.short_description})")
    return "\n".join(results)


# --- DATA SEARCH TOOL: ORDER STATUS ---
def get_user_order_status(user) -> str:
    if not user.is_authenticated:
        return "The user is not logged in. Ask them to log in to view their order history."
    
    recent_orders = Order.objects.filter(emailAddress=user.email).order_by('-created')[:3]
    if not recent_orders.exists():
        return "This user has no past orders."
        
    results = []
    for order in recent_orders:
        results.append(f"- Order #{order.id} (Status: {order.status}) - ₹{order.total}")
    return "\n".join(results)

# --- THE CHATBOT BRAIN (FIXING FAMOUS & CANCELLATION OVERLAPS) ---
@csrf_protect
def pizza_chatbot_backend(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return JsonResponse({'reply': 'I didn\'t catch that. Could you repeat it?'})

            query_lower = user_message.lower()

            # --- 1. DIRECT INTERCEPT: MENU / GENERAL PIZZA ASKS ---
            if any(word in query_lower for word in ['menu', 'pizza', 'pizzas', 'piza']) and len(query_lower.split()) <= 4:
                exact_menu = search_pizza_products("menu")
                return JsonResponse({'reply': exact_menu})

            # --- 2. DIRECT INTERCEPT: CHEAPEST ---
            if any(word in query_lower for word in ['cheap', 'cheapest', 'lowest', 'affordable', 'min', 'budget']):
                cheapest_items = search_pizza_products("cheap")
                if "menu" in query_lower:
                    return JsonResponse({'reply': f"From our menu, here are the most affordable choices:\n{cheapest_items}"})
                return JsonResponse({'reply': cheapest_items})

            # --- 3. DIRECT INTERCEPT: EXPENSIVE ---
            if any(word in query_lower for word in ['expensive', 'highest', 'priciest', 'max', 'premium']):
                expensive_items = search_pizza_products("expensive")
                if "menu" in query_lower:
                    return JsonResponse({'reply': f"From our menu, here are our premium selections:\n{expensive_items}"})
                return JsonResponse({'reply': expensive_items})

           # --- 4. DIRECT INTERCEPT: EXPENSIVE ---
            if any(word in query_lower for word in ['expensive', 'highest', 'priciest', 'max', 'premium']):
                expensive_items = search_pizza_products("expensive")
                if "menu" in query_lower:
                    return JsonResponse({'reply': f"From our menu, here are our premium selections:\n{expensive_items}"})
                return JsonResponse({'reply': expensive_items})

            # --- NEW DIRECT INTERCEPT: DISCOUNTS & OFFERS ---
            # Instantly catches single-word queries like "discount" or phrases like "any offers" / "coupon codes"
            if any(word in query_lower for word in ['discount', 'discounts', 'offer', 'offers', 'coupon', 'coupons', 'deal', 'deals']):
                # Option A: Check your FAQ database first if you have built a 'discount' entry in Django Admin
                words = query_lower.split()
                q_objects = Q()
                for word in words:
                    if len(word) > 3:
                        q_objects |= Q(keywords__icontains=word)
                
                if q_objects:
                    matched_faqs = FAQ.objects.filter(q_objects)
                    if matched_faqs.exists():
                        return JsonResponse({'reply': matched_faqs.first().answer})
                
                # Option B: Fallback preset response if no custom FAQ entry exists yet
                return JsonResponse({'reply': "Get 20% off on your first order using code: PIZZA20! We also have a 'Buy 1 Get 1 Free' offer running every Wednesday."})

            # --- 5. DIRECT INTERCEPT: DELIVERY CHARGES ---
            if "delivery" in query_lower:
                return JsonResponse({'reply': "We deliver within a 5-mile radius around the campus area! Delivery costs a fixed fee of ₹50 per order."})
            # --- 6. EXTRA EXCLUSION GATE: CANCELLATION DETECTOR ---
            # NEW GATE: If they want to cancel, force it to skip order tracking so it hits the Admin FAQ policy instead!
            is_cancelling = any(word in query_lower for word in ['cancel', 'cancellation', 'delete', 'modify', 'change'])

           # --- 7. HIGH PRECEDENCE INTERCEPT: ORDER TRACKING (WITH AUTH GUARD) ---
            has_order_intent = any(word in query_lower for word in ['order', 'orders', 'status', 'track', 'history', 'pending']) or \
                               "order update" in query_lower or \
                               "track my" in query_lower or \
                               "order status" in query_lower

            if has_order_intent and not is_cancelling:
                # Double check that they aren't just asking for store location info
                if not any(loc_word in query_lower for loc_word in ['store', 'location', 'address', 'where is your']):
                    
                    # AUTHENTICATION GUARD: If they want order info but are logged out, stop immediately!
                    if not request.user.is_authenticated:
                        return JsonResponse({'reply': "Please login first to view or track your orders."})
                    
                    # If they are logged in, fetch their actual order records cleanly
                    order_status_info = get_user_order_status(request.user)
                    if "no past orders" not in order_status_info.lower():
                        return JsonResponse({'reply': f"Here is the latest update on your order data:\n{order_status_info}"})
            # --- 8. LOWER PRECEDENCE INTERCEPT: EXACT FAQ MATCH ---
            words = query_lower.split()
            q_objects = Q()
            for word in words:
                if len(word) >= 2:
                    q_objects |= Q(keywords__icontains=word)
            
            if q_objects:
                matched_faqs = FAQ.objects.filter(q_objects)
                if matched_faqs.exists():
                    return JsonResponse({'reply': matched_faqs.first().answer})

            # --- 9. AI MODEL FALLBACK LAYER ---
            db_context = search_pizza_products(user_message)
            order_context = get_user_order_status(request.user)

            system_prompt = (
                "You are a crisp, polite virtual assistant for a Pizza Store.\n\n"
                "CRITICAL RULES:\n"
                "1. DO NOT SUMMARIZE LISTS: If the context provides a list, output it exactly.\n"
                "2. NO FLUFF: Be direct and helpful.\n"
                "3. ACCURACY: NEVER invent prices or details.\n"
                "4. CHITCHAT ALLOWED: You may respond naturally and politely to standard conversational greetings and farewells (like 'hi', 'hello', 'thanks', or 'bye').\n"
                "5. FALLBACK: For any store, menu, or policy question where you cannot find the answer in the context below, reply EXACTLY with: 'Please contact +91 1234567890 for more info.'\n\n"
                f"INVENTORY CONTEXT:\n{db_context}\n\n"
                f"USER ORDER CONTEXT:\n{order_context}\n\n"
            )

            try:
                response = client.chat.completions.create(
                    model="local-model", 
                    messages=[
                        
                        {"role": "system", "content": system_prompt}, 
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.0,
                    timeout=15.0  
                )
                ai_reply = response.choices[0].message.content
            except Exception as ai_error:
                print(f"⚠️ Local LLM Error: {ai_error}") 

            return JsonResponse({'reply': ai_reply})
            
        except Exception as e:
            return JsonResponse({'reply': f"CRASH REPORT: {str(e)}"}, status=500)
            
    return JsonResponse({'error': 'Invalid request method'}, status=400)