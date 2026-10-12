{
    "name": "Manufacturing Pasteurisation Data",
    'version': '20.0.1.0.1',
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
    'author': 'Matouš Čmelík',
    'maintainer': 'Matouš Čmelík',
    'website': 'https://github.com/cmeldas/odoo_mrp_pasteurization',
    'support': 'cmeldas@gmail.com',
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
