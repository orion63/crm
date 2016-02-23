# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.osv import osv
from activity_model import Activity_Child
import datetime

class Position_Status(models.Model):
	_name = 'sead.position.status'
	name = fields.Char('Descripción', required=True)

class General_Area(models.Model):
	_name = 'sead.position.general_area'
	name = fields.Char('Descripción', required=True, size=20)

class Business_Area(models.Model):
	_name = 'sead.position.business_area'
	name = fields.Char('Descripción', required=True, size=50)

class event_extension(osv.osv):
	_inherit = 'event.event'
	compatible_code = fields.Char('Codigo compatible', size=20)	


class res_partner_extension(osv.osv):
	_inherit = 'res.partner'
	# when _name is not explicitly set, implicitly it is the same as the original
	status = fields.Many2one('sead.position.status', 'Estatus')
	general_area = fields.Many2one('sead.position.general_area', 'Area general')
	business_area = fields.Many2one('sead.position.business_area', 'Area')
	email_exclude = fields.Boolean('Excluir email')
	email_gracias = fields.Boolean('Email g.n.i.')
	secretary = fields.Char('Secretaria', size=60)
	secretary_email = fields.Char('Secr. email', size=80)
	secretary_email_exclude = fields.Boolean('Secr. email excluir')
	secretary_email_gracias = fields.Boolean('Secr. email g.n.i.')
	personal_email = fields.Char('Email personal', size=80)
	personal_email_exclude = fields.Boolean('Pers. email excluir')
	personal_email_gracias = fields.Boolean('Pers. email g.n.i.')
	secretary_personal_email = fields.Char('Secr. email personal', size=80)
	secretary_personal_email_exclude = fields.Boolean('Secr. email pers. excluir')
	secretary_personal_email_gracias = fields.Boolean('Secr. email pers. g.n.i.')
	secretary_phone = fields.Char('Telefono secretaria', size=40)
	secretary_mobile = fields.Char('Telefono movil secre.', size=40)
	other_phones = fields.Char('Telefonos', size=40)
	direct_phone = fields.Char('Telf. directo', size=40)
	business_line = fields.Char('Giro', size=80)
	common_name = fields.Char('Nombre común', size=60)
	regular_customer = fields.Boolean('Cliente habitual')
	activities = fields.Many2many('sead.activity.child', 'activity_parter_rel', 'partner_rel_id', 'activ_rel_id', 'Actividades')
	events = fields.Many2many('event.event', 'event_parter_rel', 'partner_rel_id', 'event_rel_id', 'Events')
	seller_1 = fields.Many2one('res.users', 'Vendedor equipo 1')
	seller_2 = fields.Many2one('res.users', 'Vendedor equipo 2')
	seller_3 = fields.Many2one('res.users', 'Vendedor equipo 3')
	seller_sponsors = fields.Many2one('res.users', 'Vendedor auspicios')
	bd_user = fields.Many2one('res.users', 'Responsable BD')
	compatible_code = fields.Char('Codigo compatible', size=20)
	hierarchy_level = fields.Selection((('1', 'Nivel1'), ('2', 'Nivel 2'), ('3', 'Nivel 3'), ('4', 'Nivel 4'), ('5', 'Nivel 5'), ('6', 'Nivel 6'), ('7', 'Nivel 7')), 'Nivel jerárquico')
	gender = fields.Selection((('M', 'Masculino'), ('F', 'Femenino')), 'Género')
	gender_suffix = fields.Char(compute='_compute_sufijo_genero')
	ejec_codigo = fields.Char('ejec_codigo', size = 20)
	semi_fecha_creacion = fields.Date('fecha de creacion')
	semi_fecha_cambio = fields.Date('fecha de cambio')
	semi_fecha_modificacion = fields.Date('fecha de actualizacion')
	semi_usuario_creacion = fields.Many2one('res.users', 'Usuario creacion')
	semi_usuario_modificacion = fields.Many2one('res.users', 'Usuario actualizacion')
	semi_usuario_cambio = fields.Many2one('res.users', 'Usuario cambio')
	mailing_ids = fields.Many2many('mail.mass_mailing')
	rank_position = fields.Integer('Ranking posicion')
	rank_points = fields.Integer('Ranking puntos')

	@api.depends('gender')
	def _compute_sufijo_genero(self):
		# Let's initialize the field with some default value
		# Otherwise it'll throw an error 'field is accessed before assign'
		for record in self:
			record.gender_suffix = 'o'
			if record.gender == 'F':
				record.gender_suffix = 'a'	

	@api.one
	def write(self, values):
		# deberemos copiar algunos campos a los cargos
		cambio_de_actividades = values.get('activities', False)
		if (not self.is_company):
			# es un cargo
			if (not cambio_de_actividades):
				# no está grabando actividades
				# veamos si ya tenía
				if self.activities == False:
					# no tenía actividades
					# vamos a jalar las de la empresa
					valor = []
					activs =self.parent_id.activities
					for activ in activs:
						valor = valor + [activ.id]
					values['activities'] = [[6, 0, valor]]

		result = super(res_partner_extension, self).write(values)

		# si es una empresa y ha tenido cambios en actividades, debemos actualizar los empleados
		#if (self.is_company and cambio_de_actividades):
		if self.is_company:
			self.update_childs()

		return result

	@api.one
	def update_childs(self):

		if self.seller_1:
			s1 = self.seller_1.id
		else:
			s1 = False

		if self.seller_2:
			s2 = self.seller_2.id
		else:
			s2 = False

		if self.seller_3:
			s3 = self.seller_3.id
		else:
			s3 = False

		if self.seller_sponsors:
			ss = self.seller_sponsors.id
		else:
			ss = False

		valor = []
		activs = self.activities
		for activ in activs:
			valor = valor + [activ.id]

		for child in self.child_ids:
			child.write({'activities':  [[6, 0, valor]]})
			child.write({'seller_1': s1})
			child.write({'seller_2': s2})
			child.write({'seller_3': s3})
			child.write({'seller_sponsors': ss})

		return True


	@api.multi
	def get_mass_emails(self):
		result = []
		if (self.email_exclude == False) and (self.email_gracias  == False) and (self.email != False):
			result = result + [self.email]

		if (self.personal_email_exclude == False) and (self.personal_email_gracias == False) and (self.personal_email != False):
			result = result + [self.personal_email]

		if (self.secretary_email_exclude == False) and (self.secretary_email_gracias == False) and (self.secretary_email != False):
			result = result + [self.secretary_email]

		if (self.secretary_personal_email_exclude == False) and (self.secretary_personal_email_gracias == False) and (self.secretary_personal_email != False):
			result = result + [self.secretary_personal_email]

		return result
		

	@api.multi
	def get_all_emails(self):
		result = []
		if self.email != False:
			result = result + [self.email]

		if self.personal_email != False:
			result = result + [self.personal_email]

		if self.secretary_email != False:
			result = result + [self.secretary_email]

		if self.secretary_personal_email != False:
			result = result + [self.secretary_personal_email]

		return result


	@api.multi
	def do_register_verification(self):
		self.semi_fecha_modificacion = datetime.datetime.today()
		self.semi_usuario_modificacion = self.env.user
		return True

	@api.multi
	def get_company_report(self):
		return {
			'type' : 'ir.actions.act_url',
			'url': '/web/binary/download_document?model=res.partner&field=name&id=%s&filename=ficha_partner.html'%(self.id),
			'target': 'self',
		}

	# cambios GL para incluir provincia y distrito en los campos - 12/02/2016
	# esta funcion recaba los campos que se debe copiar de la empresa a los ejecutivos cuando se indica use_company_address
	def _address_fields(self, cr, uid, context=None):
		address_fields = super(res_partner_extension, self)._address_fields(cr, uid, context=context)
		return list(address_fields + ['province_id', 'district_id'])		
