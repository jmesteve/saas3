from openerp.osv import osv, fields
from openerp.addons.payment_adyen.controllers.main import AdyenController
import urlparse
try:
    import simplejson as json
except ImportError:
    import json
from openerp.tools import float_round

class AcquirerAdyen(osv.Model):
    _inherit = 'payment.acquirer'
    
    def adyen_form_generate_values(self, cr, uid, id, partner_values, tx_values, context=None):
        base_url = self.pool['ir.config_parameter'].get_param(cr, uid, 'website_payment.base.url')
        acquirer = self.browse(cr, uid, id, context=context)
        # tmp
        import datetime
        from dateutil import relativedelta
        tmp_date = datetime.date.today() + relativedelta.relativedelta(days=1)

        adyen_tx_values = dict(tx_values)
        adyen_tx_values.update({
            'merchantReference': tx_values['reference'],
            'paymentAmount': '%d' % int(float_round(tx_values['amount'], 2) * 100),
            'currencyCode': tx_values['currency'] and tx_values['currency'].name or '',
            'shipBeforeDate': tmp_date,
            'skinCode': acquirer.adyen_skin_code,
            'merchantAccount': acquirer.adyen_merchant_account,
            'shopperLocale': partner_values['lang'],
            'sessionValidity': tmp_date,
            'resURL': '%s' % urlparse.urljoin(base_url, AdyenController._return_url),
        })
        if adyen_tx_values.get('return_url'):
            adyen_tx_values['merchantReturnData'] = json.dumps({'return_url': '%s' % adyen_tx_values.pop('return_url')})
        adyen_tx_values['merchantSig'] = self._adyen_generate_merchant_sig(acquirer, 'in', adyen_tx_values)
        return partner_values, adyen_tx_values