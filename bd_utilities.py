# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.osv import osv
from openerp import tools


class bd_utilities_seller_change_wizard(osv.TransientModel):
	_name = 'sead.bd_utilities.seller_change_wizard'
	seller_source = fields.Many2one('res.users', 'Vendedor saliente')
	seller_target = fields.Many2one('res.users', 'Vendedor entrante')
	team_to_change = fields.Selection((('1', 'Vendedor 1'), ('2', 'Vendedor 2'), ('3', 'Vendedor 3')), 'Equipo a cambiar')

	@api.one
	def do_change(self):
		# called by button defined in view.xml
		# self represents one record (api.one)
		# self.is_done = not self.is_done
		# must return something for XMLRPC
		if (self.team_to_change != False) and (self.seller_source.id != False) and (self.seller_target.id != False):
			partner_obj = self.env['res.partner']
			source_id = self.seller_source.id
			target_id = self.seller_target.id

			# definiremos el team a cambiar
			if self.team_to_change == '1':
				seller_team = 'seller_1'
			if self.team_to_change == '2':
				seller_team = 'seller_2'
			if self.team_to_change == '3':
				seller_team = 'seller_3'

			# no vamos a usar partner.update_childs() por ser muy lento y dar timeout

			partners = partner_obj.search([(seller_team, '=', source_id), ('customer', '=', True)])
			for partner in partners:
				partner_id = partner.id
				partner.write({seller_team:  target_id})
				self.env.cr.execute('UPDATE res_partner SET ' + seller_team + ' = ' + str(target_id) + 'where company_id = ' + str(partner_id) + ' and is_company = False')

			return True	
		else:
			raise osv.except_osv(("Error!"), (" Para porceder debe seleccionar equipo, vendedor saliente y vendedor entrante!"))
			return False


class bd_utilities_seller_redistribution_wizard(osv.TransientModel):
	_name = 'sead.bd_utilities.seller_redistribution_wizard'
	seller_source = fields.Many2one('res.users', 'Vendedor saliente')
	seller_target1 = fields.Many2one('res.users', 'Vendedor entrante 1')
	seller_target2 = fields.Many2one('res.users', 'Vendedor entrante 2')
	seller_target3 = fields.Many2one('res.users', 'Vendedor entrante 3')
	seller_target4 = fields.Many2one('res.users', 'Vendedor entrante 4')
	seller_target5 = fields.Many2one('res.users', 'Vendedor entrante 5')
	seller_target6 = fields.Many2one('res.users', 'Vendedor entrante 6')
	team_to_change = fields.Selection((('1', 'Vendedor 1'), ('2', 'Vendedor 2'), ('3', 'Vendedor 3')), 'Equipo a cambiar')

	@api.one
	def do_change(self):
		# called by button defined in view.xml
		# self represents one record (api.one)
		#self.is_done = not self.is_done
		# must return something for XMLRPC
		if (self.team_to_change != False) and (self.seller_source.id != False) and (self.seller_target1.id != False):
			if (self.seller_target2.id != False):

				# armaremos una lista con las vendedoras
				vendedoras = []
				if self.seller_target1.id != False:
					vendedoras = vendedoras + [self.seller_target1.id]
				if self.seller_target2.id != False:
					vendedoras = vendedoras + [self.seller_target2.id]
				if self.seller_target3.id != False:
					vendedoras = vendedoras + [self.seller_target3.id]
				if self.seller_target4.id != False:
					vendedoras = vendedoras + [self.seller_target4.id]
				if self.seller_target5.id != False:
					vendedoras = vendedoras + [self.seller_target5.id]
				if self.seller_target6.id != False:
					vendedoras = vendedoras + [self.seller_target6.id]

				# definiremos el team a cambiar
				if self.team_to_change == '1':
					seller_team = 'seller_1'
				if self.team_to_change == '2':
					seller_team = 'seller_2'
				if self.team_to_change == '3':
					seller_team = 'seller_3'

				# obtenemos el id a cambiar
				source_id = self.seller_source.id

				# recuperemos la seleccion
				self.env.cr.execute('SELECT id, name FROM res_partner where ' + seller_team + ' = ' + str(source_id) + ' and is_company = True and customer = true order by rank_points desc')
				seleccion = self.env.cr.fetchall()

				# obtengamos el objeto partner
				partner_obj = self.env['res.partner']

				# realicemos el cambio
				vend_position = 0
				vend_direction = 1

				for partner in seleccion:
					target_id = vendedoras[vend_position]
					partner_id = partner[0]
					partner_name = partner[1]
					# buscamos el partner
					partners = partner_obj.search([('id', '=', partner_id)])
					if len(partners) > 0:
						partner = partners[0]
					else:
						osv.except_osv(("Error inesperado!"), (" Se ha producido un error inesperado. Favor avisar a sistemas. Código = bdu01"))
					# ejecutamos
					partner.write({seller_team:  target_id})
					self.env.cr.execute('UPDATE res_partner SET ' + seller_team + ' = ' + str(target_id) + 'where company_id = ' + str(partner_id) + ' and is_company = False')
					# preparamos el siguiente
					vend_position = vend_position + vend_direction
					if vend_position >= len(vendedoras):
						vend_position = len(vendedoras) - 1
						vend_direction = -1
					if vend_position < 0:
						vend_position = 0
						vend_direction = 1

				return True
			else:
				raise osv.except_osv(("Error!"), (" Debe seleccionar por lo menos dos vendedores entrantes!"))
				return False				
		else:
			raise osv.except_osv(("Error!"), (" Para proceder debe seleccionar equipo, vendedor saliente y por lo menos dos vendedores entrantes!"))
			return False


