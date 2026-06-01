def apply_discount(price, discount):
    # a discount can exceed the price; never return a negative price
    result = price - discount
    if result < 0:
        return 0
    return result
