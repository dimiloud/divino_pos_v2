class POSManager {
    constructor() {
        this.cart = new Map();
        this.bindEvents();
    }

    bindEvents() {
        document.querySelectorAll('.product-item').forEach(btn => {
            btn.addEventListener('click', () => this.addToCart(btn));
        });

        document.querySelector('.btn-cash').addEventListener('click', () => {
            this.processSale('CASH');
        });

        document.querySelector('.btn-card').addEventListener('click', () => {
            this.processSale('CARD');
        });
    }

    addToCart(productBtn) {
        const id = productBtn.dataset.id;
        const price = parseFloat(productBtn.dataset.price);
        const name = productBtn.querySelector('h3').textContent;

        if (this.cart.has(id)) {
            const item = this.cart.get(id);
            item.quantity += 1;
        } else {
            this.cart.set(id, {
                id,
                name,
                price,
                quantity: 1
            });
        }

        this.updateCartDisplay();
    }

    updateCartDisplay() {
        const cartDiv = document.querySelector('.cart-items');
        cartDiv.innerHTML = '';
        let total = 0;

        for (let item of this.cart.values()) {
            const itemTotal = item.price * item.quantity;
            total += itemTotal;

            cartDiv.innerHTML += `
                <div class="cart-item flex justify-between p-2 border-b">
                    <span>${item.name} x${item.quantity}</span>
                    <span>${itemTotal.toFixed(2)} €</span>
                </div>
            `;
        }

        cartDiv.innerHTML += `
            <div class="total font-bold mt-4 text-xl">
                Total: ${total.toFixed(2)} €
            </div>
        `;
    }

    async processSale(paymentMethod) {
        const saleData = {
            payment_method: paymentMethod,
            items: Array.from(this.cart.values()).map(item => ({
                product_id: item.id,
                quantity: item.quantity,
                unit_price: item.price
            }))
        };

        try {
            const response = await fetch('/api/sales/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(saleData)
            });

            if (response.ok) {
                this.cart.clear();
                this.updateCartDisplay();
                alert('Vente effectuée avec succès!');
            } else {
                throw new Error('Erreur lors de la vente');
            }
        } catch (error) {
            alert('Erreur: ' + error.message);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new POSManager();
});