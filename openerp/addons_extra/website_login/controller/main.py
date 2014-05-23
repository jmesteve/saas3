import logging

from openerp import http
import werkzeug.utils
from openerp.addons.web.http import request, LazyResponse
import openerp.addons.website.controllers.main as website
import openerp.addons.web.controllers.main as web
from openerp import pooler, sql_db
import openerp
import openerp.addons.auth_signup.controllers.main as auth_signup
import openerp.addons.website_sale.controllers.main as ecommerce
from openerp.tools.translate import _
from openerp.addons.auth_signup.res_users import SignupError
from openerp.tools import exception_to_unicode
import re

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
        
        products = [product for product in products_nofilter if product.product_variant_ids[0].qty_available > 0]

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
    
