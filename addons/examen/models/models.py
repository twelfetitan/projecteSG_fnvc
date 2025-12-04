# -*- coding: utf-8 -*-

from odoo import models, fields, api


# class examen(models.Model):
#     _name = 'examen.examen'
#     _description = 'examen.examen'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

class furgoneta(models.Model):
    _name ='examen.furgoneta'
    _description ='furgoneta'

    capacitat = fields.Integer(string='en metres cuadrats')
    matricula = fields.Char()
    imagen = fields.Image()

    viajes_ids = fields.One2many('examen.viatge', 'furgoneta_id', string='Viatges')
    
    paquets_ids = fields.Many2many('examen.paquet', string='Paquetes transportados')


class paquet (models.Model):
    _name ='examen.paquet'
    _description ='paquet'

    identificador = fields.Integer()
    volum = fields.Char(string='en metres cuadrats')
    
class viatge (models.Model):
    _name ='examen.viatge'
    _description ='viatge'
    
    id_viatge = fields.Char(string='Identificador del viaje')
    
    furgoneta_id = fields.Many2one('examen.furgoneta', string='Furgoneta')
    
    paquets_ids = fields.Many2many('examen.paquet', string='Paquetes del viaje')
    
    m3_aprofitats = fields.Integer(string='M3 aprovechados', readonly=True)
    
    conductor_id = fields.Many2one('res.partner', string='Conductor')


class conductor (models.Model): #res.partner
    #_name ='examen.conductor'
    #_description ='conductor'
    _inherit = 'res.partner'



