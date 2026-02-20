# -*- coding: utf-8 -*-
from odoo import http


class Natacion(http.Controller):

    @http.route('/natacion/championship', auth='none', type='http', methods=['GET'], csrf=False)
    def championship_info(self, name=None, **kw):
        if not name:
            return "Parametro 'name' es requerido"
        
        championship = http.request.env['natacion.championship'].sudo().search([('name', '=', name)], limit=1)
        
        if not championship:
            return f"Campeonato '{name}' no encontrado"
            
        return championship._get_full_json()

   