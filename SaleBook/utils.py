def stats_cart(cart):
    total_amount, total_quantity = 0, 0

    if cart:
        for c in cart:
            total_quantity += c.quantity
            total_amount += c.quantity * c.books.price

    return {
        "total_amount": total_amount,
        "total_quantity": total_quantity
    }
