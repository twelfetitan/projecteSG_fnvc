# -*- coding: utf-8 -*-
# from odoo import http


# class Examen(http.Controller):
#     @http.route('/examen/examen', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/examen/examen/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('examen.listing', {
#             'root': '/examen/examen',
#             'objects': http.request.env['examen.examen'].search([]),
#         })

#     @http.route('/examen/examen/objects/<model("examen.examen"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('examen.object', {
#             'object': obj
#         })

