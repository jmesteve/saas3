# -*- coding: utf-8 -*-
import logging

from openerp import http
import werkzeug.utils
import werkzeug.wrappers
from werkzeug.exceptions import HTTPException, NotFound
from openerp.addons.web.http import request, LazyResponse
import openerp.addons.website.controllers.main as website
import openerp.addons.web.controllers.main as web
import openerp.addons.payment_paypal.controllers.main as payment_paypal
from openerp import pooler, sql_db
import openerp
import openerp.addons.auth_signup.controllers.main as auth_signup
import openerp.addons.website_sale.controllers.main as ecommerce
from openerp.tools.translate import _
from openerp.addons.auth_signup.res_users import SignupError
from openerp.tools import exception_to_unicode
import re
from openerp.osv import orm, fields
from openerp import SUPERUSER_ID
import urllib2
import urllib
import pprint
import urlparse
try:
    import simplejson as json
except ImportError:
    import json

_logger = logging.getLogger(__name__)

class Home_extend(web.Home): 

    def check_email(self, email):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return False
        return True
    
    @http.route()
    def web_login(self, *args, **kw):
        mode = request.params.get('mode')
        qcontext = request.params.copy()
        response = web.render_bootstrap_template(request.session.db, 'auth_signup.signup', qcontext, lazy=True)
        token = qcontext.get('token', None)
        token_infos = None
        if token:
            try:
                # retrieve the user info (name, login or email) corresponding to a signup token
                res_partner = request.registry.get('res.partner')
                token_infos = res_partner.signup_retrieve_info(request.cr, openerp.SUPERUSER_ID, token)
                for k, v in token_infos.items():
                    qcontext.setdefault(k, v)
            except:
                qcontext['error'] = _("Invalid signup token")
                response.params['template'] = 'web.login'
                return response

        # retrieve the module config (which features are enabled) for the login page
        icp = request.registry.get('ir.config_parameter')
        config = {
            'signup': icp.get_param(request.cr, openerp.SUPERUSER_ID, 'auth_signup.allow_uninvited') == 'True',
            'reset': icp.get_param(request.cr, openerp.SUPERUSER_ID, 'auth_signup.reset_password') == 'True',
        }
        qcontext.update(config)

        if 'error' in qcontext or mode not in ('reset', 'signup') or (not token and not config[mode]):
            response = super(Home_extend, self).web_login(*args, **kw)
            if isinstance(response, LazyResponse):
                response.params['values'].update(config)
            return response

        if request.httprequest.method == 'GET':
            if token_infos:
                qcontext.update(token_infos)
        else:
            res_users = request.registry.get('res.users')
            login = request.params.get('login')
            if mode == 'reset' and not token:
                try:
                    res_users.reset_password(request.cr, openerp.SUPERUSER_ID, login)
                    qcontext['message'] = _("An email has been sent with credentials to reset your password")
                    response.params['template'] = 'web.login'
                except Exception:
                    qcontext['error'] = _("Could not reset your password")
                    _logger.exception('error when resetting password')
            else:
                values = dict((key, qcontext.get(key)) for key in ('login', 'name', 'password'))
                valid_email = True
                if(not self.check_email(values['login'])):
                    valid_email = False
                    qcontext['error'] = _('The email is invalid!')
                res = request.registry.get('res.users').search(request.cr, openerp.SUPERUSER_ID, [('login','=',values['login'])])
                if res:
                    #try:
                        #auth_signup.Home()._signup_with_values(token, values)
                        #request.cr.commit()
                    #except SignupError, e:
                    #    qcontext['error'] = exception_to_unicode(e)
                    qcontext['error'] = _('The user is already registered!')
                elif not valid_email:
                    qcontext['error'] = _('The email is invalid!')
                else:
                    return super(Home_extend, self).web_login(*args, **kw)
                    
                
        return response
    
    @http.route('/shop/register', type='http', auth='public', website=True, multilang=True)
    def login_register(self, redirect=None, **kw):
        #response = self.web_login_shop(*args, **kw)
        web.ensure_db()

        values = request.params.copy()
        if not redirect:
            redirect = '/shop?' + request.httprequest.query_string
        values['redirect'] = redirect
            
        response = self.web_login(redirect=redirect, **kw)
        if isinstance(response, LazyResponse):
            values = dict(response.params['values'], disable_footer=True)
            response = request.website.render(response.params['template'], values)
        return response
    
    @http.route('/shop/login', type='http', auth='public', website=True, multilang=True)
    def login_shop(self, redirect=None, **kw):
        #response = self.web_login_shop(*args, **kw)
        web.ensure_db()

        values = request.params.copy()
        if not redirect:
            redirect = '/shop?' + request.httprequest.query_string
        values['redirect'] = redirect
        if request.httprequest.method == 'POST':
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            if uid is not False:
                return http.redirect_with_hash(redirect)
            values['error'] = _("Wrong login/password")
            
        response = super(Home_extend, self).web_login(redirect=redirect, **kw)
        if isinstance(response, LazyResponse):
            values = dict(response.params['values'], disable_footer=True)
            response = request.website.render(response.params['template'], values)
        return response
    
    @http.route('/shop/session/logout', type='http', auth="none")
    def logout(self, redirect='/'):
        request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)

    @http.route('/home', type='http', auth="public", website=True, multilang=True)
    def index_website(self, **kw):
        try:
            main_menu = request.registry['ir.model.data'].get_object(request.cr, request.uid, 'website', 'main_menu')
            first_menu = main_menu.child_id and main_menu.child_id[0]
            # Dont 302 loop on /
            #if first_menu and not ((first_menu.url == '/home') or first_menu.url.startswith('/home#') or first_menu.url.startswith('/home?')):
            #    return request.redirect(first_menu.url)
        except:
            pass
        return self.page("website.homepage")

    @http.route('/', type='http', auth="public", website=True, multilang=True)
    def index(self, **kw):
        redirection_url = None
        dbname = request.session.db
        uid = openerp.SUPERUSER_ID
        context = request.session.context
        serverhost = request.httprequest.host
        # Get database connexion
        try:
            db = sql_db.db_connect(dbname) # You can get the db name from config
            cr = db.cursor()
            pool = pooler.get_pool(cr.dbname)
            ids = pool.get('shop.redirect').search(cr, uid, [('serverhost','ilike', serverhost)], limit=1, context=context)
            shop_redirect = pool.get('shop.redirect').browse(cr, uid, ids,context=context)[0]
            redirection_url = shop_redirect.route if shop_redirect != None else None
        
            default_shop_redirect = pool.get('ir.config_parameter').get_param(cr, uid, 'default_shop_redirect', context=context)
            redirection_url = default_shop_redirect if not redirection_url and default_shop_redirect else redirection_url
            cr.close()
        except:
            pass
            
        if not redirection_url:
            redirection_url = '/home'
        
        return request.redirect(redirection_url)
    

