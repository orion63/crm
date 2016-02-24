# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.osv import osv
from email.utils import formataddr
from openerp import api, tools


class mass_mailing_extension(osv.osv):
	_name = 'mail.mass_mailing'	
	_inherit = 'mail.mass_mailing'
	partner_ids = fields.Many2many('res.partner', string='Destinatarios')

	@api.one
	def do_agregar_mailing(self):
		# called by button defined in todo_view.xml
		# self represents one record (api.one)
		# self.is_done = not self.is_done
		# must return something for XMLRPC

		dumb = self.env['sead.activity.child']
		ids = [1]
		obj_dumb = dumb.search([('id', 'in', ids)])
		for child in obj_dumb:
			Basura = "\r\n"+ "Activ: " + child.name
			print(Basura)
			raise osv.except_osv(("Warning!"), (Basura))

		#browse
		Basura = "\r\n"+ "Cliente: " + self.name
		raise osv.except_osv(("Warning!"), (Basura))
		return True		

	@api.one
	def do_consolidar_mailing(self):
		# called by button defined in view.xml
		# self represents one record (api.one)
		# self.is_done = not self.is_done
		# must return something for XMLRPC

		valor = []
		partners = self.partner_ids
		for partner in partners:
			valor = valor + [partner.id]
		self.write({'mailing_domain':  [['id', 'in', valor]]})
		return True		

	@api.one
	def do_limpiar_mailing(self):
		# called by button defined in view.xml
		# self represents one record (api.one)
		# self.is_done = not self.is_done
		# must return something for XMLRPC
		valor = []
		self.write({'partner_ids':  [(6, 0, valor)]})
		return True


class mail_mail_extension(osv.osv):
	_name = 'mail.mail'
	_inherit = 'mail.mail'

	def send_get_mail_to(self, cr, uid, mail, partner=None, context=None):
		"""Forge the email_to with the following heuristic:
		  - if 'partner', recipient specific (Partner Name <email>)
		  - else fallback on mail.email_to splitting """
		if partner:
			#print('----------------- xxxxxxxxxxxxxxx---------------')
			#email_to = [formataddr((partner.name, partner.email))]
			if mail.mailing_id:
				destinos = partner.get_mass_emails()
			else:
				destinos = partner.get_all_emails()
			email_to = []
			for destino in destinos:
				email_to = email_to + [formataddr((partner.name, destino))]
			#print(email_to)
			#print('----------------- xxxxxxxxxxxxxxx---------------')
		else:
			email_to = tools.email_split(mail.email_to)
			#email_to = super(mail_mail_extension, self).send_get_mail_to(self, cr, uid, mail, partner=None, context=None)
		return email_to


class mass_mailing_wizard(osv.TransientModel):
	_name = 'mail.mass_mailing.wizard'	
	basura = fields.Char('Telf. directo', size=40)
	mailing_id = fields.Many2one('mail.mass_mailing', 'Mailing')
	partner_ids = fields.Many2many('res.partner', string='Contacts')
	dst_partner_id = fields.Many2one('res.partner', string='Destination Contact')

	def default_get(self, cr, uid, fields, context=None):
		if context is None:
			context = {}
		res = super(mass_mailing_wizard, self).default_get(cr, uid, fields, context)
		if context.get('active_model') == 'res.partner' and context.get('active_ids'):
			partner_ids = context['active_ids']
			res['partner_ids'] = partner_ids            
		return res

	@api.one
	def do_agregar_ejecutivos(self):
		# called by button defined in todo_view.xml
		# self represents one record (api.one)
		# self.is_done = not self.is_done
		# must return something for XMLRPC

		mailing = self.mailing_id
		ejecutivos = self.partner_ids
		basura = mailing.name
		for ejecutivo in ejecutivos:
			if not ejecutivo.is_company:
				mailing.partner_ids = [(4, ejecutivo.id)]
		return True		


class mass_export_partner(osv.TransientModel):
	_name = 'mail.mass_export_partner'	
	partner_ids = fields.Many2many('res.partner', string='Contacts')

	def default_get(self, cr, uid, fields, context=None):
		if context is None:
			context = {}
		res = super(mass_export_partner, self).default_get(cr, uid, fields, context)
		if context.get('active_model') == 'res.partner' and context.get('active_ids'):
			partner_ids = context['active_ids']
			res['partner_ids'] = partner_ids            
		return res


	@api.multi
	def do_exportar_mailing(self):
		return {
			'type' : 'ir.actions.act_url',
			'url': '/web/binary/download_document_mailing?model=res.partner&field=name&id=%s&filename=exportacion.csv'%(self.id),
			'target': 'self',
		}		

	@api.multi
	def do_exportar_etiquetas(self):
		return {
			'type' : 'ir.actions.act_url',
			'url': '/web/binary/download_document_etiquetas?model=res.partner&field=name&id=%s&filename=etiquetas.csv'%(self.id),
			'target': 'self',
		}				