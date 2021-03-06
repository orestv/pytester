from webpy import web
import model
import json

urls = (
    '/?', 'Dashboard',
    # '', 'Dashboard',
    '/login', 'Login',
    '/test', 'Test',
    '/tests', 'Tests',
    '/topic', 'Topic',
    '/topics', 'Topics',
    '/questions', 'Questions',
    '/question', 'Question',
    '/uploadQuestions', 'QuestionsUpload'
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

class Tests:
    def GET(self):
        tests = model.get_tests()
        return json.dumps(tests)

class Test:
    def POST(self):
        i = web.input(topics = [], final = False)
        action = i.action
        if action == 'add':
            topic_ids = [int(x) for x in i.topics]
            question_count = int(i.question_count)
            name = i.name
            final = i.final
            model.add_test(name, topic_ids, question_count, final)
        elif action == 'rename':
            name = i.name
            model.rename_test(test_id, name)
        elif action == 'delete':
            test_id = i.id
            model.delete_test(test_id)

class Login:
    def POST(self):
        i = web.input()
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
        i = web.input()
        topic_id = i.topic_id
        if i.get('json'):
            questions = model.get_questions_for_topic(topic_id)
            return json.dumps(questions)
        else:
            topic_name = model.get_topic(topic_id)['name']
            return render.questions(topic_id, topic_name)


class QuestionsUpload:
    def POST(self):
        i = web.input()
        questions = i['file']
        topic_id = i['topic_id']
        model.upload_questions(topic_id, questions)
        raise web.seeother('/questions?topic_id=%(id)s' % {'id': topic_id})

class Question:
    def GET(self):
        i = web.input()
        question_id = i['question_id']
        print 'question id is', question_id
        question = model.get_question(question_id)
        print 'Question is', question
        topic_id = question['topic_id']
        action = i.action
        if action == 'delete':
            model.delete_question(question_id)
        raise web.seeother('questions?topic_id=%(id)s' % {'id': topic_id})

class Topic:
    def POST(self):
        i = web.input()
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