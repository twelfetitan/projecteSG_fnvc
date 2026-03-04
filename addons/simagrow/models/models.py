# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Usuario(models.Model):
    _name = 'simagrow.usuario'
    _description = 'Usuario de Simagrow'

    nif = fields.Char(required=True)
    nombre = fields.Char(required=True)
    apellidos = fields.Char(required=True)
    fecha_nacimiento = fields.Date(required=True)
    correo = fields.Char(required=True)
    creditos = fields.Integer(string="Créditos")
    num_incidencias = fields.Integer(string="Número de incidencias", compute="_num_incidencias", store=True)


    incidencia_ids = fields.One2many('simagrow.incidencia', 'usuario_id', string="Incidencias")

    name = fields.Char(string="Nombre completo", compute="_compute_name")

    @api.depends('nombre', 'apellidos')
    def _compute_name(self):
        for record in self:
            record.name = f"{record.nombre} {record.apellidos}"

    @api.constrains('fecha_nacimiento')
    def _check_fecha_nacimiento(self):
        for record in self:
            if record.fecha_nacimiento and record.fecha_nacimiento > fields.Date.today():
                raise ValidationError("La fecha de nacimiento no puede ser futura.")
            
    @api.depends('incidencia_ids')
    def _num_incidencias(self):
        for record in self:
            record.num_incidencias = len(record.incidencia_ids)

    
class Incidencia(models.Model):
    _name = 'simagrow.incidencia'
    _description = 'Incidencia de un usuario'

    idIncidencia = fields.Integer(string="ID Incidencia", readonly=True)
    descripcion = fields.Char(required=True)
    ubicacion = fields.Char(required=True)
    resuelta = fields.Boolean()
    fechaIncidencia = fields.Date(string="Fecha", default=fields.Date.today) #YYYY-MM-DD

    espacio_id = fields.Many2one('simagrow.espacio', string="Espacio", required=True)
    usuario_id = fields.Many2one('simagrow.usuario', string="Usuario", required=True)
    
    @api.model
    def create(self, vals):
        vals['idIncidencia'] = self.search_count([]) + 1
        return super(Incidencia, self).create(vals)

   

class Espacio(models.Model):
    _name = 'simagrow.espacio'
    _description = 'Espacio de incidencia'

    ubicacion = fields.Char(required=True) 
    planta = fields.Selection([
        ('0', 'Planta 0'),
        ('1', 'Planta 1'),
        ('2', 'Planta 2'),
    ], string='Planta', required=True)

    incidencia_ids = fields.One2many('simagrow.incidencia', 'espacio_id', string="Incidencias")


class Recompensas(models.Model):
    _name = 'simagrow.recompensas'
    _description = 'Recompensas disponibles'

    nombre = fields.Char()
    tipo = fields.Selection([
        ('filamento', 'Filamento'),
        ('merchandising', 'Merchandising'),
        ('snacks', 'Snacks'),
    ], string='Tipo')
    tokens = fields.Integer()
    imagen = fields.Image()


class CanjeRecompensaWizard(models.TransientModel):
    _name = 'simagrow.canje_recompensa.wizard'
    _description = 'Wizard para canjear recompensas'

    usuario_id = fields.Many2one('simagrow.usuario', string="Usuario", required=True, default=lambda self: self.env.context.get('active_id'))
    recompensa_id = fields.Many2one('simagrow.recompensas', string="Recompensa", required=True)
    tokens_disponibles = fields.Integer(related='usuario_id.creditos', readonly=True)
    tokens_requeridos = fields.Integer(related='recompensa_id.tokens', readonly=True)

    @api.onchange('usuario_id')
    def _onchange_usuario(self):
        if self.usuario_id:
            return {'domain': {'recompensa_id': [('tokens', '<=', self.usuario_id.creditos)]}}

    def action_canjear(self):
        self.ensure_one()
        if self.usuario_id.creditos < self.recompensa_id.tokens:
            raise UserError(f"No tienes suficientes tokens. Necesitas {self.recompensa_id.tokens} y tienes {self.usuario_id.creditos}.")
        
        self.usuario_id.creditos -= self.recompensa_id.tokens
        return {'type': 'ir.actions.act_window_close'}

