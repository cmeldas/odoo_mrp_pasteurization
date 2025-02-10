{
    'name': 'Manufacturing Pasteurisation Data',
    'version': '1.0',
    'category': 'Manufacturing',
    'summary': 'Add pasteurisation data to manufacturing orders',
    'description': """
        This module adds pasteurisation-related fields to manufacturing orders:
        * Pasteurisation Temperature
        * Pasteurisation Duration
        * Pasteurisation Start Time
    """,
    'depends': ['mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_production_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}