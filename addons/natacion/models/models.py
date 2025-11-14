# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Club(models.Model):
    _name = 'natacion.club'
    _description = 'club'

    name = fields.Char()
    town = fields.Char()
    member_ids = fields.One2many('res.partner', 'club_id')
    image = fields.Image()


class Category(models.Model):
    _name = 'natacion.category'
    _description = 'categoria'

    name = fields.Char()
    minimum_age = fields.Integer()
    maximum_age = fields.Integer()


class Swimmer(models.Model):
    # _name = 'natacion.swimmer'
    # _description = 'nadador'
    _inherit = 'res.partner'

    is_swimmer = fields.Boolean()
    year_birth = fields.Integer()
    age = fields.Integer(compute="_get_age")
    category = fields.Many2one('natacion.category')
    club_id = fields.Many2one('natacion.club')
    best_time_ids = fields.One2many('natacion.besttime', 'swimmer_id')
    image = fields.Image()

    @api.depends("year_birth")
    def _get_age(self):
        for s in self:
            s.age = int(fields.Date.to_string(fields.Date.today()).split('-')[0]) - s.year_birth


class BestTime(models.Model):
    _name = 'natacion.besttime'
    _description = 'mejor tiempo por estilo'

    swimmer_id = fields.Many2one('res.partner')
    style_id = fields.Many2one('natacion.style')
    time = fields.Integer()


class Style(models.Model):
    _name = 'natacion.style'
    _description = 'estilo'

    name = fields.Char()
    best_swimmer_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='natacion_style_swimmer_rel',
        column1='style_id',
        column2='swimmer_id'
    )


class Championship(models.Model):
    _name = 'natacion.championship'
    _description = 'campeonato'

    name = fields.Char()
    club_ids = fields.Many2many(
        comodel_name='natacion.club',
        relation='natacion_championship_club_rel',
        column1='championship_id',
        column2='club_id'
    )
    swimmer_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='natacion_championship_swimmer_rel',
        column1='championship_id',
        column2='swimmer_id'
    )
    session_ids = fields.One2many('natacion.session', 'championship_id')
    start_date = fields.Char()
    end_date = fields.Char()


class Session(models.Model):
    _name = 'natacion.session'
    _description = 'sesion'

    name = fields.Char()
    date = fields.Char()
    championship_id = fields.Many2one('natacion.championship')
    event_ids = fields.One2many('natacion.event', 'session_id')


class Event(models.Model):
    _name = 'natacion.event'
    _description = 'prova'

    name = fields.Char()
    style_id = fields.Many2one('natacion.style')
    category_id = fields.Many2one('natacion.category')
    session_id = fields.Many2one('natacion.session')
    swimmer_ids = fields.Many2many(
        'res.partner',
        'natacion_event_swimmer_rel',
        'event_id',
        'swimmer_id'
    )
    series_ids = fields.One2many('natacion.series', 'event_id')


class Series(models.Model):
    _name = 'natacion.series'
    _description = 'serie'

    name = fields.Char()
    event_id = fields.Many2one('natacion.event')
    result_ids = fields.One2many('natacion.result', 'series_id')


class Result(models.Model):
    _name = 'natacion.result'
    _description = 'resultado'

    swimmer_id = fields.Many2one('res.partner')
    series_id = fields.Many2one('natacion.series')
    time = fields.Integer()
    rank = fields.Integer()
