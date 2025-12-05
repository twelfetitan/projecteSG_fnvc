# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


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

    capacitat = fields.Integer(string = "Capacitat en m3")
    matricula = fields.Char()
    llista = fields.Char()
    image = fields.Image()

    id_viage = fields.One2many('examen.viatge', 'furgoneta', string="viatge")
    paquets_enviats = fields.One2many('examen.paquet', 'furgoneta_id', string="Paquets enviats")

class paquet(models.Model):
     _name = 'examen.paquet'
     _description = 'paquet'

     volum = fields.Integer(string = "Volum en m3")
     id_paquet = fields.Integer()

     viatge_id = fields.Many2one('examen.viatge', string="Viatge")
     furgoneta_id = fields.Many2one('examen.furgoneta', string="Furgoneta", compute='_compute_furgoneta', store=True)

     @api.depends('viatge_id')
     def _compute_furgoneta(self):
        for paquet in self:
            paquet.furgoneta_id = paquet.viatge_id.furgoneta

     @api.constrains('volum', 'viatge_id')#Cuando se modifique volum o viatge_id
     def _check_capacity(self):
        for paquet in self:
            f = paquet.furgoneta_id #f igual a la furgoneta
            if f:  # si hay furgoneta
                # suma de todos los paquetes ya existentes
                total = sum(f.paquets_enviats.mapped('volum'))
                # agregamos el paquete que queremos guardar
                total += paquet.volum
                if total > f.capacitat:
                    raise ValidationError("¡No puedes poner más paquetes! La furgoneta no tiene suficiente espacio.")


class conductor(models.Model):
     #_name = 'examen.conductor'
     #_description = 'conductor'
      _inherit = 'res.partner'

      viatges_ids = fields.One2many('examen.viatge', 'conductor', string="Viatges")

class viatge(models.Model):
     _name = 'examen.viatge'
     _description = 'viatge'

     id_viatge = fields.Integer

     conductor = fields.Many2one('res.partner', string="Conductor")
     furgoneta = fields.Many2one('examen.furgoneta', string="Furgoneta")
     paquets_ids = fields.One2many('examen.paquet', 'viatge_id', string="Paquets")
