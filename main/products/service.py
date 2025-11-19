from .models import Product, ProductSolicitation
import datetime
from django.db import transaction

class ProductService:

    @transaction.atomic
    def add_product_to_cart(product_data):
        if not ProductSolicitation.objects.filter(product=product_data.get('id')).exists():
            product = Product.objects.create(**product_data)
            solicitation = ProductSolicitation.objects.create(
                product=product,
                status='EN_CARRITO',
                quantity=1,
                solicitant_name="",
                solicitant_contact="",
                date = datetime.datetime.now(),
                is_paid=False,
            )
        else:
            solicitation = ProductSolicitation.objects.get(product=product_data.get('id'))
            solicitation.quantity += 1
            solicitation.save()
        return solicitation

    def get_cart_solicitations(solicitant_name, solicitant_contact):
        return ProductSolicitation.objects.filter(status='EN_CARRITO').filter(solicitant_name=solicitant_name).filter(solicitant_contact=solicitant_contact)

    @transaction.atomic
    def update_solicitation_status(solicitation_id, new_status):    
        solicitation = ProductSolicitation.objects.get(id=solicitation_id)
        solicitation.status = new_status
        solicitation.save()
        return solicitation

    @transaction.atomic
    def mark_solicitation_as_paid(solicitation_id):
        solicitation = ProductSolicitation.objects.get(id=solicitation_id)
        solicitation.is_paid = True
        solicitation.save()
        return solicitation

    @transaction.atomic
    def remove_product_from_cart(solicitation_id):
        if ProductSolicitation.objects.filter(id=solicitation_id).exists() \
            and ProductSolicitation.objects.get(id=solicitation_id).status == 'EN_CARRITO':

            if  ProductSolicitation.objects.get(id=solicitation_id).quantity == 1:
                solicitation = ProductSolicitation.objects.get(id=solicitation_id)
                solicitation.delete()
                return True
            else:
                solicitation = ProductSolicitation.objects.get(id=solicitation_id)
                solicitation.quantity -= 1
                solicitation.save()
                return solicitation

