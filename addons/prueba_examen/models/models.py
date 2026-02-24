# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class prueba_examen(models.Model):
#     _name = 'prueba_examen.prueba_examen'
#     _description = 'prueba_examen.prueba_examen'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