class bd_utilities_seller_null_distribution_wizard(osv.TransientModel):
	_name = 'sead.bd_utilities.seller_null_distribution_wizard'
	seller_target1 = fields.Many2one('res.users', 'Vendedor entrante 1')
	seller_target2 = fields.Many2one('res.users', 'Vendedor entrante 2')
	seller_target3 = fields.Many2one('res.users', 'Vendedor entrante 3')
	seller_target4 = fields.Many2one('res.users', 'Vendedor entrante 4')
	seller_target5 = fields.Many2one('res.users', 'Vendedor entrante 5')
	seller_target6 = fields.Many2one('res.users', 'Vendedor entrante 6')
	team_to_change = fields.Selection((('1', 'Vendedor 1'), ('2', 'Vendedor 2'), ('3', 'Vendedor 3')), 'Equipo a cambiar')

	@api.one
	def do_change(self):
		# called by button defined in view.xml
		# self represents one record (api.one)
		#self.is_done = not self.is_done
		# must return something for XMLRPC
		if (self.team_to_change != False) and (self.seller_target1.id != False):
			if (self.seller_target2.id != False):

				# armaremos una lista con las vendedoras
				vendedoras = []
				if self.seller_target1.id != False:
					vendedoras = vendedoras + [self.seller_target1.id]
				if self.seller_target2.id != False:
					vendedoras = vendedoras + [self.seller_target2.id]
				if self.seller_target3.id != False:
					vendedoras = vendedoras + [self.seller_target3.id]
				if self.seller_target4.id != False:
					vendedoras = vendedoras + [self.seller_target4.id]
				if self.seller_target5.id != False:
					vendedoras = vendedoras + [self.seller_target5.id]
				if self.seller_target6.id != False:
					vendedoras = vendedoras + [self.seller_target6.id]

				# definiremos el team a cambiar
				if self.team_to_change == '1':
					seller_team = 'seller_1'
				if self.team_to_change == '2':
					seller_team = 'seller_2'
				if self.team_to_change == '3':
					seller_team = 'seller_3'

				# recuperemos la seleccion
				self.env.cr.execute('SELECT id, name FROM res_partner where ' + seller_team + ' is null and is_company = True and customer = true order by rank_points desc')

				seleccion = self.env.cr.fetchall()

				# obtengamos el objeto partner
				partner_obj = self.env['res.partner']

				# realicemos el cambio
				vend_position = 0
				vend_direction = 1

				for partner in seleccion:
					target_id = vendedoras[vend_position]
					partner_id = partner[0]
					partner_name = partner[1]
					# buscamos el partner
					partners = partner_obj.search([('id', '=', partner_id)])
					if len(partners) > 0:
						partner = partners[0]
					else:
						osv.except_osv(("Error inesperado!"), (" Se ha producido un error inesperado. Favor avisar a sistemas. Código = bdu02"))
					# ejecutamos
					partner.write({seller_team:  target_id})
					self.env.cr.execute('UPDATE res_partner SET ' + seller_team + ' = ' + str(target_id) + 'where company_id = ' + str(partner_id) + ' and is_company = False')
					# preparamos el siguiente
					vend_position = vend_position + vend_direction
					if vend_position >= len(vendedoras):
						vend_position = len(vendedoras) - 1
						vend_direction = -1
					if vend_position < 0:
						vend_position = 0
						vend_direction = 1

				return True
			else:
				raise osv.except_osv(("Error!"), (" Debe seleccionar por lo menos dos vendedores entrantes!"))
				return False				
		else:
			raise osv.except_osv(("Error!"), (" Para proceder debe seleccionar equipo y por lo menos dos vendedores entrantes!"))
			return False
