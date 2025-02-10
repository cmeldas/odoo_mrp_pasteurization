{
    "name": "Manufacturing Pasteurisation Data",
    "version": "1.0",
    "category": "Manufacturing",
    "summary": "Add pasteurisation data to manufacturing orders",
    "description": """
        Log pasteurisation data on manufacturing orders.
    """,
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_production_views.xml",
        "views/product_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
