# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.osv import osv

from openerp import tools
import base64
import re
import StringIO
import pyqrcode
import pdfkit


class event_registration_extension(models.Model):
	# event.py
	_inherit = 'event.registration'
	# when _name is not explicitly set, implicitly it is the same as the original
	partner_function = fields.Char('Cargo')
	registration_type = fields.Selection((('V', 'Venta'), ('A', 'Auspicio'), ('I', 'Invitado'), ('C', 'Canje')), default = 'V', string = 'Tipo de cupo')
	registration_days = fields.Selection((('C', 'Evento completo'), ('1', 'Dia 1'), ('2', 'Dia 2'), ('3', 'Dia 3')), default = 'C', string = 'Dias')


	# esto divide un registro múltiple en registros individuales
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


	# copiado de sale.py: def action_quotation_send(self, cr, uid, ids, context=None):
	# abrirá una ventana de redacción de correo para un registro de evento
	def prepare_eticket(self, cr, uid, ids, context=None):
		'''
		This function opens a window to compose an email, with the edi sale template message loaded by default
		'''
		assert len(ids) == 1, 'This option should only be used for a single id at a time.'
		ir_model_data = self.pool.get('ir.model.data')
		#try:
		#    template_id = ir_model_data.get_object_reference(cr, uid, 'sale', 'email_template_edi_sale')[1]
		#except ValueError:
		#    template_id = False
		template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False 
		ctx = dict()

		ctx.update({
			'default_model': 'event.registration',
			'default_res_id': ids[0],
			'default_use_template': bool(template_id),
			'default_template_id': template_id,
			'default_composition_mode': 'comment',
			'include_eticket': True,
			'mark_so_as_sent': True
		})
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(compose_form_id, 'form')],
			'view_id': compose_form_id,
			'target': 'new',
			'context': ctx,
		}


	def generate_QRcode(self, text, escala):
		qr = pyqrcode.create(text)
		output = StringIO.StringIO()
		qr.png(output, scale=escala)
		result = output.getvalue().encode('base64')
		# se devuelve un PNG codificado en base64
		return result


	# crea el código QR y lo pone como attachment
	@api.multi
	def create_QRcode(self, text):
		file_name = re.sub(r'[^a-zA-Z0-9_-]', '_', 'Codigo_QR')
		file_name += ".png"
		attachment_obj = self.env['ir.attachment']

		# si ya existía el adjunto, lo eliminamos
		attachs = attachment_obj.search([('res_id', '=', self.id), ('res_model', '=', self._name), ('datas_fname', '=', file_name)])
		if len(attachs) > 0:
			# debemos eliminar los anteriores
			for attach in attachs:
				attach.unlink()

		result = self.generate_QRcode(text, 15)

		attachment_id = attachment_obj.create(
			{
				'name': file_name,
				'datas': result,
				'datas_fname': file_name,
				'res_model': self._name,
				'res_id': self.id,
				'type': 'binary'
			})
		return True

	# crea el eticket completo y lo agrega como attachment
	@api.multi
	def create_eticket(self):
		# obtenemos el objeto con la nueva API !!
		attachment_obj = self.env['ir.attachment']
		nombre_asistente = self.name.encode('ascii')
		nombre_evento = self.event_id.name		
		file_name = 'eticket'
		label_codigo = str(self.id)
		label_TC = ''
		label_dia1 = ''
		label_dia2 = ''
		label_dia3 = ''

		# veremos si ya hay eTickets adjuntos
		attachs = attachment_obj.search([('res_id', '=', self.id), ('res_model', '=', self._name), ('datas_fname', 'like', file_name)])
		if len(attachs) > 0:
			# debemos eliminar los anteriores
			for attach in attachs:
				attach.unlink()

		# nombramos el archivo segun el tipo de cupo por dias
		if (self.registration_days == False)  or (self.registration_days == 'C'):
			file_name += '_completo'
			label_TC = '<TC>COMPLETO</TC>'
			label_dia1 = '<D1>SI</D1>'
			label_dia2 = '<D2>SI</D2>'
			label_dia3 = '<D3>SI</D3>'
		if self.registration_days == "1":
			file_name += '_dia1'
			label_TC = '<TC>DIA 1</TC>'
			label_dia1 = '<D1>SI</D1>'
			label_dia2 = '<D2>NO</D2>'
			label_dia3 = '<D3>NO</D3>'
		if self.registration_days == "2":
			file_name += '_dia2'
			label_TC = '<TC>DIA 2</TC>'
			label_dia1 = '<D1>NO</D1>'
			label_dia2 = '<D2>SI</D2>'
			label_dia3 = '<D3>NO</D3>'
		if self.registration_days == "3":
			file_name += '_dia3'
			label_TC = '<TC>DIA 3</TC>'
			label_dia1 = '<D1>NO</D1>'
			label_dia2 = '<D2>NO</D2>'
			label_dia3 = '<D3>SI</D3>'			
		file_name += '.html'

		label_QR = '<CD>' + label_codigo + '</CD>\n' + '<NM>'+ nombre_asistente + '</NM>\n' + label_TC + "\n" + label_dia1 +"\n" + label_dia2 +"\n" + label_dia3 

		# buscamos el eTicket correspondiente en los adjuntos del evento
		attachs = attachment_obj.search([('res_id', '=', self.event_id.id), ('res_model', '=', 'event.event'), ('datas_fname', '=', file_name)])
		if len(attachs) == 0:
			# el evento no tiene eTicket!! tenemos que avisar
			raise osv.except_osv(("ERROR!"), (" El evento no tiene el eTicket adjunto (" + file_name + ")."))
		else:
			# el evento tiene el eTicket, vamos a copiarlo
			# tomamos sus datos y reemplazamos el nombre
			# sys.getdefaultencoding() indica que usamos ascii

			attach = attachment_obj.browse(attachs[0].id)
			nuevo_texto = attach.datas.decode('base64')
			# decode(): Gets you from bytes -> Unicode
			nuevo_texto = nuevo_texto.replace('XXXXXXXXXXXXXXXX', nombre_asistente)

			# ahora vamos a insertar el codigo QR
			texto_imagen = '<img src="data:image/png;base64,' + self.generate_QRcode(label_QR, 2.4) + '" alt="QR.png">'
			raw_text = nuevo_texto.replace('ZZZZZZZZZZZZZZZZ', texto_imagen)
			# ya tenemos el HTML listo!

			incluir_html = False
			if incluir_html:
				nuevo_texto = raw_text.encode('base64')
				# creamos el attach del html en el registro
				attachment_id = attachment_obj.create(
					{
						'name': file_name,
						'datas': nuevo_texto,
						'datas_fname': file_name,
						'res_model': self._name,
						'res_id': self.id,
						'type': 'binary'
		            })

			pdftext = pdfkit.from_string(raw_text.decode('utf-8'), False)
			pdftext = pdftext.encode('base64')
			pdf_filename = 'eticket.pdf'	
			# creamos el attach del pdf en el registro
			attachment_id = attachment_obj.create(
				{
					'name': pdf_filename,
					'datas': pdftext,
					'datas_fname': pdf_filename,
					'res_model': self._name,
					'res_id': self.id,
					'type': 'binary'
	            })

			# y también generamos el QR code adjunto
			self.create_QRcode(label_QR)
		return True



