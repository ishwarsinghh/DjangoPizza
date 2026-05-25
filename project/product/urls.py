from django.urls import path

from . import views

urlpatterns = [
    path('', views.index,name="home"),     
    path('<slug:category_slug>', views.products_by_category,name="products_by_category"), 
    path('product/<int:pk>', views.product_detail,name="product_detail"),   
    path('cart/add/<int:product_id>', views.add_cart,name="add_cart"),    
    path('product/cart', views.cart_detail,name="cart_detail"), 
    path('cart/remove/<int:product_id>', views.cart_remove_minus, name='cart_remove_minus'),
    path('cart/remove_product/<int:product_id>', views.cart_remove_product, name='cart_remove_product'),              
    path('product/cart/checkout', views.checkout,name="checkout"), 
    path('thankyou/<int:order_id>', views.thankyou, name='thankyou'), 
    path('account/create/', views.signupView, name='signup'),  
    path('account/signin/', views.signinView, name='signin'), 
    path('account/signout/', views.signoutView, name='signout'),
    path('search/', views.search, name='search'),   
    path('my_dashboard/', views.orderHistory, name='my_dashboard'),  
    path('order/<int:order_id>', views.viewOrder, name='order_detail'),   
    path('order_history/<int:order_id>', views.status_complete, name='status_complete'),      
    

    
    
]       
