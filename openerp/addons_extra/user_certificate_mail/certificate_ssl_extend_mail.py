from openerp.osv import fields, osv

class certificate_ssl_extend_mail(osv.osv):
    
    _inherit = 'certificate.ssl'
    
    def action_send_mail(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the ssl template message loaded by default
        '''
        
        certificate = self.pool.get('certificate.ssl').browse(cr, uid, ids, context=context)[0]
        
        ir_attachment = self.pool.get('ir.attachment')
        mail_mail = self.pool.get('mail.mail')
        ir_model_data = self.pool.get('ir.model.data')
        attachment_ids = []
        attachment_data = {
            'name': certificate.name_filep12,
            'datas_fname': certificate.name_filep12,
            'datas': certificate.certificate_data_p12,
            'res_model': mail_mail._name
        }
        attachment_ids.append(ir_attachment.create(cr, uid, attachment_data, context=context))
        
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'user_certificate_mail', 'email_template_ssl')[1]
            
            email_obj = self.pool.get('email.template')  
            #get the object corresponding to template_id
            email = email_obj.browse(cr, uid, template_id)
            #get the id of the document, stored into field scanned
            attachment_id = attachment_ids[0]
            #write the new attachment to mail template
            email_obj.write(cr, uid, template_id, {'attachment_ids': [(6, 0, [attachment_id ])]})  
        except ValueError:
            template_id = False
            
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        ctx.update({
            'default_model': 'certificate.ssl',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })
        return {
            'name': 'Compose Email',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        
        
    def action_send_mail_password(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the ssl template password message loaded by default
        '''
        
        certificate = self.pool.get('certificate.ssl').browse(cr, uid, ids, context=context)[0]
        ir_model_data = self.pool.get('ir.model.data')
        
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'user_certificate_mail', 'email_template_ssl_password')[1]
        except ValueError:
            template_id = False
            
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        ctx.update({
            'default_model': 'certificate.ssl',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })
        return {
            'name': 'Compose Email',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }