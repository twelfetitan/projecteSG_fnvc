# -*- coding: utf-8 -*-
{
    'name': "natacion",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', "sale"],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/club_views.xml',
        'views/category_views.xml',
        'views/result_views.xml',
        'views/series_views.xml',
        'views/event_views.xml',
        'views/style_views.xml',
        'views/besttime_views.xml',
        'views/swimmer_views.xml',
        'views/views.xml',
        'views/templates.xml',
        'reports/championship_report.xml',
        'reports/championship_report_template.xml',
        'views/championship_views.xml',
        'reports/session_tickets.xml',
        'reports/session_tickets_template.xml',
        'views/session_views.xml',
        
        'demo/clubs.xml',
        'demo/category.xml',
        'demo/swimmers.xml',
        'demo/cuota.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
        
    
    ],
}