class mail_compose_message_extend(osv.TransientModel):
	_inherit = 'mail.compose.message'
	include_model_attachments = fields.Boolean(string='incluir adjuntos del model')
	# se detectará el cambio de template y si se ha solicitado incluir eticket
	# en ese caso, se incluirá como adjuntos todos los documentos del registro de evento

	def onchange_template_id(self, cr, uid, ids, template_id,
                             composition_mode, model, res_id, context=None):
		if not context:
			context = {}

		template_obj = self.pool.get('email.template')
		if template_id and isinstance(template_id, list):
			template_id = template_id[0]

		result = super(mail_compose_message_extend, self).onchange_template_id(
                        cr, uid, ids, template_id,
                        composition_mode, model, res_id, context=context)

		attach = []
		if template_id:
			if context and context.get('include_eticket') :
				# buscamos los attachments del registro y los agregamos al correo
				template = template_obj.browse(cr, uid, template_id, context)
				attachment_obj = self.pool.get('ir.attachment')
				attach = attachment_obj.search(cr, uid, [('res_id', '=', res_id), ('res_model', '=', model)])

		attach += result.get('value', {}).pop('attachment_ids', [])
		result.get('value', {}).update({'attachment_ids': attach})			

		return result


	def default_get(self, cr, uid, fields, context=None):
		# esto ya no es necesario, queda como ejemplo
		if context is None:
			context = {}
		result = super(mail_compose_message_extend, self).default_get(cr, uid, fields, context=context)
		if context and context.get('include_eticket') :
			result['include_model_attachments'] = True
		return result
