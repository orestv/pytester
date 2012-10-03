import web
import model

urls = (
	'', 'retest',
	'/test', 'Test',
	'/start', 'Start'
)
render = web.template.render('templates/')

if web.config.get('_session') is None:
	session = web.session.Session(app, web.session.DiskStore('sessions'), {'student_id': -1})
	web.config._session = session
else:
	session = web.config.get('_session')

class retest:
	def GET(self): raise web.seeother('/')

class Test:
	def GET(self):
		i = web.input(name = None)
		attempt_id = i.attempt_id
		test_id = i.test_id
		student_id = session['student_id']
		questions = model.get_questions_for_test(test_id, student_id)
		# return test_id, student_id, attempt_id
		return render.test(questions, None)

class Start:
	def GET(self):
		i = web.input(name=None)
		test_id = i.test_id
		student_id = session['student_id']
		attempt_id = model.start_new_attempt(test_id, student_id)
		raise web.seeother('/test?attempt_id=%s&test_id=%s'%(attempt_id, test_id))

app_test = web.application(urls, locals())