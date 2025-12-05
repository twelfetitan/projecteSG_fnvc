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

#Furgoneta ->capacitat(m3), matricula, foto, llista
#Paquet: identificador, volum(m3)
#viatge. Conductor, identificador, furgoneta, llista de paquets, m3 aprofitats
#conductor(res.partner)


class furgoneta(models.Model):
    _name = 'examen.furgoneta'
    _description = 'furgoneta'

    viatges_ids = fields.One2many('examen.viatge', 'furgoneta')
    paquets_enviats = fields.One2many('examen.paquet', 'furgoneta_id')

    matricula = fields.Char()
    capacitat = fields.Integer()
    llista = fields.Char()
    image = fields.Image()

class paquet(models.Model):
    _name = 'examen.paquet'
    _description = 'paquet'

    viatge_id = fields.Many2one('examen.viatge')
    furgoneta_id = fields.Many2one('examen.furgoneta')

    identificador = fields.Char()
    volum = fields.Integer()

    @api.constrains('volum', 'furgoneta_id')
    def _check_capacity(self):
        for rec in self:
            if rec.furgoneta_id:#Si existe la futgoneta
                total = sum(rec.furgoneta_id.paquets_enviats.mapped('volum'))
                if total > rec.furgoneta_id.capacitat:
                    raise ValidationError("La furgoneta no té prou capacitat.")
    
class conductor(models.Model):
    #_name = 'examen.conductor'
    #_description = 'conductor'

    _inherit = 'res.partner'

    viatges_ids = fields.One2many('examen.viatge', 'conductor')

class viatge(models.Model):
    _name = 'examen.viatge'
    _description = 'viatge'

    id_viatge = fields.Char()
    conductor = fields.Many2one('res.partner')
    furgoneta = fields.Many2one('examen.furgoneta')

    llista = fields.One2many('examen.paquet', 'viatge_id')