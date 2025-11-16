from django.contrib import admin

from .testimonial.models import Testimonial
from .products.models import Product, ProductSolicitation



class ProductSolicitationAdmin(admin.ModelAdmin):    
    list_display = (
        'id', 
        'date', 
        'status',
        'solicitant_name', 
        'solicitant_contact',
        'product', 
        'quantity', 
        'is_paid', 
        'registered_user',
    )
    
    list_filter = ('status', 'is_paid', 'date', 'product')
    
    search_fields = ('solicitant_name', 'solicitant_contact', 'product__name', 'product__ref')
    
    fieldsets = (
        ('Product Details', {
            'fields': ('product', 'quantity', 'date')
        }),
        ('Solicitant Information', {
            'fields': ('solicitant_name', 'solicitant_contact', 'registered_user')
        }),
        ('Order Fulfillment (Admin Only)', {
            'fields': ('status', 'is_paid')
        }),
    )
    
    readonly_fields = ('date',)



admin.site.register(Product)

admin.site.register(Testimonial)

admin.site.register(ProductSolicitation, ProductSolicitationAdmin)