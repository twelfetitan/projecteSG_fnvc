# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import unicodedata
import re

class Usuario(models.Model):
    _name = 'simagrow.usuario'
    _description = 'Usuario de Simagrow'

    
    idUsuario = fields.Integer(string="ID Usuario", readonly=True)
    nif = fields.Char(required=True)
    nombre = fields.Char(required=True)
    apellidos = fields.Char(required=True)
    fecha_nacimiento = fields.Date(required=True)
    correo = fields.Char(string="Correo", readonly=True)
    contrasena = fields.Char(string="Contraseña", readonly=True)
    creditos = fields.Integer(string="Créditos")
    num_incidencias = fields.Integer(string="Número de incidencias", compute="_num_incidencias", store=True)
    admin = fields.Boolean()

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

    #Eliminar tildes y caracteres especiales
    def _limpiar(self, texto):
        nfkd = unicodedata.normalize('NFKD', texto)
        return re.sub(r'[^a-zA-Z]', '', ''.join(c for c in nfkd if not unicodedata.combining(c)))

    @api.model
    def create(self, vals):
        #ID
        max_id = self.sudo().search([], order='idUsuario desc', limit=1).idUsuario or 0
        vals['idUsuario'] = max_id + 1

        #Contrasenña
        apellidos = vals.get('apellidos', '')
        partes_apellidos = apellidos.split() if apellidos else []
        primer_apellido = partes_apellidos[0] if len(partes_apellidos) > 0 else ''
        segundo_apellido = partes_apellidos[1] if len(partes_apellidos) > 1 else ''
        letras = self._limpiar(primer_apellido)[:3].lower()

        fecha = vals.get('fecha_nacimiento', '')
        if fecha:
            partes = str(fecha).split('-')
            dd = partes[2]
            mm = partes[1]
            yy = partes[0][2:]
            vals['contrasena'] = f"{letras}{dd}{mm}{yy}"
        else:
            vals['contrasena'] = letras

       #Correo
        nombre = vals.get('nombre', '')
        parte_nombre = self._limpiar(nombre)[:3].lower()
        parte_ap1 = self._limpiar(primer_apellido)[:3].lower()
        parte_ap2 = self._limpiar(segundo_apellido)[:3].lower()
        dominio = "@administrador.es" if vals.get('admin') else "@alu.edu.gva.es"
        vals['correo'] = f"{parte_nombre}{parte_ap1}{parte_ap2}{dominio}"

        return super(Usuario, self).create(vals)

class Incidencia(models.Model):
    _name = 'simagrow.incidencia'
    _description = 'Incidencia de un usuario'

    idIncidencia = fields.Integer(string="ID Incidencia", readonly=True)
    titulo = fields.Char(required=True)
    descripcion = fields.Char(required=True)
   
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

    idEspacio = fields.Integer(string="ID Espacio", readonly=True)
    ubicacion = fields.Char(required=True)
    planta = fields.Selection([
        ('0', 'Planta 0'),
        ('1', 'Planta 1'),
        ('2', 'Planta 2'),
    ], string='Planta', required=True)

    name = fields.Char(string="Nombre", compute='_compute_name', store=True)

    @api.depends('ubicacion', 'planta')
    def _compute_name(self):
        planta_label = {'0': 'Planta 0', '1': 'Planta 1', '2': 'Planta 2'}
        for record in self:
            record.name = f"{record.ubicacion} - {planta_label.get(record.planta, '')}"

    incidencia_ids = fields.One2many('simagrow.incidencia', 'espacio_id', string="Incidencias")

    @api.model
    def create(self, vals):
        max_id = self.sudo().search([], order='idEspacio desc', limit=1).idEspacio or 0
        vals['idEspacio'] = max_id + 1
        return super(Espacio, self).create(vals)



class Recompensas(models.Model):
    _name = 'simagrow.recompensas'
    _description = 'Recompensas disponibles'

    idRecompensa = fields.Integer(string="ID Recompensa", readonly=True)
    nombre = fields.Char()
    tipo = fields.Selection([
        ('filamento', 'Filamento'),
        ('merchandising', 'Merchandising'),
        ('snacks', 'Snacks'),
    ], string='Tipo')
    tokens = fields.Integer()
    imagen = fields.Binary(string="Imagen", attachment=False)

    

    @api.depends('nombre')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.nombre or f"Recompensa {record.id}"

    @api.model
    def create(self, vals):
        max_id = self.sudo().search([], order='idRecompensa desc', limit=1).idRecompensa or 0
        vals['idRecompensa'] = max_id + 1
        return super(Recompensas, self).create(vals)


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

