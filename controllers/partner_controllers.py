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


# http://www.emiprotechnologies.com/technical_notes/odoo-technical-notes-59/post/how-to-download-any-file-on-button-click-244
class Ficha_Partner(http.Controller):
	@http.route('/web/binary/download_document', type='http', auth="public")
	@serialize_exception

	def download_document(self,model,field,id,filename=None, **kw):
		partner_id = id
		partner_obj = request.registry['res.partner']
		partners = partner_obj.read(request.cr, request.uid, [int(partner_id)], ['name','vat', 'common_name', 'activities', 'child_ids'], context=None)		
		partner = partners[0]

		Model = request.registry[model]

		# cabeceras
		fc = ''
		fc = fc + '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">' + '\n'
		fc = fc + '<html>' + '\n'
		fc = fc + '<head>' + '\n'
		#fc = fc + '	<meta content="text/html; charset=ISO-8859-1" http-equiv="content-type">' + '\n'
		fc = fc + '	<meta http-equiv="content-type" content="text/html; charset=utf-8"/>' + '\n'		
		fc = fc + '	<title>Ficha de empresa</title>' + '\n'
		fc = fc + '</head>' + '\n'
		fc = fc + '<body>' + '\n'

		# la empresa
		if partner['vat']:
			empr_ruc = partner['vat']
		else:
			empr_ruc = ''

		if partner['common_name']:
			empr_common_name = partner['common_name']
		else:
			empr_common_name = ''

		fc = fc + '	<big><span style="font-weight: bold;">' + partner['name'] + '</span></big>' + '\n'
		fc = fc + '	<small><br style="font-family: Helvetica,Arial,sans-serif;">RUC: ' + empr_ruc + '\n'
		fc = fc + '	<br style="font-family: Helvetica,Arial,sans-serif;">Nombre comun: ' + empr_common_name + '\n'
		fc = fc + '	<br style="font-family: Helvetica,Arial,sans-serif;">Actividades:' + '\n'

		activities_obj = request.registry['sead.activity.child']
		activities = activities_obj.read(request.cr, request.uid, partner['activities'], ['name'], context=None)	
		for activity in activities:
			fc = fc + '<br style="font-family: Helvetica,Arial,sans-serif;">' + activity['name'] + '<br>' + '\n'

		fc = fc + '<br></small>'

		# los ejecutivos
		childs = partner_obj.read(request.cr, request.uid, partner['child_ids'], 
			['name','vat', 'function', 'business_area', 'hierarchy_level', 'street', 'email', 'direct_phone', 'secretary', 'semi_fecha_modificacion', 'state_id', 'province_id', 'district_id', 'gender_suffix'], context=None)
		Ordenar_Lista(childs, 'hierarchy_level', 'A')

		for child in childs:
			cargo_email = child['email'] if child['email'] else ""
			cargo_direct_phone = child['direct_phone'] if child['direct_phone'] else ""
			cargo_secretaria = child['secretary'] if child['secretary'] else ""
			cargo_cargo = child['function'] if child['function'] else ""
			cargo_area = child['business_area'][1] if child['business_area'] else ""
			cargo_nivel = child['hierarchy_level'] if child['hierarchy_level'] else ""
			cargo_modif = child['semi_fecha_modificacion'] if child['semi_fecha_modificacion'] else ""
			state = child['state_id'][1] if child['state_id'] else ""
			province = child['province_id'][1] if child['province_id'] else ""
			district = child['district_id'][1] if child['district_id'] else ""

			td_start = '<td style="font-family: Helvetica,Arial,sans-serif;"><small>'
			td_close = '</small></td>'

			fc = fc + '	<hr style="width: 100%; height: 2px;">' + '\n'
			fc = fc + '	<table style="text-align: left; width: 100%;" border="0" cellpadding="0" cellspacing="2">' + '\n'
			fc = fc + '		<tbody>' + '\n'
			fc = fc + ' 		<tr>' + '\n'
			fc = fc + ' 			' + td_start + 'Cargo: ' + cargo_cargo + td_close + '\n'
			#fc = fc + ' 			' + td_start + 'Nombre: ' + child['name'].decode('utf-8') + td_close + '\n'
			fc = fc + ' 			' + td_start + 'Nombre: ' + child['name'] + td_close + '\n'
			fc = fc + ' 		</tr>' + '\n'
			fc = fc + '			<tr>' + '\n'
			fc = fc + '				' + td_start + 'Area: ' + cargo_area + td_close + '\n'
			fc = fc + '				' + td_start + 'Nivel: ' + cargo_nivel + td_close + '\n'
			fc = fc + '			</tr>' + '\n'
			fc = fc + '			<tr>' + '\n'
			fc = fc + '				' + td_start + 'Direccion: ' + child['street'] + td_close + '\n'
			fc = fc + '				' + td_start + state + ' / ' + province + ' / ' + district + td_close + '\n'
			fc = fc + '			</tr>' + '\n'
			fc = fc + '			<tr>' + '\n'
			fc = fc + '				' + td_start + 'eMail: ' + cargo_email + td_close + '\n'
			fc = fc + '				' + td_start + 'Telefono directo: ' + cargo_direct_phone + td_close + '\n'
			fc = fc + '			</tr>' + '\n'
			fc = fc + '			<tr>' + '\n'
			fc = fc + '				' + td_start + 'Secretaria: ' + cargo_secretaria + td_close + '\n'
			fc = fc + '				' + td_start + td_close + '\n'
			fc = fc + '			</tr>' + '\n'
			fc = fc + '			<tr>' + '\n'
			fc = fc + '				' + td_start + 'Ultima actualizacion: ' + cargo_modif + td_close + '\n'
			fc = fc + '				' + td_start + '</td>' + '\n'
			fc = fc + '			</tr>' + '\n'
			fc = fc + '		</tbody>' + '\n'
			fc = fc + '	</table>' + '\n'
			fc = fc + '	<br>' + '\n'

		fc = fc + '</body></html>'


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
				[('Content-Type', 'application/octet-stream'),('Content-Disposition', content_disposition(filename))])  

