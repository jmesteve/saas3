import openerp.http as http
from openerp.http import request
import werkzeug.utils
import openerp.addons.web.controllers.main as main

#class Session_extend(main.Session):
#    @http.route('/web/session/logout', type='http', auth="none")
#    def logout(self, redirect='/web'):
#        request.session.logout(keep_db=True)
#        return werkzeug.utils.redirect(redirect, 303)

class Home_extend(main.Home):
    @http.route('/login', type='http', auth="none")
    def login(self, redirect=None, **kw):
        
        #return http.redirect_with_hash(redirect)
        
        #main.ensure_db()

        values = request.params.copy()
        if not redirect:
            redirect = '/web?' + request.httprequest.query_string
        values['redirect'] = redirect
        if request.httprequest.method == 'POST':
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            if uid is not False:
                return http.redirect_with_hash(redirect)
            values['error'] = "Wrong login/password"
        return main.render_bootstrap_template(request.session.db, 'web.login', values, lazy=True)
