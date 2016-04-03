# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.osv import osv

from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import serialize_exception,content_disposition


def Ordenar_Lista(UnaLista, UnCampo, UnOrden):
	for x in range(0, len(UnaLista)):
		for y in range(x, len(UnaLista)):
			if UnOrden == 'A':
				if UnaLista[x][UnCampo] > UnaLista[y][UnCampo]:
					UnaLista[x], UnaLista[y] = UnaLista[y], UnaLista[x]
			else:
				if UnaLista[x][UnCampo] < UnaLista[y][UnCampo]:
					UnaLista[x], UnaLista[y] = UnaLista[y], UnaLista[x]


def prep_csv(UnTexto):
	if "," in UnTexto:
		result = '"' + UnTexto + '"'
	else:
		if (len(UnTexto) > 0) and (UnTexto[0] == '"') and (UnTexto[len(UnTexto) - 1] != '"'):
			result = '"' + UnTexto + '"'
		else:
			result = UnTexto
	return result

def prep_barras(UnTexto):
	result = '[[' + UnTexto + ']]'
	return result


# http://www.emiprotechnologies.com/technical_notes/odoo-technical-notes-59/post/how-to-download-any-file-on-button-click-244
class Export_event_registration_gafetes(http.Controller):
	@http.route('/web/binary/download_event_registration_gafetes', type='http', auth="public")
	@serialize_exception

	def download_document(self,model,field,id,filename=None, **kw):
		print('----------------- download_document ------------------')
		registration_id = id
		wizard_obj = request.registry['event.export_registration']
		wizards = wizard_obj.read(request.cr, request.uid, [int(registration_id)], ['registration_ids'], context=None)		
		wizard = wizards[0]
		registration_ids = wizard['registration_ids']
		print('----')
		print(registration_ids)
		Model = request.registry[model]

		# vamos a jalar los registros
		registration_obj = request.registry['event.registration']
		registrations = registration_obj.read(request.cr, request.uid, registration_ids, 
			['id', 'name', 'display_name', 'partner_id', 'partner_function', 'credential_printed', 'state'], context=None)

		# iniciemos un objeto partner para busquedas
		partner_obj = request.registry['res.partner']

		# cabeceras
		fc = ''
		for registration in registrations:
			if (not (registration['credential_printed'])) and (registration['state'] != 'cancel'):
				# si el partner_id corresponde a un ejecutivo, podemos extraer sus nombres y apellidos
				partner = partner_obj.read(request.cr, request.uid, registration['partner_id'][0], 
					['is_company', 'name', 'names', 'last_name', 'mother_name', 'gender_suffix', 'title', 'parent_id'], context=None)
				if partner['is_company']:
					# no tenemos un ejecutivo en la BD, solamente lo escrito en el registro
					names = registration['name'] if registration['name'] else ""
					apellido_p = ''
					apellido_m = ''
					cargo = registration['partner_function'] if registration['partner_function'] else ""
					company = partner['name']
				else:
					# es un ejecutivo de la BD, tenemos sus datos desagregados
					names = partner['names'] if partner['names'] else ""
					apellido_p = partner['last_name'] if partner['last_name'] else ""
					apellido_m = partner['mother_name'] if partner['mother_name'] else ""
					cargo = registration['partner_function'] if registration['partner_function'] else ""
					company = partner['parent_id'][1]
				
				fc = fc + prep_barras(names) + prep_barras(apellido_p) + prep_barras(apellido_m) +  prep_barras(cargo) + prep_barras(company) + '\n'

		if not fc:
			print('not fc')
			return request.not_found()
		else:
			print(' si fc')
			print(filename)
			if not filename:
					print('not filename')
					filename = '%s_%s' % (model.replace('.', '_'), id)
			return request.make_response(fc,
				#[('Content-Type', 'application/octet-stream'),('Content-Disposition', content_disposition(filename))])  
				[('Content-Type', 'application/octet-stream;charset=utf-8'),('Content-Disposition', content_disposition(filename))])  

