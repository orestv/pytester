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
	session = web.session.Session(app, web.session.DiskStore('sessions'), {'student_id': -1})
	web.config._session = session
else:
	session = web.config.get('_session')

class LoginHandler:
	def POST(self):
		i = web.input(name=None)
		firstname = i.firstname
		lastname = i.lastname
		student_id = model.get_student(firstname, lastname)['id']
		session.student_id = student_id
		web.seeother('/dashboard')

class Dashboard:
	def GET(self):
		student_id = int(session['student_id'])
		student_info = model.get_student_info(student_id)
		attempts = model.get_student_test_attempts(student_id)
		return render.dashboard(student_id, student_info['firstname'], student_info['lastname'], attempts)

class login:
	def GET(self):
		return render.login()

class hello:
	def GET(self):
		return 'Hello, {0}!'.format('Orest')

if __name__ == '__main__':
	app.run()