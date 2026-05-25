from django.contrib import admin

from .models import   Cart, CartItem, Category, Order, OrderItem, Product
# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug':('name',)}
    list_per_page = 20
    
admin.site.register(Category,CategoryAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','price','created','updated']
    prepopulated_fields = {'slug':('name',)}
    list_per_page = 20
    
admin.site.register(Product,ProductAdmin)  


admin.site.register(Cart)  
admin.site.register(CartItem)


class OrderItemAdmin(admin.TabularInline):
    model = OrderItem
    fieldsets = [
        ('Product', {'fields': ['product'], }),
        ('Quantity', {'fields': ['quantity'], }),
        ('Price', {'fields': ['price'], }),
    ]
    readonly_fields = ['product', 'quantity', 'price']
    can_delete = False
    max_num = 0
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = ['created','total','first_name','last_name','phone','address']
    search_fields = ['id','first_name','last_name','emailAddress','phone','city']
    inlines = [
        OrderItemAdmin,
    ]
    
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False 