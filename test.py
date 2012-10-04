import web
import model

urls = (
	'', 'retest',
	'/test', 'Test',
	'/start', 'Start'
)
render = web.template.render('templates/')
app = web.application(urls, locals())

class retest:
	def GET(self): raise web.seeother('/')

class Test:
	def GET(self):
		i = web.input(name = None)
		attempt_id = i.attempt_id
		test_id = i.test_id
		student_id = web.ctx.session['student_id']
		questions = model.get_questions_for_test(test_id, student_id)
		# return test_id, student_id, attempt_id
		return render.test(questions, None)

class Start:
	def GET(self):
		i = web.input(name=None)
		test_id = i.test_id
		student_id = web.ctx.session['student_id']
		attempt_id = model.start_new_attempt(test_id, student_id)
		raise web.seeother('/test?attempt_id=%s&test_id=%s'%(attempt_id, test_id))