{
    'name': 'Custom Executive Dashboard',
    'version': '18.0.1.0.0',
    'category': 'Productivity',
    'summary': 'YTD Dashboard for Sales, Purchases, and Inventory',
    'description': 'Custom OWL Dashboard featuring Year-to-Date metrics and charts.',
    'author': 'Your Name',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'sale_management', 'purchase', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_dashboard/static/src/css/dashboard.css',
            'custom_dashboard/static/src/js/dashboard_component.js',
            'custom_dashboard/static/src/xml/dashboard_template.xml',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}