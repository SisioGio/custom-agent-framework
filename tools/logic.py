import re
from datetime import datetime
from tools.data import *



def validate_input(value: str, regex: str, name: str):
    if not re.fullmatch(regex, value):
        raise ValueError(f"Invalid {name}: {value}")
    return value


def get_vendor_number(vendor_name: str):
    validate_input(vendor_name, r".*", "vendor_name")

    vendor = next((item for item in VENDORS if item['name'] == vendor_name),None)
    if not vendor:
        raise Exception(f"Vendor {vendor_name} does not exist in our database")
    
    return vendor['number']




def get_vendor_statement(vendor_number: str, date: str):
    validate_input(vendor_number, r"[0-9]{6}", "vendor_number")
    validate_input(date, r"[0-9]{2}\.[0-9]{2}\.[0-9]{4}", "date")
    statements = DUMMY_VENDOR_STATEMENTS.get(vendor_number, [])
    return [s for s in statements if s["date"] == date]


def get_vendor_open_items(vendor_number: str):
    validate_input(vendor_number, r"[0-9]{6}", "vendor_number")
    return DUMMY_VENDOR_OPEN_ITEMS.get(vendor_number, [])


def get_customer_statement(customer_number: str, date: str):
    validate_input(customer_number, r"[0-9]{6}", "customer_number")
    validate_input(date, r"[0-9]{2}\.[0-9]{2}\.[0-9]{4}", "date")
    statements = DUMMY_CUSTOMER_STATEMENTS.get(customer_number, [])
    return [s for s in statements if s["date"] == date]


def get_customer_open_items(customer_number: str):
    validate_input(customer_number, r"[0-9]{6}", "customer_number")
    return DUMMY_CUSTOMER_OPEN_ITEMS.get(customer_number, [])


def get_trial_balance(fiscal_year: str, period: str):
    validate_input(fiscal_year, r"[0-9]{4}", "fiscal_year")
    validate_input(period, r"(0[1-9]|1[0-2])", "period")
    return DUMMY_TRIAL_BALANCE.get(fiscal_year, {}).get(period, [])


def get_gl_account_balance(gl_account: str, fiscal_year: str, period: str):
    validate_input(gl_account, r"[0-9]{6,8}", "gl_account")
    validate_input(fiscal_year, r"[0-9]{4}", "fiscal_year")
    validate_input(period, r"(0[1-9]|1[0-2])", "period")
    return DUMMY_GL_ACCOUNT_BALANCE.get(gl_account, {}).get(fiscal_year, {}).get(period, 0)


