import webapp2
import authomatic
from config import CONFIG


def links(handler):
    for p in CONFIG.keys():
        handler.response.write('<a href="auth/{p}">{p}</a><br />'.format(p=p))
    handler.response.write('<br /><br />')


def loop(handler, obj):
    handler.response.write('<table>')
    for k, v in obj.__dict__.items():
        if not k in ('data', 'gae_user', 'credentials', 'content'):
            style = 'color: red' if not v else ''
            handler.response.write('<tr style="{}"><td>{}:</td><td>{}</td></tr>'.format(style, k, v))
    handler.response.write('</table>')


class Login(webapp2.RequestHandler):
    def any(self, provider_name):
        self.response.write("""<!DOCTYPE html><html>
        <head>
            <script src="https://google-code-prettify.googlecode.com/svn/loader/run_prettify.js?skin=sunburst"></script>
        </head>
        """)
        
        self.response.write('<body>')
        self.response.write('<a href="..">Home</a> | ')
        self.response.write('<a href="../auth/{}">Retry</a>'.format(provider_name))
        
        result = authomatic.login(provider_name)
        
        if result.error:
            self.response.write('<h4>ERROR: {}</h4>'.format(result.error.message))
        
        elif result.user:
            result.user.update()
            
            self.response.write('<h3>User</h3>')
            self.response.write('<img src="{}" width="100" height="100" />'.format(result.user.picture))
            loop(self, result.user)
            
            if result.user.credentials:
                # loop through credentials attrs
                self.response.write('<h3>Credentials</h3>')
                loop(self, result.user.credentials)
                
                # refresh credentials
                response = result.user.credentials.refresh(force=True)
                
                if response:
                    self.response.write('<h3>Refresh status: {}</h3>'.format(response.status))
            
            self.response.write('<pre id="ui" class="prettyprint"></pre>')
            
            self.response.write("""
            <script type="text/javascript">
                ui = document.getElementById('ui');
                ui.innerHTML = JSON.stringify({}, undefined, 4);
            </script>
            """.format(result.user.content))
        
        self.response.write('</body></html>')


class Home(webapp2.RequestHandler):
    def get(self):
        links(self)


ROUTES = [webapp2.Route(r'/auth/<:.*>', Login, handler_method='any'),
          webapp2.Route(r'/', Home)]


app = authomatic.middleware(webapp2.WSGIApplication(ROUTES, debug=True),
                            config=CONFIG, # Here goes the config.
                            secret='some random secret string')