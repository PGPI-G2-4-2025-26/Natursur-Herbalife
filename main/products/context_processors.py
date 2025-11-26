from django.db.models import Sum
from .models import OrderProduct
from .service import ProductService  

def cart_status(request):
    item_count = 0
    
    order = ProductService.get_active_cart_for_request(request)

    if order:
        result = OrderProduct.objects.filter(order=order).aggregate(total=Sum('quantity'))
        item_count = result['total'] or 0

    return {
        'cart_has_items': item_count > 0,
        'cart_item_count': int(item_count)
    }