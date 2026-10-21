"""Input checks shared by the forms. Each returns a dict of field -> message;
an empty dict means the input is valid. No Flask, no database.
"""

from __future__ import annotations

import re

# ACRA UEN formats: business nnnnnnnnX; local company yyyynnnnnX;
# other entities TyyPQnnnnX (T = 20xx, S = 19xx, R = 18xx).
UEN = r"(?:\d{8}[A-Z]|\d{9}[A-Z]|[TSR]\d{2}[A-Z]{2}\d{4}[A-Z])"
UEN_RE = re.compile(rf"^{UEN}$")
# CPF Submission Number: UEN, 3-letter payment type, 2-digit serial (dashes optional).
CSN_RE = re.compile(rf"^{UEN}-?[A-Z]{{3}}-?\d{{2}}$")
TAX_REF_RE = re.compile(r"^[A-Z0-9]{8,12}$")
# Malaysian employer numbers vary by agency; accept letters, digits, spaces and dashes.
MY_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9 \-]{0,19}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

SG_FIELDS = {
    "sg.uen": ("UEN", UEN_RE, "Use the ACRA format, e.g. 201912345A or T09LL0001B."),
    "sg.cpf_csn": ("CPF Submission Number", CSN_RE, "Use UEN-TYPE-NN, e.g. 201912345A-PTE-01."),
    "sg.iras_tax_ref": ("IRAS tax reference", TAX_REF_RE, "8-12 letters and digits, usually the UEN."),
}
MY_FIELDS = {
    "my.epf_employer_no": ("EPF employer number", MY_ID_RE, "Letters, digits, spaces or dashes, up to 20."),
    "my.socso_employer_code": ("SOCSO employer code", MY_ID_RE, "Letters, digits, spaces or dashes, up to 20."),
    "my.lhdn_employer_no": ("LHDN employer number (E)", MY_ID_RE, "Letters, digits, spaces or dashes, up to 20."),
    "my.hrdc_mycoid": ("HRD Corp MyCoID", MY_ID_RE, "Letters, digits, spaces or dashes, up to 20."),
}


def clean(value) -> str:
    return (value or "").strip()


def company_name_errors(name: str) -> dict:
    name = clean(name)
    if not 2 <= len(name) <= 120:
        return {"name": "Company name must be 2 to 120 characters."}
    return {}


def country_errors(sg: bool, my: bool) -> dict:
    if not (sg or my):
        return {"countries": "Turn on Singapore payroll, Malaysian payroll, or both."}
    return {}


def identifier_errors(values: dict) -> dict:
    """Format checks for statutory identifiers. Blank is allowed (set up later)."""
    errors = {}
    for key, (label, pattern, hint) in {**SG_FIELDS, **MY_FIELDS}.items():
        value = clean(values.get(key)).upper()
        if value and not pattern.match(value):
            errors[key] = f"{label}: {hint}"
    return errors


def entitlement_errors(allowed_sg: bool, allowed_my: bool, sg: bool, my: bool) -> dict:
    """A company may only run the payroll countries enabled for its customer."""
    if (sg and not allowed_sg) or (my and not allowed_my):
        off = [n for on, ok, n in ((sg, allowed_sg, "Singapore"), (my, allowed_my, "Malaysian")) if on and not ok]
        return {"countries": f"{' and '.join(off)} payroll is not enabled for this customer. Ask your iPay administrator."}
    return {}


def text_errors(value: str, field: str, label: str, lo: int = 2, hi: int = 120) -> dict:
    if not lo <= len(clean(value)) <= hi:
        return {field: f"{label} must be {lo} to {hi} characters."}
    return {}


def new_user_errors(display_name: str, email: str, password: str, prefix: str = "") -> dict:
    """A user created by an administrator: a temporary password, no confirmation field."""
    errors = {}
    if not 1 <= len(clean(display_name)) <= 80:
        errors[prefix + "display_name"] = "Enter the person's name (up to 80 characters)."
    if not EMAIL_RE.match(clean(email)):
        errors[prefix + "email"] = "Enter a valid email address."
    if len(password or "") < 10:
        errors[prefix + "password"] = "Use a temporary password of at least 10 characters."
    return errors


def account_errors(display_name: str, email: str, password: str, confirm: str) -> dict:
    errors = {}
    if not 1 <= len(clean(display_name)) <= 80:
        errors["display_name"] = "Enter your name (up to 80 characters)."
    if not EMAIL_RE.match(clean(email)):
        errors["email"] = "Enter a valid email address."
    if len(password or "") < 10:
        errors["password"] = "Use at least 10 characters."
    elif password != confirm:
        errors["confirm"] = "The two passwords do not match."
    return errors
