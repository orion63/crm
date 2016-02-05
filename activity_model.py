# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.osv import osv

class Activity_Master(models.Model):
	_name = 'sead.activity.master'
	name = fields.Char('Descripcion', required=True)

class Activity_Child(models.Model):
	_name = 'sead.activity.child'
	name = fields.Char('Descripcion', size=80, required=True)
	master = fields.Many2one('sead.activity.master', 'Actividad Padre')
	complete_name = fields.Char('Nombre completo', compute='get_complete_name', store='True')

	# https://www.odoo.com/documentation/8.0/howtos/backend.html#computed-fields-and-default-values
	# http://es.slideshare.net/openobject/odoo-from-v7-to-v8-the-new-api
	# en modelos heredados hay que llamar al search original (super)!
	@api.one
	@api.depends('master')
	def get_complete_name(self):
		names = [self.master.name, self.name]	
		self.complete_name = ' / '.join(filter(None, names))

	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		if name:
			name = name.split(' / ')[-1]
			args = [('complete_name', operator, name)] + args
		activity = self.search(args, limit=limit)
		return activity.name_get()

	def name_get(self, cr, uid, ids, context=None):
		if not isinstance(ids, list):
			ids = [ids]
		if context is None:
			context = {}

		res = []
		for activity in self.browse(cr, uid, ids, context=context):
 			name = activity.complete_name
			res.append((activity.id, name))
		return res		