# -*- coding: utf-8 -*-

from odoo import models, fields, api

class club(models.Model):
    _name = 'natacion.club'
    _description = 'club'

    name = fields.Char()
    town = fields.Char()
    member = fields.Integer()

class category(model.Model):
    _name = 'natacion.category'
    -description = 'categoria'

    minimumAge = fields.Integer()
    maximumAge = fields.Integer()

class swimmer(model.Model):
    _name = 'natacio.swimmer'
    _description 'nadador'

    name = fields.Char()
    yearBirth = fields.Integer()
    age = fields.Integer()
    category = fields.Char()
    bestTimeStyle = fields.Integer()

class style(model.Model):
    _name = 'natacio.style'
    _description 'estilo'

    name = fields.Char()
    bestSwimmerCategory = fields.Char()

class championship(model.Model):
    _name = 'natacio.championship'
    _description 'campeonato'

    club = fields.Integer()
    swimmer = fields.Char()
    sesion = fields.Char()
    startDate = fields.Integer()
    endDate = fields.Integer()
    