def prep_csv(UnTexto):
	if "," in UnTexto:
		result = '"' + UnTexto + '"'
	else:
		if (len(UnTexto) > 0) and (UnTexto[0] == '"') and (UnTexto[len(UnTexto) - 1] != '"'):
			result = '"' + UnTexto + '"'
		else:
			result = UnTexto
	return result

class Export_Partner(http.Controller):
	@http.route('/web/binary/download_document2', type='http', auth="public")
	@serialize_exception

	def download_document(self,model,field,id,filename=None, **kw):
		print('----------------- download_document ------------------')
		partner_id = id
		wizard_obj = request.registry['mail.mass_mailing.wizard']
		wizards = wizard_obj.read(request.cr, request.uid, [int(partner_id)], ['partner_ids','mailing_id'], context=None)		
		wizard = wizards[0]
		partner_ids = wizard['partner_ids']
		print('----')
		print(partner_ids)
		Model = request.registry[model]

		partner_obj = request.registry['res.partner']
		# los ejecutivos
		partners = partner_obj.read(request.cr, request.uid, partner_ids, 
			['is_company', 'name', 'street', 'state_id', 'province_id', 'district_id'], context=None)

		# cabeceras
		fc = ''
		for partner in partners:
			if partner['is_company'] == False:
				name = partner['name'] if partner['name'] else ""
				street = partner['street'] if partner['street'] else ""
				state = partner['state_id'][1] if partner['state_id'] else ""
				province = partner['province_id'][1] if partner['province_id'] else ""
				district = partner['district_id'][1] if partner['district_id'] else ""
				fc = fc + prep_csv(name) +  ',' + prep_csv(street) + ',' + prep_csv(district) + ',' + prep_csv(province) + ',' + prep_csv(state) + '\n'

		#test = 'Ramírez'
		#udata = test.decode("utf-8")
		#asciidata = udata.encode("ascii","ignore")
		# ANSI ???????
		#fc = udata

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


