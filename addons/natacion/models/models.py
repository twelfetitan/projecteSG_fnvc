# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date, timedelta
from odoo.exceptions import UserError
import random



class Club(models.Model):
    _name = 'natacion.club'
    _description = 'club'


    name = fields.Char()
    town = fields.Char()
    member_ids = fields.One2many('res.partner', 'club_id')
    points = fields.Integer(string='Points', default=0, readonly=True)
    image = fields.Image()


    ranking = fields.Integer(string="Ranking", compute='_compute_ranking', store=False)
    ranking_icon = fields.Char(compute='_compute_ranking_icon', store=False)
    ranking_color = fields.Char(compute='_compute_ranking_color', store=False)
    ranking_ribbon = fields.Html(string="Ribbon", compute='_compute_ranking_ribbon', store=False)


    @api.model
    def set_default_points(self):
        self.search([('points', '=', False)]).write({'points': 0})


    @api.depends('points')
    def _compute_ranking(self):
        clubs = self.search([])
        clubs_sorted = sorted(clubs, key=lambda c: c.points, reverse=True)
        ranking_map = {c.id: idx + 1 for idx, c in enumerate(clubs_sorted)}
        for c in self:
            c.ranking = ranking_map.get(c.id, 0)


    @api.depends('ranking')
    def _compute_ranking_icon(self):
        for c in self:
            c.ranking_icon = {1: "🥇", 2: "🥈", 3: "🥉"}.get(c.ranking, "")


    @api.depends('ranking')
    def _compute_ranking_color(self):
        for c in self:
            c.ranking_color = {
                1: "#FFD700",
                2: "#C0C0C0",
                3: "#CD7F32"
            }.get(c.ranking, "#FFFFFF")


    @api.depends('ranking_color')
    def _compute_ranking_ribbon(self):
        for c in self:
            c.ranking_ribbon = (
                f'<div style="width:100%; height:8px; background-color:{c.ranking_color};"></div>'
            )




class Result(models.Model):
    _name = 'natacion.result'
    
    swimmer_id = fields.Many2one('res.partner')
    series_id = fields.Many2one('natacion.series')
    time = fields.Integer(required=True)  # EJ: 2534 = 25.34s
    rank = fields.Integer(compute='_compute_rank', store=True)
    
    POINTS_BY_RANK = {1:7,2:5,3:3,4:2,5:1}
    
    @api.depends('series_id.result_ids.time')
    def _compute_rank(self):
        for result in self:
            if result.series_id:
                series_results = result.series_id.result_ids.sorted('time')
                rank_map = {r.id: idx+1 for idx,r in enumerate(series_results)}
                result.rank = rank_map.get(result.id, 0)




class Category(models.Model):
    _name = 'natacion.category'
    _description = 'categoria'


    name = fields.Char(required=True)
    minimum_age = fields.Integer(required=True)
    maximum_age = fields.Integer(required=True)


    @api.constrains('minimum_age', 'maximum_age')
    def _check_age_overlap(self):
        for cat in self:
            if cat.minimum_age > cat.maximum_age:
                raise UserError("La edad mínima no puede ser mayor que la máxima.")
            overlap = self.search([
                ('id', '!=', cat.id),
                ('minimum_age', '<=', cat.maximum_age),
                ('maximum_age', '>=', cat.minimum_age),
            ])
            if overlap:
                raise UserError(
                    "Las categorías no pueden solaparse. Solapa con: " +
                    ", ".join(overlap.mapped('name'))
                )



class Swimmer(models.Model):
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
    event_ids = fields.Many2many(
        'natacion.event',
        'natacion_event_swimmer_rel',
        'swimmer_id',
        'event_id',
        string="Eventos",
        readonly=True,
    )
    event_count = fields.Integer(string="Número de Eventos", compute="_compute_event_count", store=False)
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
            'target': 'current',
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
        from datetime import date as pydate
        for s in self:
            if not s.end_quota:
                s.quota_progress = 0
                continue
            today = pydate.today()
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
        column2='swimmer_id',
    )


