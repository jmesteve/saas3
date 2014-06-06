from openerp.osv import osv, fields
from openerp.addons.payment_ogone.controllers.main import OgoneController
import urlparse
from openerp.tools import float_round

class PaymentAcquirerOgone(osv.Model):
    _inherit = 'payment.acquirer'
    
    def ogone_form_generate_values(self, cr, uid, id, partner_values, tx_values, context=None):
        base_url = self.pool['ir.config_parameter'].get_param(cr, uid, 'website_payment.base.url')
        acquirer = self.browse(cr, uid, id, context=context)

        ogone_tx_values = dict(tx_values)
        temp_ogone_tx_values = {
            'PSPID': acquirer.ogone_pspid,
            'ORDERID': tx_values['reference'],
            'AMOUNT': '%d' % int(float_round(tx_values['amount'], 2) * 100),
            'CURRENCY': tx_values['currency'] and tx_values['currency'].name or '',
            'LANGUAGE':  partner_values['lang'],
            'CN':  partner_values['name'],
            'EMAIL':  partner_values['email'],
            'OWNERZIP':  partner_values['zip'],
            'OWNERADDRESS':  partner_values['address'],
            'OWNERTOWN':  partner_values['city'],
            'OWNERCTY':  partner_values['country'] and partner_values['country'].name or '',
            'OWNERTELNO': partner_values['phone'],
            'ACCEPTURL': '%s' % urlparse.urljoin(base_url, OgoneController._accept_url),
            'DECLINEURL': '%s' % urlparse.urljoin(base_url, OgoneController._decline_url),
            'EXCEPTIONURL': '%s' % urlparse.urljoin(base_url, OgoneController._exception_url),
            'CANCELURL': '%s' % urlparse.urljoin(base_url, OgoneController._cancel_url),
        }
        if ogone_tx_values.get('return_url'):
            temp_ogone_tx_values['PARAMPLUS'] = 'return_url=%s' % ogone_tx_values.pop('return_url')
        shasign = self._ogone_generate_shasign(acquirer, 'in', temp_ogone_tx_values)
        temp_ogone_tx_values['SHASIGN'] = shasign
        ogone_tx_values.update(temp_ogone_tx_values)
        return partner_values, ogone_tx_values
