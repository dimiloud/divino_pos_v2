class POS {
    constructor() {
        this.cart = new Cart();
        this.initEventListeners();
    }

    initEventListeners() {
        // Recherche de produits
        document.getElementById('search-product').addEventListener('input', (e) => {
            this.filterProducts(e.target.value);
        });

        // Filtrage par catégorie
        document.querySelectorAll('[data-category]').forEach(button => {
            button.addEventListener('click', (e) => {
                this.filterByCategory(e.target.dataset.category);
            });
        });

        // Ajout de produits au panier
        document.querySelectorAll('.product-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const productId = card.dataset.productId;
                this.addToCart(productId);
            });
        });

        // Gestion du paiement
        document.getElementById('checkout-btn').addEventListener('click', () => {
            this.showPaymentModal();
        });

        // Vider le panier
        document.getElementById('clear-cart-btn').addEventListener('click', () => {
            this.cart.clear();
        });

        // Validation du paiement
        document.getElementById('confirm-payment-btn').addEventListener('click', () => {
            this.processPayment();
        });
    }

    async addToCart(productId) {
        try {
            const response = await fetch(`/api/products/${productId}/`);
            const product = await response.json();
            this.cart.addItem(product);
        } catch (error) {
            console.error('Erreur lors de l\'ajout au panier:', error);
        }
    }

    filterProducts(searchTerm) {
        const products = document.querySelectorAll('.product-card');
        products.forEach(product => {
            const name = product.querySelector('.card-title').textContent.toLowerCase();
            const show = name.includes(searchTerm.toLowerCase());
            product.style.display = show ? '' : 'none';
        });
    }

    filterByCategory(categoryId) {
        const products = document.querySelectorAll('.product-card');
        products.forEach(product => {
            if (categoryId === 'all' || product.dataset.category === categoryId) {
                product.style.display = '';
            } else {
                product.style.display = 'none';
            }
        });
    }

    showPaymentModal() {
        if (this.cart.total <= 0) {
            alert('Le panier est vide');
            return;
        }

        const modal = new bootstrap.Modal(document.getElementById('payment-modal'));
        document.getElementById('payment-amount').value = `${this.cart.total.toFixed(2)} €`;
        modal.show();
    }

    async processPayment() {
        const paymentMethod = document.getElementById('payment-method').value;
        const saleData = {
            items: this.cart.items.map(item => ({
                product: item.id,
                quantity: item.quantity,
                unit_price: item.price
            })),
            payment_method: paymentMethod,
            total_amount: this.cart.total
        };

        try {
            const response = await fetch('/api/sales/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(saleData)
            });

            if (response.ok) {
                const sale = await response.json();
                this.cart.clear();
                bootstrap.Modal.getInstance(document.getElementById('payment-modal')).hide();
                this.showSuccessMessage('Vente enregistrée avec succès');
            } else {
                throw new Error('Erreur lors du traitement du paiement');
            }
        } catch (error) {
            console.error('Erreur:', error);
            this.showErrorMessage('Erreur lors du traitement du paiement');
        }
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    showSuccessMessage(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.querySelector('.container-fluid').prepend(alert);
    }

    showErrorMessage(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.querySelector('.container-fluid').prepend(alert);
    }
}

// Initialisation du POS
document.addEventListener('DOMContentLoaded', () => {
    new POS();
});