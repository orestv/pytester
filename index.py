from webpy import web
import model
import test
import admin

render = web.template.render('templates/')
urls = (
        '/', 'login',
        '/dashboard', 'Dashboard',
        '/loginHandler', 'LoginHandler',
        '/test', test.app,
        '/admin', admin.app
    )
app = web.application(urls, locals())

if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'), {'student_id': -1})
    web.config._session = session
else:
    session = web.config.get('_session')
def session_hook():
    web.ctx.session = session
app.add_processor(web.loadhook(session_hook))


class LoginHandler:
    def POST(self):
        i = web.input()
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
        tests = model.get_student_available_tests(student_id)
        return render.dashboard(student_info, attempts, tests)

class login:
    def GET(self):
        return render.login()

if __name__ == '__main__':
    app.run()