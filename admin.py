import web
import model

urls = (
    '/', 'Dashboard',
    '/login', 'Login',
    '/generateTest', 'GenerateTest'
)
render = web.template.render('templates/')
app = web.application(urls, locals())


class Dashboard:
    def GET(self):
        if not web.ctx.session['admin_logged_in']:
            raise web.seeother('/login')
        topics = model.get_topics()
        return render.admin_dashboard(topics)

class GenerateTest:
    pass

class Login:
    def POST(self):
        i = web.input(name=None)
        password = i.password
        if password == 'HardTaught':
            web.ctx.session['admin_logged_in'] = True
            raise web.seeother('/')
        else:
            return render.admin()

    def GET(self):
        return render.admin()