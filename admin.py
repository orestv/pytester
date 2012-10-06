import web
import model
import json

urls = (
    '/?', 'Dashboard',
    # '', 'Dashboard',
    '/login', 'Login',
    '/generateTest', 'GenerateTest',
    '/topic', 'Topic',
    '/topics', 'Topics',
    '/questions', 'Questions'
)
render = web.template.render('templates/')
app = web.application(urls, locals())

class Dashboard:
    def GET(self):
        if not web.ctx.session.get('admin_logged_in'):
            raise web.seeother('/login')
        topics = model.get_topics()
        return render.admin_dashboard(topics)

class Topics:
    def GET(self):
        topics = model.get_topics()
        return json.dumps(topics)

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

class Questions:
    def GET(self):
        i = web.input(name=None)
        id = i.topic_id
        name = model.get_topic(id)['name']
        questions = model.get_questions_for_topic(id)
        return render.questions(id, name, questions)

class Topic:
    def POST(self):
        i = web.input(name=None)
        action = i.action
        if action == 'add':
            name = i.name
            model.add_topic(name)
        elif action == 'delete':
            id = i.id
            model.delete_topic(id)
        elif action == 'rename':
            id = i.id
            name = i.name
            print id, name
            model.rename_topic(id, name)