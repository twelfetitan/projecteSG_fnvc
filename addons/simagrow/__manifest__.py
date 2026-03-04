# -*- coding: utf-8 -*-
{
    'name': "simagrow",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "Simagrow",
    'website': "https://portal.edu.gva.es/ieslluissimarro/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/usuario_views.xml',
        'views/incidencia_views.xml',
        'views/espacio_views.xml',
        'reports/recompensas_report_template.xml',
        'views/recompensas_views.xml',
        'demo/recompensas.xml',
        'demo/espacios.xml',
        'demo/usuarios.xml'
    ],
}
