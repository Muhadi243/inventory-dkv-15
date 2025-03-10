{
    'name': 'Inventaris',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Module for managing inventory',
    'description': 'This module helps to manage inventory including data of barang, lokasi, jenis barang, and inventaris.',
    'author': 'Your Name',
    'company': 'Your Company',
    'maintainer': 'Your Name',
    'depends': ['base', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/barang_views.xml',
        'views/lokasi_views.xml',
        'views/jenis_barang_views.xml',
        'views/inventaris_views.xml',
        'views/menu_views.xml',
        'reports/barang_qr_code_template.xml',
        'reports/barang_qr_code_report.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'AGPL-3',
    'auto_install': False,
}
