def apply_discount(price, discount):
    result = price - discount
    if result < 0:
        return 0
    return result
