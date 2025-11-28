# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date, timedelta
from odoo.exceptions import UserError



class Club(models.Model):
    _name = 'natacion.club'
    _description = 'club'

    name = fields.Char()
    town = fields.Char()
    member_ids = fields.One2many('res.partner', 'club_id')
    image = fields.Image()

    ranking = fields.Integer(string="Ranking", compute='_compute_ranking', store=False)
    ranking_icon = fields.Char(compute='_compute_ranking_icon', store=False)
    ranking_color = fields.Char(compute='_compute_ranking_color', store=False)
    ranking_ribbon = fields.Html(string="Ribbon", compute='_compute_ranking_ribbon', store=False)

    @api.depends('member_ids')
    def _compute_ranking(self):
        clubs = self.search([])
        clubs_sorted = sorted(clubs, key=lambda c: len(c.member_ids), reverse=True)
        for idx, c in enumerate(clubs_sorted, start=1):
            c.ranking = idx

    @api.depends('ranking')
    def _compute_ranking_icon(self):
        for c in self:
            if c.ranking == 1:
                c.ranking_icon = "🥇"
            elif c.ranking == 2:
                c.ranking_icon = "🥈"
            elif c.ranking == 3:
                c.ranking_icon = "🥉"
            else:
                c.ranking_icon = ""

    @api.depends('ranking')
    def _compute_ranking_color(self):
        for c in self:
            if c.ranking == 1:
                c.ranking_color = "#FFD700"
            elif c.ranking == 2:
                c.ranking_color = "#C0C0C0"
            elif c.ranking == 3:
                c.ranking_color = "#CD7F32"
            else:
                c.ranking_color = "#FFFFFF"

    @api.depends('ranking_color')
    def _compute_ranking_ribbon(self):
        for c in self:
            c.ranking_ribbon = f'<div style="width:100%; height:8px; background-color:{c.ranking_color};"></div>'

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
    end_quota = fields.Date(readonly=True)
    quota_progress = fields.Float(compute="_compute_quota_progress", store=False)
    quota_valid = fields.Boolean(compute='_compute_quota_valid', store=False)
    event_ids = fields.Many2many('natacion.event', 'natacion_event_swimmer_rel', 
                                 'swimmer_id', 'event_id', 
                                 string="Eventos", readonly=True)
    event_count = fields.Integer(string="Número de Eventos",  compute="_compute_event_count", store=False)
    has_events = fields.Boolean(compute='_compute_has_events', store=False)
    
    image = fields.Image()
    


    @api.depends("year_birth")
    def _get_age(self):
        for s in self:
            s.age = int(fields.Date.to_string(fields.Date.today()).split('-')[0]) - s.year_birth

    def action_open_res_partner_view(self):
         return { 
             'name': 'Swimmer', 
             'view_type': 'form', 
             'view_mode': 'form', 
             'res_model': 'res.partner',
             'res_id': self.id,
             'type': 'ir.actions.act_window',
             'target' : 'current'
         }
    
    def pay_quota(self):
        product = self.env.ref("natacion.product_cuota_anual")

        startDate = fields.Date.today()

        endDt = fields.Date.from_string(startDate)
        endDt = endDt.replace(year=endDt.year + 1)

        order = self.env["sale.order"].create({
        "partner_id": self.id,
        "validity_date": endDt,
        })

        self.env["sale.order.line"].create({
            "order_id": order.id,
            "product_id": product.id,
     })

        
        self.end_quota = endDt
        return order.get_formview_action()
    
    @api.depends("end_quota")
    def _compute_quota_progress(self):
        from datetime import date
        for s in self:
            if not s.end_quota:
                s.quota_progress = 0
                continue

            today = date.today()
            end = s.end_quota

            if today >= end:
                s.quota_progress = 0
                continue

            start = end.replace(year=end.year - 1)

            if today < start:
                s.quota_progress = 100
                continue

            total_days = (end - start).days
            remaining_days = (end - today).days

            s.quota_progress = (remaining_days / total_days) * 100

    @api.depends('end_quota')
    def _compute_quota_valid(self):
        today = date.today()
        for s in self:
            s.quota_valid = bool(s.end_quota and s.end_quota >= today)
    
    @api.depends('event_ids')
    def _compute_event_count(self):
        for s in self:
            s.event_count = len(s.event_ids)

    @api.depends('event_ids')
    def _compute_has_events(self):
        for s in self:
            s.has_events = bool(s.event_ids)

            

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

    @api.constrains('swimmer_ids')
    def _check_quota_validity(self):
        for event in self:
            for swimmer in event.swimmer_ids:
                if not getattr(swimmer, 'quota_valid', False):
                    raise UserError(f"El nadador {swimmer.name} no tiene una cuota válida y no puede participar.")


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