class Export_Partner_mailing(http.Controller):
	@http.route('/web/binary/download_document_mailing', type='http', auth="public")
	@serialize_exception

	def download_document(self,model,field,id,filename=None, **kw):
		print('----------------- download_document ------------------')
		partner_id = id
		wizard_obj = request.registry['mail.mass_export_partner']
		wizards = wizard_obj.read(request.cr, request.uid, [int(partner_id)], ['partner_ids'], context=None)		
		wizard = wizards[0]
		partner_ids = wizard['partner_ids']
		print('----')
		print(partner_ids)
		Model = request.registry[model]

		activities_obj = request.registry['sead.activity.child']

		partner_obj = request.registry['res.partner']
		# los ejecutivos
		partners = partner_obj.read(request.cr, request.uid, partner_ids, 
			['is_company', 'name', 'names', 'last_name', 'gender_suffix', 'title', 
			'email', 'email_exclude', 'email_gracias', 
			'personal_email', 'personal_email_exclude', 'personal_email_gracias',
			'secretary_email', 'secretary_email_exclude', 'secretary_email_gracias', 
			'secretary_personal_email', 'secretary_personal_email_exclude', 'secretary_personal_email_gracias',
			'hierarchy_level', 'function', 'business_area', 'activities', 'parent_id'], context=None)

		# cabeceras
		fc = ''
		for partner in partners:
			if partner['is_company'] == False:
				name = partner['name'] if partner['name'] else ""
				names = partner['names'] if partner['names'] else ""
				last_name = partner['last_name'] if partner['last_name'] else ""
				suffix = partner['gender_suffix'] if partner['gender_suffix'] else "o"
				estimado = 'Estimad' + suffix
				nivel = prep_csv(partner['hierarchy_level'] if partner['hierarchy_level'] else "")
				cargo = prep_csv(partner['function'] if partner['function'] else "")
				area =  prep_csv(partner['business_area'][1] if partner['business_area'] else "")
				title = partner['title'][1] if partner['title'] else ""
				empresa = partner['parent_id'][1] if partner['parent_id'] else ""
				actividades = ''
				for actividad_id in partner['activities']:
					act = activities_obj.read(request.cr, request.uid, actividad_id, ['name'], context=None)
					if (actividades != ''):
						actividades = actividades + ' - '
					actividades = actividades + act['name']

				emails = []
				if (partner['email_exclude'] == False) and (partner['email_gracias']  == False) and (partner['email'] != False):
					emails = emails + [partner['email']]

				if (partner['personal_email_exclude'] == False) and (partner['personal_email_gracias'] == False) and (partner['personal_email'] != False):
					emails = emails + [partner['personal_email']]

				if (partner['secretary_email_exclude'] == False) and (partner['secretary_email_gracias'] == False) and (partner['secretary_email'] != False):
					emails = emails + [partner['secretary_email']]

				if (partner['secretary_personal_email_exclude'] == False) and (partner['secretary_personal_email_gracias'] == False) and (partner['secretary_personal_email'] != False):
					emails = emails + [partner['secretary_personal_email']]

				emails_text = ''
				for email in emails:
				    if len(emails_text) == 0:
				        emails_text = emails_text + email
				    else:
				        emails_text = emails_text + ';' + email
				email = ''
				if len(emails) > 0:
					email = emails[0]

				fc = fc + prep_csv(email) + ',' +  prep_csv(estimado) + ',' + prep_csv(title) +  ',' + prep_csv(names)+  ',' + prep_csv(last_name) +  ',' + prep_csv(suffix) + ',' + prep_csv(emails_text) +  ',' 
				fc = fc + cargo + ',' + area + ',' + nivel + ',' + prep_csv(name) + ',' + prep_csv(empresa) + ',' + prep_csv(actividades) + '\n'

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


class Export_Partner_etiquetas(http.Controller):
	@http.route('/web/binary/download_document_etiquetas', type='http', auth="public")
	@serialize_exception

	def download_document(self,model,field,id,filename=None, **kw):
		print('----------------- download_document ------------------')
		partner_id = id
		wizard_obj = request.registry['mail.mass_export_partner']
		wizards = wizard_obj.read(request.cr, request.uid, [int(partner_id)], ['partner_ids'], context=None)		
		wizard = wizards[0]
		partner_ids = wizard['partner_ids']
		print('----')
		print(partner_ids)
		Model = request.registry[model]

		partner_obj = request.registry['res.partner']
		# los ejecutivos
		partners = partner_obj.read(request.cr, request.uid, partner_ids, 
			['is_company', 'name', 'names', 'last_name', 'mother_name', 'gender', 'gender_suffix', 'title', 'function', 
			'street', 'state_id', 'province_id', 'district_id', 'parent_id'], context=None)

		# cabeceras
		fc = ''
		for partner in partners:
			if partner['is_company'] == False:
				name = partner['name'] if partner['name'] else ""
				names = partner['names'] if partner['names'] else ""
				last_name = partner['last_name'] if partner['last_name'] else ""
				mother_name = partner['mother_name'] if partner['mother_name'] else ""
				function = partner['function'] if partner['function'] else ""
				suffix = partner['gender_suffix'] if partner['gender_suffix'] else "o"
				gender = partner['gender'] if partner['gender'] else ""
				estimado = 'Estimad' + suffix
				title = partner['title'][1] if partner['title'] else ""
				street = partner['street'] if partner['street'] else ""
				state = partner['state_id'][1] if partner['state_id'] else ""
				province = partner['province_id'][1] if partner['province_id'] else ""
				district = partner['district_id'][1] if partner['district_id'] else ""
				empresa = partner['parent_id'][1] if partner['parent_id'] else ""

				fc = fc + prep_csv(empresa)+  ',' + prep_csv(names) +  ',' + prep_csv(last_name)+  ',' + prep_csv(mother_name) +  ',' + prep_csv(function) + ',' + prep_csv(street) + ',' + prep_csv(district) + ',' + prep_csv(province) + ',' + prep_csv(state) +  ',' + prep_csv(estimado) +  ',' + prep_csv(name) +  ',' + prep_csv(title)+  ',' + prep_csv(suffix) + '\n'

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