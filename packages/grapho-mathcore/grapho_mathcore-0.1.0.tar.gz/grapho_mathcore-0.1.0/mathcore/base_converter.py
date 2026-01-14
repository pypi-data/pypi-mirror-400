DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def to_base10(number, base):
    value=0
    for digit in number:
        value = value * base + DIGITS.index(digit)
    return value

def from_base10(number, base):
    if number == 0:
        return "0"
    result = ""
    while number > 0:
        result = DIGITS[number % base] + result
        number //= base
    return result

def convert_base(number, base_from, base_to):
    number = number.upper()

    if not (2 <= base_from <= 36 and 2 <= base_to <= 36):
        raise ValueError("Bases need to be between 2 and 36")
    
    for digit in number:
        if digit not in DIGITS[:base_from]:
            raise ValueError("Invalid number for the base chosen")
    
    base10 = to_base10(number, base_from)
    return from_base10(base10, base_to)