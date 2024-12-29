class POSManager {
    constructor() {
        this.cart = new Map();
        this.bindEvents();
        this.initializeWebSocket();
    }

    bindEvents() {
        // Événements des produits
        document.querySelectorAll('.product-item').forEach(btn => {
            btn.addEventListener('click', () => this.addToCart(btn));
        });

        // Filtres
        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.filterProducts(e.target.value);
        });

        document.getElementById('categoryFilter').addEventListener('change', (e) => {
            this.filterByCategory(e.target.value);
        });

        // Paiement
        document.querySelectorAll('[data-payment]').forEach(btn => {
            btn.addEventListener('click', () => {
                const method = btn.dataset.payment;
                this.processSale(method);
            });
        });
    }

    initializeWebSocket() {
        this.ws = new WebSocket(`ws://${window.location.host}/ws/pos/`);
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'stock_update') {
                this.updateProductStock(data.product_id, data.new_stock);
            }
        };

        this.ws.onclose = () => {
            console.log('WebSocket connection closed');
            // Tentative de reconnexion
            setTimeout(() => this.initializeWebSocket(), 5000);
        };
    }

    addToCart(productBtn) {
        const id = productBtn.dataset.id;
        const stock = parseInt(productBtn.dataset.stock);

        if (stock <= 0) {
            toastr.error('Produit en rupture de stock');
            return;
        }

        const currentItem = this.cart.get(id);
        if (currentItem && currentItem.quantity >= stock) {
            toastr.warning('Stock insuffisant');
            return;
        }

        const price = parseFloat(productBtn.dataset.price);
        const name = productBtn.dataset.name;

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
        const cartDiv = document.getElementById('cart-items');
        cartDiv.innerHTML = '';
        let total = 0;

        for (let [id, item] of this.cart) {
            const itemTotal = item.price * item.quantity;
            total += itemTotal;

            const itemDiv = document.createElement('div');
            itemDiv.className = 'cart-item d-flex justify-content-between align-items-center p-2 border-bottom';
            itemDiv.innerHTML = `
                <div>
                    <span class="fw-bold">${item.name}</span><br>
                    <small class="text-muted">${item.price.toFixed(2)} € x ${item.quantity}</small>
                </div>
                <div class="d-flex align-items-center">
                    <span class="me-3">${itemTotal.toFixed(2)} €</span>
                    <button class="btn btn-sm btn-outline-danger" onclick="pos.removeFromCart('${id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            cartDiv.appendChild(itemDiv);
        }

        document.getElementById('cart-total').textContent = `${total.toFixed(2)} €`;
        this.updatePaymentButtons(total > 0);
    }

    removeFromCart(productId) {
        this.cart.delete(productId);
        this.updateCartDisplay();
    }

    updatePaymentButtons(enabled) {
        document.querySelectorAll('[data-payment]').forEach(btn => {
            btn.disabled = !enabled;
        });
    }

    async processSale(paymentMethod) {
        try {
            const formData = new FormData();
            formData.append('payment_method', paymentMethod);
            
            const items = [];
            for (let [id, item] of this.cart) {
                items.push({
                    id: item.id,
                    quantity: item.quantity
                });
            }
            formData.append('products', JSON.stringify(items));

            const response = await fetch('/api/pos/process-sale/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                toastr.success('Vente effectuée avec succès');
                this.cart.clear();
                this.updateCartDisplay();
                this.printReceipt(data.sale_id);
            } else {
                throw new Error(data.error || 'Erreur lors de la vente');
            }

        } catch (error) {
            toastr.error(error.message);
            console.error('Erreur:', error);
        }
    }

    filterProducts(search) {
        const searchLower = search.toLowerCase();
        document.querySelectorAll('.product-item').forEach(item => {
            const name = item.dataset.name.toLowerCase();
            const visible = name.includes(searchLower);
            item.style.display = visible ? '' : 'none';
        });
    }

    filterByCategory(categoryId) {
        document.querySelectorAll('.product-item').forEach(item => {
            if (!categoryId || item.dataset.category === categoryId) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }

    updateProductStock(productId, newStock) {
        const productBtn = document.querySelector(`[data-id="${productId}"]`);
        if (productBtn) {
            productBtn.dataset.stock = newStock;
            const stockSpan = productBtn.querySelector('.stock-qty');
            if (stockSpan) {
                stockSpan.textContent = newStock;
            }
            if (newStock <= 0) {
                productBtn.classList.add('out-of-stock');
            }
        }
    }

    async printReceipt(saleId) {
        try {
            const response = await fetch(`/api/pos/receipt/${saleId}/`);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const printWindow = window.open(url);
            printWindow.onload = () => {
                printWindow.print();
                window.URL.revokeObjectURL(url);
            };
        } catch (error) {
            console.error('Erreur d\'impression:', error);
            toastr.error('Erreur lors de l\'impression du ticket');
        }
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    window.pos = new POSManager();
});
