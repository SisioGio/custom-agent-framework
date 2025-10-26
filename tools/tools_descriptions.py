TOOLS = [
    {
        "name": "get_vendor_number",
        "description": "Retrieve the vendor number using vendor name",
        "arguments": [
            {
                "name": "vendor_name",
                "description": "The vendor name",
                "regex": ".*",
                "required": True
            }
        ],
        "output":[
            {
                "name":'vendor_number',
                "description":"The vendor account number"
            }
        ]
    },
    
    {
        "name": "get_vendor_statement",
        "description": "Retrieve the vendor entries (invoices, payments, credit notes)",
        "arguments": [
            {
                "name": "vendor_number",
                "description": "The account number",
                "regex": "[0-9]{6}",
                "required": True
            },
            {
                "name": "date",
                "description": "The desired date on which to retrieve the statement (dd.MM.yyyy)",
                "regex": "[0-9]{2}\\.[0-9]{2}\\.[0-9]{4}",
                "required": True
            }
        ]
    },
    # AP - Vendor open items
    {
        "name": "get_vendor_open_items",
        "description": "Retrieve all open invoices and credit notes for a vendor",
        "arguments": [
            {
                "name": "vendor_number",
                "description": "The vendor account number",
                "regex": "[0-9]{6}",
                "required": True
            }
        ]
    },
    # AR - Customer statement
    {
        "name": "get_customer_statement",
        "description": "Retrieve the customer entries (invoices, payments, credit notes)",
        "arguments": [
            {
                "name": "customer_number",
                "description": "The customer account number",
                "regex": "[0-9]{6}",
                "required": True
            },
            {
                "name": "date",
                "description": "The desired date on which to retrieve the statement (dd.MM.yyyy)",
                "regex": "[0-9]{2}\\.[0-9]{2}\\.[0-9]{4}",
                "required": True
            }
        ]
    },
    # AR - Customer open items
    {
        "name": "get_customer_open_items",
        "description": "Retrieve all open invoices and credit notes for a customer",
        "arguments": [
            {
                "name": "customer_number",
                "description": "The customer account number",
                "regex": "[0-9]{6}",
                "required": True
            }
        ]
    },
    # GL - Trial balance
    {
        "name": "get_trial_balance",
        "description": "Retrieve the general ledger trial balance for a given period",
        "arguments": [
            {
                "name": "fiscal_year",
                "description": "The fiscal year (YYYY)",
                "regex": "[0-9]{4}",
                "required": True
            },
            {
                "name": "period",
                "description": "The fiscal period (MM)",
                "regex": "(0[1-9]|1[0-2])",
                "required": True
            }
        ]
    },
    # GL - Account balance
    {
        "name": "get_gl_account_balance",
        "description": "Retrieve the balance of a specific GL account for a given fiscal year and period",
        "arguments": [
            {
                "name": "gl_account",
                "description": "The general ledger account number",
                "regex": "[0-9]{6,8}",
                "required": True
            },
            {
                "name": "fiscal_year",
                "description": "The fiscal year (YYYY)",
                "regex": "[0-9]{4}",
                "required": True
            },
            {
                "name": "period",
                "description": "The fiscal period (MM)",
                "regex": "(0[1-9]|1[0-2])",
                "required": True
            }
        ]
    }
]
