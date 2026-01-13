from toon import encode

data = {
    "order_id": "ORD-5521",
    "customer": {
        "name": "Bob Smith",
        "level": "Gold"
    },
    "inventory": [
        {"id": 101, "item": "Laptop", "price": 1200, "in_stock": True},
        {"id": 102, "item": "Mouse", "price": 25, "in_stock": True},
        {"id": 103, "item": "Monitor", "price": 350, "in_stock": False}
    ],
    "tags": ["electronics", "office", "urgent"]
}

toon_string = encode(data)
print(toon_string)