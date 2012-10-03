import web
import model

urls = (
	'/', 'Dashboard',
	'/login', 'Login',
	'/generateTest', 'GenerateTest'
)
render = web.template.render('templates/')
app_admin = web.application(urls, locals())
if web.config.get('_session') is None:
	session = web.session.Session(app_admin, web.session.DiskStore('sessions'), {})
	web.config._session = session
else:
	session = web.config.get('_session')


class Dashboard:
	def GET(self):
		return render.admin_dashboard()

class GenerateTest:
	pass

class Login:
	def POST(self):
		i = web.input(name=None)
		password = i.password
		if password == 'HardTaught':
			session['admin_logged_in'] = True
			raise web.seeother('/')
		else:
			return render.admin()

	def GET(self):
		return render.admin()