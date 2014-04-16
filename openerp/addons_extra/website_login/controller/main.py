from openerp import http
import werkzeug.utils
from openerp.addons.web.http import request, LazyResponse
import openerp.addons.website.controllers.main as website
import openerp.addons.web.controllers.main as web
from openerp import pooler, sql_db
import openerp

class Home_extend(web.Home):
    
    def web_login_shop(self, redirect=None, **kw):
        web.ensure_db()

        values = request.params.copy()
        if not redirect:
            redirect = '/shop?' + request.httprequest.query_string
        values['redirect'] = redirect
        if request.httprequest.method == 'POST':
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            if uid is not False:
                return http.redirect_with_hash(redirect)
            values['error'] = "Wrong login/password"
        return web.render_bootstrap_template(request.session.db, 'web.login', values, lazy=True)
    
    @http.route('/shop/login', type='http', auth='public', website=True, multilang=True)
    def login_shop(self, *args, **kw):
        response = self.web_login_shop(*args, **kw)
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
    