class Championship(models.Model):
    _name = 'natacion.championship'
    _description = 'campeonato'

    name = fields.Char()
    club_ids = fields.Many2many('natacion.club')
    swimmer_ids = fields.Many2many('res.partner')
    session_ids = fields.One2many('natacion.session', 'championship_id')
    start_date = fields.Date(required=True)
    end_date = fields.Date()
    
    # ✅ NUEVO: Clasificación general HTML
    general_classification = fields.Html(compute='_compute_general_classification')

    def action_open_swimmer_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inscripció Nadadors',
            'res_model': 'natacion.championship.swimmer.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'default_championship_id': self.id,
            },
        }

    def action_generate_random(self):
        self.ensure_one()
        
        # ✅ CREA styles/categories SI NO EXISTEN
        if not self.env['natacion.style'].search([]):
            styles_data = [('Libre',), ('Espalda',), ('Pecho',), ('Mariposa',)]
            self.env['natacion.style'].create([{'name': name} for name, in styles_data])
        
        if not self.env['natacion.category'].search([]):
            categories_data = [('Prebenjamín', 6, 7), ('Benjamín', 8, 9), ('Alevín', 10, 12), ('Infantil', 13, 14)]
            self.env['natacion.category'].create([{'name': name, 'minimum_age': min_age, 'maximum_age': max_age} 
                                                for name, min_age, max_age in categories_data])
        
        from datetime import datetime, timedelta
        import random

        now = datetime.now()
        start_dt = datetime(year=now.year, month=now.month, day=now.day) + timedelta(days=random.randint(7, 30))
        
        created_sessions = self.env['natacion.session']
        for i in range(3, 6):
            session = self.env['natacion.session'].create({
                'name': f'Sesión {i}',
                'date': start_dt + timedelta(hours=10 + i, minutes=0, days=i),
                'championship_id': self.id
            })
            created_sessions |= session

        all_swimmers = self.env['res.partner']
        styles = self.env['natacion.style'].search([])
        categories = self.env['natacion.category'].search([])
        
        for session in created_sessions:
            for j in range(4, 7):
                # ✅ ASIGNA style/category SIEMPRE
                style = random.choice(styles)
                category = random.choice(categories)
                
                event = self.env['natacion.event'].create({
                    'name': f'{random.choice(["50m", "100m"])} {style.name}',
                    'style_id': style.id,
                    'category_id': category.id,
                    'session_id': session.id,
                })
                
                series = self.env['natacion.series'].create({
                    'name': f'Serie {random.randint(1,3)}',
                    'event_id': event.id
                })
                
                swimmers = self.env['res.partner'].search([
                    ('is_swimmer', '=', True),
                    ('club_id', '!=', False)  # ✅ Solo con club
                ], limit=12)
                
                if swimmers:
                    selected = random.sample(list(swimmers), min(6, len(swimmers)))
                    for swimmer in selected:
                        self.env['natacion.result'].create({
                            'swimmer_id': swimmer.id,
                            'series_id': series.id,
                            'time': random.randint(2500, 4500),  # 25-45s realista
                        })
                        all_swimmers |= swimmer
        
        self.swimmer_ids = all_swimmers
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✅ Campeonato generado',
                'message': f'{len(created_sessions)} sesiones con tabla',
                'type': 'success',
            }
        }

    
    @api.depends('session_ids.event_ids.series_ids.result_ids')
    def _compute_general_classification(self):
        for champ in self:
            results = self.env['natacion.result'].search([
                ('series_id.event_id.session_id.championship_id', '=', champ.id),
                ('rank', '>', 0)
            ]).sorted('time')   
        
        html = """
            <table style='width:100%; border-collapse:collapse; font-family:Arial;'>
                <thead>
                    <tr style='background:#2E86AB; color:white;'>
                        <th style='padding:12px; text-align:left;'>Nadador</th>
                        <th style='padding:12px; text-align:center;'>Tiempo</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for idx, result in enumerate(results[:20], 1):
           
            time_str = f"{result.time/100:.2f}s"
            html += f"""
                <tr style='border-bottom:1px solid #ddd;'>
                    <td style='padding:12px;'>{result.swimmer_id.name}</td>
                    <td style='padding:12px; text-align:center; font-weight:bold; color:#2E86AB;'>{time_str}</td>
                </tr>
            """
        
        html += "</tbody></table>"
        champ.general_classification = html if results else "<p>No hay resultados</p>"





class Championship_swimmers_wizard(models.TransientModel):
    _name = 'natacion.championship.swimmers.wizard'
    _description = 'Championship Swimmers Wizard'


    championship_id = fields.Many2one(
        'natacion.championship',
        required=True,
        default=lambda self: self.env.context.get('active_id'),
    )


    swimmer_ids = fields.Many2many(
        'res.partner',
        string='Nadadores (Clubs Inscritos)',
        relation='natacion_championship_swimmer_wizard_rel',
        column1='wizard_id',
        column2='partner_id',
        domain="[]",  # ← Domain dinámico abajo
    )


    swimmer_quota_valid = fields.Many2many(
        'res.partner',
        compute='_compute_quota_status',
        string='Nadadores con Cuota'
    )


    @api.depends('championship_id')
    def _compute_swimmer_domain(self):
        """DOMAIN dinámico: FILTRA lista sin poblar"""
        for wizard in self:
            if wizard.championship_id.club_ids:
                enrolled_clubs = wizard.championship_id.club_ids.ids
                domain = [
                    ('is_swimmer', '=', True),
                    ('club_id', 'in', enrolled_clubs),  # ← Solo clubs inscritos
                    ('quota_valid', '=', True)  # ← Cuota OK
                ]
                return {'domain': {'swimmer_ids': domain}}  # ← SOLO FILTRA, no pobla
            return {'domain': {'swimmer_ids': [('id', '=', False)]}}  # Vacío


    @api.onchange('championship_id')
    def _onchange_championship(self):
        return self._compute_swimmer_domain()  # Trigger domain


    @api.depends('swimmer_ids')
    def _compute_quota_status(self):
        for record in self:
            record.swimmer_quota_valid = record.swimmer_ids.filtered('quota_valid')


    def action_confirm(self):
        if not self.swimmer_ids:
            raise UserError("¡Selecciona nadadores!")
       
        invalid_clubs = self.swimmer_ids.filtered(
            lambda s: s.club_id and s.club_id not in self.championship_id.club_ids
        )
        if invalid_clubs:
            raise UserError(f"Clubs no inscritos: {', '.join(invalid_clubs.mapped('club_id.name'))}")
       
        invalid_quota = self.swimmer_ids.filtered(lambda s: not s.quota_valid)
        if invalid_quota:
            raise UserError(f"Sin cuota: {', '.join(invalid_quota.mapped('name'))}")
       
        self.championship_id.swimmer_ids |= self.swimmer_ids
        return {'type': 'ir.actions.act_window_close'}





class Session(models.Model):
    _name = 'natacion.session'
    _description = 'sesion'


    name = fields.Char()
    date = fields.Datetime(string="Fecha y hora", required=True)
    championship_id = fields.Many2one('natacion.championship')
    event_ids = fields.One2many('natacion.event', 'session_id')
    duration_minutes = fields.Integer(
        string="Duración total (min)",
        compute="_compute_duration",
        store=True,
    )


    @api.constrains('date')
    def _check_session_after_championship(self):
        for s in self:
            if s.championship_id and s.date.date() < s.championship_id.start_date:
                raise UserError("La sesión debe ser posterior al inicio del campeonato.")


    @api.constrains('date')
    def _check_no_overlap(self):
        for s in self:
            others = self.search([
                ('id', '!=', s.id),
                ('date', '=', s.date),
            ])
            if others:
                raise UserError("Ya existe otra sesión en ese mismo día y hora.")


    @api.depends('event_ids.series_ids')
    def _compute_duration(self):
        for s in self:
            s.duration_minutes = len(s.event_ids.mapped('series_ids')) * 10



class Session_wizard(models.TransientModel):
    _name = 'natacion.session_wizard'
    _description = 'Session Wizard'


    session_id = fields.Many2one(
        'natacion.session',
        required=True,
        default=lambda self: self.env.context.get('active_id')
    )
    championship_id = fields.Many2one(
        'natacion.championship',
        related='session_id.championship_id',
        readonly=True
    )
    swimmer_ids = fields.Many2many(
        'res.partner',
        string='Nadadores del Campeonato',
        compute='_compute_swimmers',
        readonly=True
    )


    @api.depends('session_id.championship_id.swimmer_ids')
    def _compute_swimmers(self):
        for wizard in self:
            wizard.swimmer_ids = wizard.session_id.championship_id.swimmer_ids


    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}



   



class Event(models.Model):
    _name = 'natacion.event'
    _description = 'prova'


    name = fields.Char()
    style_id = fields.Many2one('natacion.style')
    category_id = fields.Many2one('natacion.category')
    session_id = fields.Many2one('natacion.session')
    swimmer_ids = fields.Many2many('res.partner', string="Swimmers")
    series_ids = fields.One2many('natacion.series', 'event_id')


    @api.constrains('swimmer_ids')
    def _check_quota_validity(self):
        for event in self:
            for swimmer in event.swimmer_ids:
                if not getattr(swimmer, 'quota_valid', False):
                    raise UserError(
                        f"El nadador {swimmer.name} no tiene una cuota válida y no puede participar."
                    )


    winner_1_id = fields.Many2one(
        'res.partner',
        string="1º Clasificado",
        compute="_compute_winners",
        store=False,
    )
    winner_2_id = fields.Many2one(
        'res.partner',
        string="2º Clasificado",
        compute="_compute_winners",
        store=False,
    )
    winner_3_id = fields.Many2one(
        'res.partner',
        string="3º Clasificado",
        compute="_compute_winners",
        store=False,
    )


    @api.depends('series_ids.result_ids.rank')
    def _compute_winners(self):
        for event in self:
            results = self.env['natacion.result'].search([
                ('series_id', 'in', event.series_ids.ids),
                ('rank', '>', 0),
            ], order='rank asc')
            event.winner_1_id = results[0].swimmer_id if len(results) > 0 else False
            event.winner_2_id = results[1].swimmer_id if len(results) > 1 else False
            event.winner_3_id = results[2].swimmer_id if len(results) > 2 else False



class Series(models.Model):
    _name = 'natacion.series'
    _description = 'serie'


    name = fields.Char()
    event_id = fields.Many2one('natacion.event')
    result_ids = fields.One2many('natacion.result', 'series_id')
    winner_id = fields.Many2one(
        'res.partner',
        string='Ganador',
        compute='_compute_winner',
        store=True,
        readonly=True,
    )


    @api.depends('result_ids.rank', 'result_ids.swimmer_id')
    def _compute_winner(self):
        for series in self:
            winner_result = series.result_ids.filtered(lambda r: r.rank == 1)
            series.winner_id = winner_result[0].swimmer_id if winner_result else False