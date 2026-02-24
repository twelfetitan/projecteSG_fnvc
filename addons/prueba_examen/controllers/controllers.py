# -*- coding: utf-8 -*-
# from odoo import http


# class PruebaExamen(http.Controller):
#     @http.route('/prueba_examen/prueba_examen', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/prueba_examen/prueba_examen/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('prueba_examen.listing', {
#             'root': '/prueba_examen/prueba_examen',
#             'objects': http.request.env['prueba_examen.prueba_examen'].search([]),
#         })

#     @http.route('/prueba_examen/prueba_examen/objects/<model("prueba_examen.prueba_examen"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('prueba_examen.object', {
#             'object': obj
#         })

