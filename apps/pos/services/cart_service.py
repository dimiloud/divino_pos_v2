from decimal import Decimal
from ..models import Product, ProductVariant

class CartService:
    def __init__(self, session):
        self.session = session
        cart = session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, variant_id, quantity=1):
        """Ajoute un article au panier ou met à jour sa quantité."""
        variant = ProductVariant.objects.get(id=variant_id)
        if variant_id not in self.cart:
            self.cart[variant_id] = {
                'quantity': 0,
                'price': str(variant.product.base_price)
            }
        
        self.cart[variant_id]['quantity'] += quantity
        if self.cart[variant_id]['quantity'] <= 0:
            self.remove(variant_id)
        else:
            self.save()

    def remove(self, variant_id):
        """Retire un article du panier."""
        if variant_id in self.cart:
            del self.cart[variant_id]
            self.save()

    def update_quantity(self, variant_id, quantity):
        """Met à jour la quantité d'un article."""
        if variant_id in self.cart and quantity > 0:
            self.cart[variant_id]['quantity'] = quantity
            self.save()

    def clear(self):
        """Vide le panier."""
        self.session['cart'] = {}
        self.save()

    def get_total(self):
        """Calcule le total du panier."""
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def get_count(self):
        """Retourne le nombre total d'articles."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_items(self):
        """Récupère les articles du panier avec leurs détails."""
        variant_ids = self.cart.keys()
        variants = ProductVariant.objects.filter(
            id__in=variant_ids
        ).select_related(
            'product',
            'size',
            'color'
        )

        for variant in variants:
            cart_item = self.cart[str(variant.id)]
            yield {
                'variant': variant,
                'quantity': cart_item['quantity'],
                'price': Decimal(cart_item['price']),
                'total_price': Decimal(cart_item['price']) * cart_item['quantity']
            }

    def save(self):
        """Sauvegarde les modifications du panier."""
        self.session.modified = True

    def validate_stock(self):
        """Vérifie la disponibilité du stock pour tous les articles."""
        errors = []
        for variant_id, item in self.cart.items():
            variant = ProductVariant.objects.get(id=variant_id)
            if variant.stock_quantity < item['quantity']:
                errors.append({
                    'variant': variant,
                    'requested': item['quantity'],
                    'available': variant.stock_quantity
                })
        return errors