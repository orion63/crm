# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.osv import osv

class event_registration_extension(models.Model):
	# event.py
	_inherit = 'event.registration'
	# when _name is not explicitly set, implicitly it is the same as the original
	partner_function = fields.Char('Cargo')
	registration_type = fields.Selection((('V', 'Venta'), ('A', 'Auspicio'), ('I', 'Invitado'), ('C', 'Canje')), default = 'V', string = 'Tipo')

	@api.multi
	def do_split_register(self):
		#self.nb_register = 1
		event = self.event_id
		event_id = event.id
		partner = self.partner_id
		partner_id = partner.id

		event_registration_obj = self.env['event.registration']
		event_registration = {
			'event_id': event_id,
			'name': self.name,
			'display_name': self.display_name,
			'nb_register': 1,
			'origin': self.origin,
			'registration_type': self.registration_type,
			'partner_id': partner_id,
			'registration_type': self.registration_type
		}
		for counter in range(1, self.nb_register):
			event_registration_obj.create(event_registration)
		self.nb_register = 1

		return True