class Ecommerce(ecommerce.Ecommerce):
    
    @http.route([
        '/shop/',
        '/shop/page/<int:page>/',
        '/shop/category/<model("product.public.category"):category>/',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>/'
    ], type='http', auth="public", website=True, multilang=True)
    def shop(self, category=None, page=0, filters='', search='', **post):
        cr, uid, context = request.cr, request.uid, request.context
        product_obj = request.registry.get('product.template')
        domain = request.registry.get('website').ecommerce_get_product_domain()
        if search:
            domain += ['|',
                ('name', 'ilike', search),
                ('description', 'ilike', search)]
        if category:
            domain.append(('product_variant_ids.public_categ_id', 'child_of', category.id))
        if filters:
            filters = simplejson.loads(filters)
            if filters:
                ids = self.attributes_to_ids(filters)
                domain.append(('id', 'in', ids or [0]))

        product_count = product_obj.search_count(cr, uid, domain, context=context)
        pager = request.website.pager(url="/shop/", total=product_count, page=page, step=ecommerce.PPG, scope=7, url_args=post)

        request.context['pricelist'] = self.get_pricelist()

        pids = product_obj.search(cr, uid, domain, limit=ecommerce.PPG+10, offset=pager['offset'], order=self._order, context=context)
        products_nofilter = product_obj.browse(cr, uid, pids, context=context)
        
        products = [product for product in products_nofilter if product.product_variant_ids[0].virtual_available > 0 and not product.product_variant_ids[0].is_delivery]

        styles = []
        try:
            style_obj = request.registry.get('product.style')
            style_ids = style_obj.search(request.cr, request.uid, [], context=request.context)
            styles = style_obj.browse(request.cr, request.uid, style_ids, context=request.context)
        except:
            pass

        category_obj = request.registry.get('product.public.category')
        category_ids = category_obj.search(cr, uid, [], context=context)
        categories = category_obj.browse(cr, uid, category_ids, context=context)
        categs = filter(lambda x: not x.parent_id, categories)

        values = {
            'products': products,
            'bins': ecommerce.table_compute().process(products),
            'rows': ecommerce.PPR,
            'range': range,
            'search': {
                'search': search,
                'category': category and category.id,
                'filters': filters,
            },
            'pager': pager,
            'styles': styles,
            'categories': categs,
            'Ecommerce': self,   # TODO fp: Should be removed
            'style_in_product': lambda style, product: style.id in [s.id for s in product.website_style_ids],
        }
        return request.website.render("website_sale.products", values)
    
    @http.route('/shop/payment/validate/', type='http', auth="public", website=True, multilang=True)
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        cr, uid, context = request.cr, request.uid, request.context
        email_act = None
        sale_order_obj = request.registry['sale.order']

        if transaction_id is None:
            tx = context.get('website_sale_transaction')
        else:
            tx = request.registry['payment.transaction'].browse(cr, uid, transaction_id, context=context)

        if sale_order_id is None:
            order = self.get_order()
        else:
            order = request.registry['sale.order'].browse(cr, SUPERUSER_ID, sale_order_id, context=context)
            assert order.website_session_id == request.httprequest.session['website_session_id']

        if not tx or not order:
            # clean context and session, then redirect to the shop
            request.registry['website'].ecommerce_reset(cr, uid, context=context)
            
            return request.redirect('/shop/')

        if not order.amount_total or tx.state == 'done':
            # confirm the quotation
            sale_order_obj.action_button_confirm(cr, SUPERUSER_ID, [order.id], context=request.context)
            
            # send by email
            email_act = sale_order_obj.action_quotation_send(cr, SUPERUSER_ID, [order.id], context=request.context)
            sale_order_obj.write(cr, SUPERUSER_ID, order.id, {'user_id': SUPERUSER_ID}, context=request.context)
            compose_id = request.registry['mail.compose.message'].create(
                    cr, SUPERUSER_ID, {
                        'model': email_act.get('context').get('default_model'),
                        #'composition_mode': email_act.get('context').get('default_composition_mode'),
                        'template_id': email_act.get('context').get('default_template_id'),
                        'composition_mode': 'mass_mail'
                    }, context=email_act.get('context'))
            
            request.registry['mail.compose.message'].write(
                    cr, SUPERUSER_ID, [compose_id],
                    request.registry['mail.compose.message'].onchange_template_id(
                        cr, SUPERUSER_ID, [compose_id],
                        email_act.get('context').get('default_template_id'), 'mass_mail', email_act.get('context').get('default_model'), False,
                        context=email_act.get('context'))['value'],
                    context=email_act.get('context'))
            request.registry['mail.compose.message'].send_mail(cr, SUPERUSER_ID, [compose_id], context=email_act.get('context'))
        elif tx.state == 'pending':
            # confirm the quotation
            sale_order_obj.action_button_confirm(cr, SUPERUSER_ID, [order.id], context=request.context)
            
            # send by email
            email_act = sale_order_obj.action_quotation_send(cr, SUPERUSER_ID, [order.id], context=request.context)
            sale_order_obj.write(cr, SUPERUSER_ID, order.id, {'user_id': SUPERUSER_ID}, context=request.context)
            compose_id = request.registry['mail.compose.message'].create(
                    cr, SUPERUSER_ID, {
                        'model': email_act.get('context').get('default_model'),
                        #'composition_mode': email_act.get('context').get('default_composition_mode'),
                        'template_id': email_act.get('context').get('default_template_id'),
                        'composition_mode': 'mass_mail'
                    }, context=email_act.get('context'))
            
            request.registry['mail.compose.message'].write(
                    cr, SUPERUSER_ID, [compose_id],
                    request.registry['mail.compose.message'].onchange_template_id(
                        cr, SUPERUSER_ID, [compose_id],
                        email_act.get('context').get('default_template_id'), 'mass_mail', email_act.get('context').get('default_model'), False,
                        context=email_act.get('context'))['value'],
                    context=email_act.get('context'))
            request.registry['mail.compose.message'].send_mail(cr, SUPERUSER_ID, [compose_id], context=email_act.get('context'))
        elif tx.state == 'cancel':
            # cancel the quotation
            sale_order_obj.action_cancel(cr, SUPERUSER_ID, [order.id], context=request.context)

        # clean context and session, then redirect to the confirmation page
        request.registry['website'].ecommerce_reset(cr, uid, context=context)

        return request.redirect('/shop/confirmation/%s' % order.id)
    
    @http.route('/shop/payment/validate/ipn/', type='http', auth="public", website=True, multilang=True)
    def payment_validate_ipn(self, transaction_id=None, sale_order_id=None, **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        cr, uid, context = request.cr, request.uid, request.context
        email_act = None
        sale_order_obj = request.registry['sale.order']

        if transaction_id is None:
            tx = context.get('website_sale_transaction')
        else:
            tx = request.registry['payment.transaction'].browse(cr, uid, transaction_id, context=context)

        if sale_order_id is None:
            order = self.get_order()
        else:
            order = request.registry['sale.order'].browse(cr, SUPERUSER_ID, sale_order_id, context=context)
            assert order.website_session_id == request.httprequest.session['website_session_id']

        _logger.info("Beginning validate payment IPN")
        
        # Get transaction from post data
        if not tx and 'custom' in post:
            custom = json.loads(post['custom'])
            if 'tx_id' in post['custom']:
                transaction_id = custom['tx_id']
                tx = request.registry['payment.transaction'].browse(cr, SUPERUSER_ID, transaction_id, context=context)
                _logger.info("Payment IPN Transaction id: %s" % transaction_id)
        
        # Get order from post data
        if not order and 'custom' in post:
            custom = json.loads(post['custom'])
            if 'order_id' in custom:
                order_id = custom['order_id']
                order = request.registry['sale.order'].browse(cr, SUPERUSER_ID, order_id, context=context)
                _logger.info("Payment IPN Order id: %s" % order_id)
        
        if not tx or not order:
            raise NotFound()

        if not order.amount_total or tx.state == 'done':
            _logger.info("Paypal IPN Confirmed")
            
            # confirm the quotation
            sale_order_obj.action_button_confirm(cr, SUPERUSER_ID, [order.id], context=request.context)
            
            # send by email
            email_act = sale_order_obj.action_quotation_send(cr, SUPERUSER_ID, [order.id], context=request.context)
            sale_order_obj.write(cr, SUPERUSER_ID, order.id, {'user_id': SUPERUSER_ID}, context=request.context)
            compose_id = request.registry['mail.compose.message'].create(
                    cr, SUPERUSER_ID, {
                        'model': email_act.get('context').get('default_model'),
                        #'composition_mode': email_act.get('context').get('default_composition_mode'),
                        'template_id': email_act.get('context').get('default_template_id'),
                        'composition_mode': 'mass_mail'
                    }, context=email_act.get('context'))
            
            request.registry['mail.compose.message'].write(
                    cr, SUPERUSER_ID, [compose_id],
                    request.registry['mail.compose.message'].onchange_template_id(
                        cr, SUPERUSER_ID, [compose_id],
                        email_act.get('context').get('default_template_id'), 'mass_mail', email_act.get('context').get('default_model'), False,
                        context=email_act.get('context'))['value'],
                    context=email_act.get('context'))
            request.registry['mail.compose.message'].send_mail(cr, SUPERUSER_ID, [compose_id], context=email_act.get('context'))
            return ''
        elif tx.state == 'cancel':
            # cancel the quotation
            sale_order_obj.action_cancel(cr, SUPERUSER_ID, [order.id], context=request.context)
            return ''

        # clean context and session, then redirect to the confirmation page
        request.registry['website'].ecommerce_reset(cr, uid, context=context)
        
        raise NotFound()
        
    @http.route(['/shop/payment/transaction/<int:acquirer_id>'], type='http', methods=['POST'], auth="public", website=True)
    def payment_transaction(self, acquirer_id, **post):
        """ Hook method that creates a payment.transaction and redirect to the
        acquirer, using post values to re-create the post action.

        :param int acquirer_id: id of a payment.acquirer record. If not set the
                                user is redirected to the checkout page
        :param dict post: should coutain all post data for the acquirer
        """
        # @TDEFIXME: don't know why we received those data, but should not be send to the acquirer
        post.pop('submit.x', None)
        post.pop('submit.y', None)
        cr, uid, context = request.cr, request.uid, request.context
        payment_obj = request.registry.get('payment.acquirer')
        transaction_obj = request.registry.get('payment.transaction')
        order = self.get_order()

        if not order or not order.order_line or acquirer_id is None:
            return request.redirect("/shop/checkout/")

        # find an already existing transaction
        tx = context.get('website_sale_transaction')
        if not tx:
            tx_id = transaction_obj.create(cr, SUPERUSER_ID, {
                'acquirer_id': acquirer_id,
                'type': 'form',
                'amount': order.amount_total,
                'currency_id': order.pricelist_id.currency_id.id,
                'partner_id': order.partner_id.id,
                'reference': order.name,
                'sale_order_id': order.id,
            }, context=context)
            request.httprequest.session['website_sale_transaction_id'] = tx_id
        elif tx and tx.state == 'draft':  # button cliked but no more info -> rewrite on tx or create a new one ?
            tx.write({
                'acquirer_id': acquirer_id,
            })
        
        if 'custom' in post:
            custom = {}
            if tx:
                custom['tx_id'] = tx.id
            elif tx_id:
                custom['tx_id'] = tx_id
            else:
                custom['tx_id'] = request.httprequest.session['website_sale_transaction_id']
            
            if order:
                custom['order_id'] = order.id
                
            custom['return_url'] = '/shop/payment/validate'
            post['custom'] = json.dumps(custom)

        acquirer_form_post_url = payment_obj.get_form_action_url(cr, uid, acquirer_id, context=context)
        acquirer_total_url = '%s?%s' % (acquirer_form_post_url, werkzeug.url_encode(post))
        return request.redirect(acquirer_total_url)
       

class Website(orm.Model):
    _inherit = 'website'

    def ecommerce_update_order(self, cr, uid, order_id, context=None):
        order_line_obj = self.pool.get('sale.order.line')
        order_line_ids = order_line_obj.search(cr, SUPERUSER_ID, [('order_id', '=', order_id)], context=context)
        order_line_ids_values = order_line_obj.browse(cr, SUPERUSER_ID, order_line_ids, context=context)
        for order_line in order_line_ids_values:
            if (order_line.product_id.virtual_available <= 0 or not order_line.product_id.website_published) and not order_line.product_id.is_delivery:
                order_line_obj.unlink(cr, SUPERUSER_ID, order_line.id, context=context)
    
    def ecommerce_get_current_order(self, cr, uid, context=None):
        SaleOrder = self.pool.get('sale.order')
        context = dict(context or {}, pricelist=self.ecommerce_get_pricelist_id(cr, uid, None, context=context))
        order_id = request.httprequest.session.get('ecommerce_order_id')
        if not order_id:
            request.httprequest.session['ecommerce_order_id'] = False
            return False
        if not order_id in SaleOrder.exists(cr, uid, [order_id], context=context):
            request.httprequest.session['ecommerce_order_id'] = False
            return False
        try:
            order = SaleOrder.browse(cr, SUPERUSER_ID, order_id, context=context)
            assert order.website_session_id == request.httprequest.session['website_session_id']
            self.ecommerce_update_order(cr, SUPERUSER_ID, order_id, context=context)
            return order
        except:
            request.httprequest.session['ecommerce_order_id'] = False
            return False
        
class PaypalController(payment_paypal.PaypalController):
    
    def paypal_validate_data(self, **post):
        """ Paypal IPN: three steps validation to ensure data correctness

         - step 1: return an empty HTTP 200 response -> will be done at the end
           by returning ''
         - step 2: POST the complete, unaltered message back to Paypal (preceded
           by cmd=_notify-validate), with same encoding
         - step 3: paypal send either VERIFIED or INVALID (single word)

        Once data is validated, process it. """
        res = False
        new_post = dict(post, cmd='_notify-validate')
        urequest = urllib2.Request("https://www.sandbox.paypal.com/cgi-bin/webscr", werkzeug.url_encode(new_post))
        uopen = urllib2.urlopen(urequest)
        resp = uopen.read()
        if resp == 'VERIFIED':
            if 'website_sale_transaction_id' in request.httprequest.session:
                tx_id = request.httprequest.session['website_sale_transaction_id']
            elif 'custom' in post and 'tx_id' in post['custom']:
                custom = json.loads(post['custom'])
                tx_id = custom['tx_id']
            else:
                return
            if tx_id:
                tx_ids = request.registry['payment.transaction'].browse(request.cr, SUPERUSER_ID, tx_id, context=request.context)
                if type(tx_ids) is not list:
                    tx = tx_ids
                    tx.write({
                        'state': 'done',
                        #'date_validate': values.get('udpate_time', fields.datetime.now()),
                        #'paypal_txn_id': values['id'],
                    })
                elif type(tx_ids) is list:
                    tx = tx_ids[0]
                    tx.write({
                        'state': 'done',
                        #'date_validate': values.get('udpate_time', fields.datetime.now()),
                        #'paypal_txn_id': values['id'],
                    })
                request.httprequest.session['website_payment_paypal_done'] = True
            _logger.info('Paypal: validated data')
            cr, uid, context = request.cr, SUPERUSER_ID, request.context
            res = request.registry['payment.transaction'].form_feedback(cr, uid, post, 'paypal', context=context)
        elif resp == 'INVALID':
            _logger.warning('Paypal: answered INVALID on data verification')
        else:
            _logger.warning('Paypal: unrecognized paypal answer, received %s instead of VERIFIED or INVALID' % resp.text)
        return res
    
    @http.route('/payment/paypal/ipn/', type='http', auth='none', methods=['POST'])
    def paypal_ipn(self, **post):
        """ Paypal IPN. """
        _logger.info('Beginning Paypal IPN form_feedback with post data %s', pprint.pformat(post))  # debug
        self.paypal_validate_data(**post)
        
        data = urllib.urlencode(post)
        base_url = request.registry['ir.config_parameter'].get_param(request.cr, SUPERUSER_ID, 'website_payment.base.url')
        return_url = urlparse.urljoin(base_url, '/shop/payment/validate/ipn')
        req = urllib2.Request(return_url, data)
        try: 
            return urllib2.urlopen(req)
        except urllib2.HTTPError as e:
            return werkzeug.wrappers.Reponse('Not Found', status=404)
        
    @http.route(['/shop/mycart/'], type='http', auth="public", website=True, multilang=True)
    def mycart(self, **post):
        cr, uid, context = request.cr, request.uid, request.context
        prod_obj = request.registry.get('product.product')

        # must have a draft sale order with lines at this point, otherwise reset
        order = self.get_order()
        if order and order.state != 'draft':
            request.registry['website'].ecommerce_reset(cr, uid, context=context)
            return request.redirect('/shop/')

        self.get_pricelist()

        suggested_ids = []
        product_ids = []
        if order:
            for line in order.order_line:
                suggested_ids += [p.id for p in line.product_id and line.product_id.accessory_product_ids or []]
                product_ids.append(line.product_id.id)
        suggested_ids = list(set(suggested_ids) - set(product_ids))
        if suggested_ids:
            suggested_ids = prod_obj.search(cr, uid, [('id', 'in', suggested_ids)], context=context)

        # select 3 random products
        suggested_products = []
        while len(suggested_products) < 3 and suggested_ids:
            index = random.randrange(0, len(suggested_ids))
            suggested_products.append(suggested_ids.pop(index))

        context = dict(context or {}, pricelist=request.registry['website'].ecommerce_get_pricelist_id(cr, uid, None, context=context))

        values = {
            'int': int,
            'suggested_products': prod_obj.browse(cr, uid, suggested_products, context),
        }
        return request.website.render("website_sale.mycart", values)
