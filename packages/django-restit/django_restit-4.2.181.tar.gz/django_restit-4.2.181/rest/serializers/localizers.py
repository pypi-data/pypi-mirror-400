from rest import helpers as rh


def cents_to_currency(cents, extra=None):
    currency, cents = divmod(cents, 100)
    return f"{currency}.{cents:02}"


def cents_to_dollars(cents, extra=None):
    dollars, cents = divmod(cents, 100)
    return f"${dollars}.{cents:02}"


def timezone(value, extra=None):
    value = rh.convertToLocalTime(extra, value, True)
    return value.strftime("%Y-%m-%d %H:%M:%S %Z")
