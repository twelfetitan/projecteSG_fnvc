# -*- coding: utf-8 -*-

from odoo import models, fields, api


class student(models.Model):
    _name = 'proves.student'
    _description = 'Estudionats'

    name = fields.Char(required = True)
    year = fields.Integer()
    photo = fields.Image(max_width= 200, max_height = 200)
    classroom_id = fields.Many2one('proves.classroom', ondelete='set null')
    subject = fields.One2many('proves.mark', 'student')
    floor = fields.Integer(related='classroom_id.floor')


class teacher(models.Model):
    _name = 'proves.teacher'
    _description = 'Profesores'

    name = fields.Char(required = True)
    year = fields.Integer()
    subjects = fields.One2many('proves.subject', 'teacher')
    classroom = fields.Many2many('proves.classroom')
    tutories = fields.Many2many(comodel_name='proves.classroom', # El model en el que es relaciona
                            relation='teacher_tutor_classroom', # (opcional) el nom del la taula en mig
                            column1='teacher_id', # (opcional) el nom en la taula en mig de la columna d'aquest model
                            column2='classroom_id')  # (opcional) el nom de la columna de l'altre model.


class classroom(models.Model):
    _name = 'proves.classroom'
    _description = 'Clases'

    name = fields.Char()
    floor = fields.Integer()
    student_list = fields.One2many('proves.student', 'classroom_id')
    teacher = fields.Many2many('proves.teacher')
    tutors = fields.Many2many(comodel_name='proves.teacher', # El model en el que es relaciona
                            relation='teacher_tutor_classroom', # (opcional) el nom del la taula en mig
                            column1='classroom_id', # (opcional) el nom en la taula en mig de la columna d'aquest model
                            column2='teacher_id')  # (opcional) el nom de la columna de l'altre model.


class mark(models.Model):
    _name = 'proves.mark'
    _description = 'notes'

    name = fields.Char()
    mark = fields.Integer()
    student = fields.Many2one('proves.student')
    subject = fields.Many2one('proves.topic')

class subject(models.Model):
    _name = 'proves.subject'
    _description = 'Asignatuars'

    name = fields.Char(required = True)
    description = fields.Text()
    course = fields.Selection([('1', 'Primer'), ('2', 'Segon')])
    teacher = fields.Many2one('proves.teacher', ondelete = 'set null')
    student = fields.One2many('proves.mark', 'student')
    mark = fields.One2many('proves.mark', 'subject')