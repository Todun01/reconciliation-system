import re

CHARGE_PATTERN = re.compile(
    r"\b(transfer commission|value added tax|sms charge|commission on nip|stamp|vat charges|vat charge|vatcharges|vatcharge|bank charge|bank charges|bankcharge|bankcharges)\b",
    re.IGNORECASE
)

def is_charge(description):

    if not isinstance(description, str):
        return False

    return bool(CHARGE_PATTERN.search(description))