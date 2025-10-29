{
    "name": "Manufacturing Pasteurisation Data",
    'version': '18.0.1.0.0',
    "category": "Manufacturing",
    "summary": "Add pasteurisation data to manufacturing orders",
    "description": """
        Log pasteurisation data on manufacturing orders.
    """,
    "depends": ["mrp"],
    "data": [
        "views/mrp_production_views.xml",
        "views/product_views.xml",
    ],
    'author': 'cmeldas@gmail.com',
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
