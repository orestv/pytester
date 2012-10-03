import web
import model

render = web.template.render('templates/')
urls = (
		'/', 'login',
		'/dashboard', 'Dashboard',
		'/loginHandler', 'LoginHandler'
	)
app = web.application(urls, globals())

if web.config.get('_session') is None:
	session = web.session.Session(app, web.session.DiskStore('sessions'), {'student_hash': 15})
	web.config._session = session
else:
	session = web.config.get('_session')

class LoginHandler:
	def POST(self):
		i = web.input(name=None)
		firstname = i.firstname
		lastname = i.lastname
		student_hash = model.get_student_hash(firstname, lastname)['hash']
		session.student_hash = student_hash
		web.seeother('/dashboard')

class Dashboard:
	def GET(self):
		if web.config.get('_session') is None:
			print 'Sesion in web.config is none'
			session = web.session.Session(app, web.session.DiskStore('sessions'), {'student_hash': 15})
			print 'Created a new sesssion, ', session
			web.config._session = session
		else:
			print 'session in web.config is not none: it is ', web.config.get('_session')
			session = web.config.get('_session')
		student_hash = session['student_hash']
		student_info = model.get_student_info(student_hash)
		return render.dashboard(student_hash, student_info['firstname'], student_info['lastname'])

class login:
	def GET(self):
		return render.login()

class hello:
	def GET(self):
		return 'Hello, {0}!'.format('Orest')

if __name__ == '__main__':
	app.run()