"""Excerpt: checkout.py -- apply_discount computes the line total we charge."""
from legacy import apply_discount


def line_total(item_price, coupon_value):
    # Coupons are fixed-amount (e.g. $10 off) and can be worth more than a cheap item. Whatever this
    # returns is sent straight to the payment processor as the amount to charge -- and a negative
    # amount (paying the customer) is rejected by the processor.
    return apply_discount(item_price, coupon_value)
