# -*- coding: utf-8 -*-
# from odoo import http


# class Simagrow(http.Controller):
#     @http.route('/simagrow/simagrow', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/simagrow/simagrow/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('simagrow.listing', {
#             'root': '/simagrow/simagrow',
#             'objects': http.request.env['simagrow.simagrow'].search([]),
#         })

#     @http.route('/simagrow/simagrow/objects/<model("simagrow.simagrow"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('simagrow.object', {
#             'object': obj
#         })

