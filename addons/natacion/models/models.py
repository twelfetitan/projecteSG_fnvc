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
    _description = 'resultado'


    swimmer_id = fields.Many2one('res.partner', string="Swimmer")
    series_id = fields.Many2one('natacion.series')
    time = fields.Integer()
    rank = fields.Integer()


    POINTS_BY_RANK = {
        1: 7,
        2: 5,
        3: 3,
        4: 2,
        5: 1,
    }


    def _update_club_points(self, old_rank, new_rank):
        club = self.swimmer_id.club_id
        if not club:
            return


        old_points = self.POINTS_BY_RANK.get(old_rank, 0) if old_rank else 0
        new_points = self.POINTS_BY_RANK.get(new_rank, 0) if new_rank else 0
        club.points = max(0, club.points - old_points + new_points)


    @api.model
    def create(self, vals):
        record = super().create(vals)
        new_rank = vals.get("rank")
        if new_rank:
            record._update_club_points(old_rank=None, new_rank=new_rank)
        return record


    def write(self, vals):
        old_ranks = {rec.id: rec.rank for rec in self}
        res = super().write(vals)
        if "rank" not in vals:
            return res
        for rec in self:
            old_rank = old_ranks.get(rec.id)
            new_rank = rec.rank
            rec._update_club_points(old_rank, new_rank)
        return res



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

    classification_html = fields.Html(compute='_compute_classification_html', store=False)

    @api.depends('session_ids', 'swimmer_ids')
    def _compute_classification_html(self):
        for rec in self:
            if not rec.session_ids:
                rec.classification_html = '<p class="alert alert-info mt-3">Sin sesiones registradas.</p>'
                continue

            results = self.env['natacion.result'].search([
                ('series_id.event_id.session_id.championship_id', '=', rec.id)
            ])

            if not results:
                rec.classification_html = '<p class="alert alert-warning mt-3">Sin resultados. Genera con "Campeonato Aleatorio".</p>'
                continue

            # Mejor tiempo por nadador (min)
            best_times = {}
            for r in results:
                tid = r.swimmer_id.id
                t = r.time / 100.0  # Centésimas → segs (27.03s)
                if tid not in best_times or t < best_times[tid]['time']:
                    best_times[tid] = {
                        'swimmer': r.swimmer_id,
                        'club': r.swimmer_id.club_id.name or '',
                        'time': t
                    }

            sorted_data = sorted(best_times.values(), key=lambda x: x['time'])

            tbody = ''
            for pos, data in enumerate(sorted_data, 1):
                row_class = ''
                if pos == 1:
                    row_class = 'table-success font-weight-bold'
                elif pos == 2:
                    row_class = 'table-warning text-dark'
                elif pos == 3:
                    row_class = 'table-danger bg-light'
                tbody += '''
                <tr class="{}">
                    <td width="50"><strong>{}º</strong></td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>'''.format(row_class, pos, data['swimmer'].name.upper(), data['club'])

            # Resumen como imagen
            start_fmt = rec.start_date.strftime('%d/%m/%Y') if rec.start_date else 'N/A'
            end_fmt = rec.end_date.strftime('%d/%m/%Y') if rec.end_date else 'N/A'
            count = len(rec.swimmer_ids)

            rec.classification_html = '''
            <div class="row mb-3 p-2 bg-light rounded">
                <div class="col-4"><strong>Fecha Inicio:</strong> {}</div>
                <div class="col-4"><strong>Fecha Fin:</strong> {}</div>
                <div class="col-4"><strong>Nadadores:</strong> <span class="badge badge-primary">{}</span></div>
            </div>
            <div class="table-responsive">
                <table class="table table-sm table-hover table-bordered">
                    <thead class="thead-dark">
                        <tr>
                            <th>Pos.</th>
                            <th>Nadador</th>
                            <th>Club</th>
                        </tr>
                    </thead>
                    <tbody>{}</tbody>
                </table>
            </div>'''.format(start_fmt, end_fmt, count, tbody)

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
        """Genera campeonato completo con datos aleatorios reales"""
        self.ensure_one()
        
        from datetime import datetime, timedelta
        import random

        now = datetime.now()
        start_dt = datetime(
            year=now.year,
            month=now.month,
            day=now.day,
        ) + timedelta(days=random.randint(7, 30))
        
        created_sessions = self.env['natacion.session']
        for i in range(random.randint(3, 5)):
            session_dt = start_dt + timedelta(
                hours=random.randint(9, 20),
                minutes=[0, 10, 20, 30][i % 4],
            ) + timedelta(days=i)
            
            session = self.env['natacion.session'].create({
                'name': f'Sesión {i+1}',
                'date': session_dt,
                'championship_id': self.id
            })
            created_sessions |= session
        
        all_swimmers = self.env['res.partner']
        for session in created_sessions:
            for j in range(random.randint(4, 6)):
                event = self.env['natacion.event'].create({
                    'name': f'{random.choice(["50m", "100m", "200m"])} {random.choice(["Libre", "Espalda", "Pecho", "Mariposa"])}',
                    'session_id': session.id,
                })
                
                for k in range(random.randint(2, 3)):
                    series = self.env['natacion.series'].create({
                        'name': f'Serie {k+1}',
                        'event_id': event.id
                    })
                    
                    swimmers = self.env['res.partner'].search([
                        ('is_swimmer', '=', True),
                        ('quota_valid', '=', True)
                    ], limit=20)
                    
                    if swimmers:
                        selected_swimmers = random.sample(
                            list(swimmers),
                            min(8, len(swimmers))
                        )
                        
                        for idx, swimmer in enumerate(selected_swimmers):
                            self.env['natacion.result'].create({
                                'swimmer_id': swimmer.id,
                                'series_id': series.id,
                                'time': random.randint(2500, 4500),  # Fix: 25.00-45.00s realista
                                'rank': idx + 1
                            })
                            all_swimmers |= swimmer
        
        self.swimmer_ids = all_swimmers
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✅ ¡Campeonato generado!',
                'message': f'{len(created_sessions)} sesiones, {len(all_swimmers)} nadadores',
                'type': 'success',
                'sticky': False,
            }
        }


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

    tickets_qty = fields.Integer(
    string="Número de Entradas",
    default=50,
    help="Cantidad de entradas a generar en el PDF"
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


    @api.depends('event_ids.swimmer_ids')
    def _compute_duration(self):
        for s in self:
            total = 0
            for event in s.event_ids:
                swimmers = len(event.swimmer_ids)
                series = (swimmers + 7) // 8
                total += series * 10
            s.duration_minutes = total


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