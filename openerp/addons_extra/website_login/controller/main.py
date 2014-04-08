from openerp import http
import werkzeug.utils
from openerp.addons.web.http import request, LazyResponse
import openerp.addons.website.controllers.main as website
import openerp.addons.web.controllers.main as web

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


    
