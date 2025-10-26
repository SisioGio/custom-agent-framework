

VENDORS = [
    {
        'name':'KingOfCars',
        'number':'123456'
    },
        {
        'name':'NYScooters',
        'number':'524543'
    }
        
]
DUMMY_VENDOR_STATEMENTS = {
    "123456": [
        {"date": "01.09.2025", "type": "invoice", "amount": 1000},
        {"date": "15.09.2025", "type": "payment", "amount": 500},
    ]
}

DUMMY_CUSTOMER_STATEMENTS = {
    "654321": [
        {"date": "02.09.2025", "type": "invoice", "amount": 1200},
        {"date": "18.09.2025", "type": "credit_note", "amount": 200},
    ]
}

DUMMY_VENDOR_OPEN_ITEMS = {
    "123456": [
        {"invoice": "INV1001", "amount": 500, "due_date": "30.09.2025"}
    ]
}

DUMMY_CUSTOMER_OPEN_ITEMS = {
    "654321": [
        {"invoice": "CUST1001", "amount": 800, "due_date": "25.09.2025"}
    ]
}

DUMMY_TRIAL_BALANCE = {
    "2025": {
        "09": [
            {"gl_account": "400000", "balance": 10000},
            {"gl_account": "500000", "balance": -2500},
        ]
    }
}

DUMMY_GL_ACCOUNT_BALANCE = {
    "400000": {
        "2025": {
            "09": 10000
        }
    }
}