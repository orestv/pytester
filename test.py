import web
import model

urls = (
	'', 'retest',
	'/test', 'Test',
	'/start', 'Start',
	'/continue', 'Continue',
	'/answerHandler', 'HandleAnswer'
)
render = web.template.render('templates/')
app = web.application(urls, locals())

class retest:
	def GET(self): raise web.seeother('/')

class Test:
	def GET(self):
		i = web.input()
		attempt_id = i.attempt_id
		test_id = i.test_id
		student_id = web.ctx.session['student_id']
		questions = model.get_questions_for_test(test_id, student_id, attempt_id)
		return render.test('Test', attempt_id, questions)
	def POST(self):
		i = web.input()
		attempt_id = i.attempt_id
		model.save_attempt(attempt_id)
		raise web.seeother('../dashboard')

class Start:
	def GET(self):
		i = web.input()
		test_id = i.test_id
		student_id = web.ctx.session['student_id']
		attempt_id = model.start_new_attempt(test_id, student_id)
		raise web.seeother('/test?attempt_id=%s&test_id=%s'%(attempt_id, test_id))

class Continue:
	def GET(self):
		i = web.input()
		attempt_id = i.attempt_id
		test_id = i.test_id
		raise web.seeother('/test?attempt_id=%s&test_id=%s'%(attempt_id, test_id))

class HandleAnswer:
	def POST(self):
		i = web.input()
		attempt_id = i.attempt_id
		question_id = i.question_id
		answers = i.answers.strip(',').split(',')
		model.update_answers(web.ctx.session['student_id'], attempt_id, question_id, answers)
		pass