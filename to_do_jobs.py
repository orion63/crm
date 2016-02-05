# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.osv import osv
from openerp import tools
import datetime


class BD_job(models.Model):
	_name = 'seminarium.jobs.bd_job'	
	date_assigned = fields.Date('Fecha asignación')
	partner = fields.Many2one('res.partner', 'Empresa', delegate=True, required=True)	
	priority = fields.Selection((('1', 'Alta prioridad'), ('2', 'Mediana prioridad'), ('3', 'Menor prioridad')), 'Prioridad', required=True)
	date_done = fields.Date('Fecha ejecución', readonly=True)
	is_done = fields.Boolean('Ejecutado', readonly=True)
	user_done = fields.Many2one('res.users', 'Usuario ejecución', readonly=True)


 	@api.model
	def create(self, values):
		if (values['date_assigned'] == False ):
			values['date_assigned'] = datetime.datetime.today()
		res = super(BD_job, self).create(values)
		return res

	@api.multi
	def do_register_job_done(self):
		self.date_done = datetime.datetime.today()
		self.user_done = self.env.user
		self.is_done = True
		return True	


