# -*- coding: utf-8 -*-
from odoo import http
import json

class Natacion(http.Controller):

    @http.route('/natacion/championship', auth='none', type='http', methods=['GET'], csrf=False)
    def championship_info(self, name=None, **kw):
        if not name:
            return "Parametro 'name' es requerido"
        
        championship = http.request.env['natacion.championship'].sudo().search([('name', '=', name)], limit=1)
        
        if not championship:
            return f"Campeonato '{name}' no encontrado"
            
        return championship._get_full_json()

    @http.route('/natacio/pagar_quota', auth='public', cors='*', csrf=False, type='http')
    def apiGet(self, **args):
        import json
        print(args, http.request.httprequest.method)
        if http.request.httprequest.method == 'POST':
            print(http.request.httprequest.data)
            data = json.loads(http.request.httprequest.data)
            record = http.request.env['res.partner'].sudo().search([('id', '=', data['id'])])
            print(record)
            if record:
                record.create_quota_sale_order()
                return http.request.make_json_response(
                    record.read(['name']),
                    headers=None,
                    cookies=None,
                    status=200
                )
            return http.request.make_json_response({"error": "Nadador no encontrado"}, status=404)

    @http.route('/natacio/clubs/string', auth='public', cors='*', csrf=False, type='http', methods=['GET'])
    def get_clubs(self, **kw):
        clubs = http.request.env['natacion.club'].sudo().search([])
   