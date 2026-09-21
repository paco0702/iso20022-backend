import re

import re

IBAN_LENGTHS = {
    "AL": 28, "AD": 24, "AT": 20, "AZ": 28, "BH": 22,
    "BE": 16, "BA": 20, "BR": 29, "BG": 22, "CR": 22,
    "HR": 21, "CY": 28, "CZ": 24, "DK": 18, "DO": 28,
    "EE": 20, "FO": 18, "FI": 18, "FR": 27, "GE": 22,
    "DE": 22, "GI": 23, "GR": 27, "GL": 18, "GT": 28,
    "HU": 28, "IS": 26, "IE": 22, "IL": 23, "IT": 27,
    "JO": 30, "KZ": 20, "XK": 20, "KW": 30, "LV": 21,
    "LB": 28, "LI": 21, "LT": 20, "LU": 20, "MK": 19,
    "MT": 31, "MR": 27, "MU": 30, "MD": 24, "MC": 27,
    "ME": 22, "NL": 18, "NO": 15, "PK": 24, "PS": 29,
    "PL": 28, "PT": 25, "QA": 29, "RO": 24, "SM": 27,
    "SA": 24, "RS": 22, "SK": 24, "SI": 19, "ES": 24,
    "SE": 24, "CH": 21, "TN": 24, "TR": 26, "AE": 23,
    "GB": 22, "VG": 24,
}

def is_valid_iban(iban):
    iban = re.sub(r"\s+", "", iban or "").upper()

    # only letters and number allow
    if not re.fullmatch(r"[A-Z0-9]+", iban):
        print("contained not only letters and numbers.")
        return False

    # must start with 2 letters + 2 digits
    if not re.match(r"^[A-Z]{2}[0-9]{2}", iban):
        print("not start with 2 letters + 2 digits.")
        return False

    country_code = iban[:2]

    if country_code not in IBAN_LENGTHS:
        print("Country code not in the list")
        return False


    if len(iban) != IBAN_LENGTHS[country_code]:
        print("Country code length doesn't match.")
        return False

    #Rearrange: move first 4 chars to the end
    rearrange = iban[4:] + iban[:4]

    # Convert letters to numbers
    numeric = ""
    for char in rearrange:
        if char.isalpha():
            numeric += str(ord(char)-55)
        else:
            numeric += char

    # Mod 97 check
    remainder = 0
    for digit in numeric:
        remainder = (remainder * 10 + int(digit)) % 97

    if remainder != 1:
        print("Remainder is not 0")
        return False
    return True