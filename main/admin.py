from django.contrib import admin

from .testimonial.models import Testimonial
from .products.models import Product, Order, OrderProduct
from .appointments.models import Appointment


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields = ('price_at_order',)


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'date',
        'status',
        'solicitant_name',
        'solicitant_contact',
        'is_paid',
        'registered_user',
    )
    list_filter = ('status', 'is_paid', 'date')
    search_fields = ('solicitant_name', 'solicitant_contact')
    fieldsets = (
        ('Order Details', {
            'fields': ('date',)
        }),
        ('Solicitant Information', {
            'fields': ('solicitant_name', 'solicitant_contact', 'solicitant_address', 'registered_user')
        }),
        ('Order Fulfillment (Admin Only)', {
            'fields': ('status', 'is_paid')
        }),
    )
    readonly_fields = ('date',)
    inlines = (OrderProductInline,)



admin.site.register(Product)

admin.site.register(Testimonial)

admin.site.register(Order)

admin.site.register(OrderProduct)


admin.site.register(Appointment)