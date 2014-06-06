# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
from openerp.addons.payment_paypal.controllers.main import PaypalController
import urlparse
try:
    import simplejson as json
except ImportError:
    import json
    
import controller.main as ecommerce
from openerp.addons.web.http import request

_logger = logging.getLogger(__name__)

class AcquirerPaypal(osv.Model):
    _inherit = 'payment.acquirer'
    
    def paypal_form_generate_values(self, cr, uid, id, partner_values, tx_values, context=None):
        base_url = self.pool['ir.config_parameter'].get_param(cr, uid, 'website_payment.base.url')
        acquirer = self.browse(cr, uid, id, context=context)
        
        # Pass order_id in custom field to paypal
        order = ecommerce.Ecommerce().get_order()
        if order:
            order_id = order.id
        else:
            order_id = False
        
        # Pass transaction_id in custom field to paypal
        if 'website_sale_transaction_id' in request.httprequest.session:
            website_sale_transaction_id = request.httprequest.session['website_sale_transaction_id']
        else:
            website_sale_transaction_id = False

        paypal_tx_values = dict(tx_values)
        paypal_tx_values.update({
            'cmd': '_xclick',
            'business': acquirer.paypal_email_account,
            'item_name': tx_values['reference'],
            'item_number': tx_values['reference'],
            'amount': tx_values['amount'],
            'currency_code': tx_values['currency'] and tx_values['currency'].name or '',
            'address1': partner_values['address'],
            'city': partner_values['city'],
            'country': partner_values['country'] and partner_values['country'].name or '',
            'email': partner_values['email'],
            'zip': partner_values['zip'],
            'first_name': partner_values['first_name'],
            'last_name': partner_values['last_name'],
            'return': '%s' % urlparse.urljoin(base_url, PaypalController._return_url),
            'notify_url': '%s' % urlparse.urljoin(base_url, PaypalController._notify_url),
            'cancel_return': '%s' % urlparse.urljoin(base_url, PaypalController._cancel_url),
        })
        if acquirer.fees_active:
            paypal_tx_values['handling'] = '%.2f' % paypal_tx_values.pop('fees', 0.0)
        if paypal_tx_values.get('return_url'):
            paypal_tx_values['custom'] = json.dumps({'return_url': '%s' % paypal_tx_values.pop('return_url'), 
                                                     'order_id': order_id, 
                                                     'tx_id': website_sale_transaction_id})
        _logger.info(paypal_tx_values)
        return partner_values, paypal_tx_values
