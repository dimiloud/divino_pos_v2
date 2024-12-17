# Documentation API

## Authentication

Toutes les requêtes API nécessitent une authentification. Utilisez le header `Authorization` avec un token JWT.

```bash
Authorization: Bearer <your-token>
```

## Endpoints

### Products

#### GET /api/products/
Liste tous les produits.

Params:
- `category`: Filtrer par catégorie
- `search`: Rechercher dans le nom ou la description
- `active`: Filtrer par statut (true/false)

#### POST /api/products/
Créer un nouveau produit.

Body:
```json
{
    "name": "Produit test",
    "category": 1,
    "price": "10.00",
    "cost": "5.00",
    "stock_quantity": 100,
    "minimum_stock": 10
}
```

### Sales

#### POST /api/sales/
Créer une nouvelle vente.

Body:
```json
{
    "payment_method": "cash",
    "items": [
        {
            "product": 1,
            "quantity": 2,
            "unit_price": "10.00"
        }
    ]
}
```

### Reports

#### GET /api/reports/sales/
Rapport des ventes.

Params:
- `start_date`: Date de début (YYYY-MM-DD)
- `end_date`: Date de fin (YYYY-MM-DD)