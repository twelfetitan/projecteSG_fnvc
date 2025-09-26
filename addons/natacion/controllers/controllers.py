# -*- coding: utf-8 -*-
# from odoo import http


# class Natacion(http.Controller):
#     @http.route('/natacion/natacion', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/natacion/natacion/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('natacion.listing', {
#             'root': '/natacion/natacion',
#             'objects': http.request.env['natacion.natacion'].search([]),
#         })

#     @http.route('/natacion/natacion/objects/<model("natacion.natacion"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('natacion.object', {
#             'object': obj
#         })

