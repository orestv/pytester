# coding=utf-8
import os
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import model
import json

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = os.urandom(24)

def loggedin():
    return 'student_id' in session
def is_admin():
    return 'admin' in session

@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'GET':
        if not loggedin():
            return render_template('login.html')
        else:
            return redirect(url_for('dashboard'))
    else:
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        student_id = model.get_student_id(firstname, lastname)
        session['student_id'] = student_id
        return redirect('/')

@app.route('/dashboard')
def dashboard():
    if not loggedin():
        return redirect('/')
    student_id = int(session['student_id'])
    student = model.get_student_info(student_id)
    attempts = model.get_student_test_attempts(student_id)
    tests = model.get_student_available_tests(student_id)
    return render_template('dashboard.html',
        student = student,
        attempts = attempts,
        tests = tests)

@app.route('/test', methods=['GET', 'POST'])
def test():
    if not loggedin():
        return redirect('/')
    if not 'test_id' in request.args:
        return redirect('/')
    test_id = request.args['test_id']
    student_id = session['student_id']
    if 'continue' in request.args and 'attempt_id' in request.args:
        attempt_id = request.args.get('attempt_id')
    else:
        attempt_id = model.start_new_attempt(test_id, student_id)
        return redirect('/test?continue=1&test_id=%s&attempt_id=%s'%(test_id, attempt_id))
    questions = model.get_questions_for_test(attempt_id)
    return render_template('test.html',
        test_name = 'Test name stub',
        attempt_id = attempt_id,
        questions = questions)
@app.route('/attempt_report')
def attempt_report():
    is_json = request.args.get('json', False)
    if not loggedin() and not is_admin():
        return 'login_fail' if is_json else redirect('/')
    if not 'attempt_id' in request.args:
        return redirect('/')
    attempt_id = request.args['attempt_id']
    if is_json:
        return json.dumps(model.get_attempt_report(attempt_id))
    else:
        return render_template('attempt_report.html',
            test_name = 'Test name stub',
            attempt_id = attempt_id)

@app.route('/end_test', methods=['POST'])
def end_test():
    if not loggedin():
        return redirect('/')
    if not 'attempt_id' in request.form:
        return redirect(url_for('dashboard'))
    if request.form.get('finished') == '1':
        model.save_attempt(request.form['attempt_id'])
    return redirect(url_for('dashboard'))

@app.route('/update_answers', methods=['GET', 'POST'])
def update_answers():
    if not (loggedin() \
            and all(key in request.form for key in \
            ['question_id',\
            'attempt_id',\
            'answers'])):
        return ''
    student_id = session['student_id']
    question_id = request.form['question_id']
    attempt_id = request.form['attempt_id']
    answers = request.form['answers']
    answers = answers.strip(',').split(',')
    model.update_answers(student_id, attempt_id, question_id, answers)
    if request.method == 'GET':
        return redirect(url_for('dashboard'))
    return ''

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == 'HardTaught':
            session['admin'] = '1'
        return redirect(url_for('admin'))
    print is_admin()
    print session
    if not is_admin():
        return render_template('admin.html')
    topics = model.get_topics()
    return render_template('admin_dashboard.html',
        topics = topics)

@app.route('/admin/test', methods=['POST'])
def admin_test():
    if not is_admin():
        return 'login_fail'
    action = request.form['action']
    if action == 'add':
        topic_ids = request.form.getlist('topics', int)
        print topic_ids
        question_count = int(request.form['question_count'])
        name = request.form['name']
        final = request.form.get('final', False)
        model.add_test(name, topic_ids, question_count, final)
    elif action == 'delete':
        test_id = request.form['id']
        model.delete_test(test_id)
    elif action=='rename':
        test_id = request.form['id']
        name = request.form['name']
        model.rename_test(test_id, name)
    return ''
@app.route('/admin/topic', methods=['POST'])
def topic():
    if not is_admin():
        return 'login_fail'
    action = request.form['action']
    if action == 'add':
        name = request.form['name']
        model.add_topic(name)
    elif action == 'delete':
        id = request.form['id']
        model.delete_topic(id)
    elif action == 'rename':
        id = request.form['id']
        name = request.form['name']
        model.rename_topic(id, name)
    return ''
@app.route('/admin/question', methods=['POST'])
def question():
    if not is_admin():
        return 'login_fail'
    question_id = request.form['question_id']
    question = model.get_question(question_id)
    topic_id = question['topic_id']
    action = request.form['action']
    if action == 'delete':
        model.delete_question(question_id)
    return redirect('/admin/questions?topic_id=%(id)s' % {'id': topic_id})
@app.route('/admin/uploadQuestions', methods=['POST'])
def upload_questions():
    if not is_admin():
        return redirect(url_for('admin'))
    file = request.files['file']
    questions = file.getvalue()
    topic_id = request.form['topic_id']
    model.upload_questions(topic_id, questions)
    return redirect('/admin/questions?topic_id=%(id)s' % {'id': topic_id})

@app.route('/admin/topics')
def topics():
    return json.dumps(model.get_topics())
@app.route('/admin/tests')
def tests():
    return json.dumps(model.get_tests())
@app.route('/admin/questions')
def questions():
    is_json = request.args.get('json', False)
    if not is_admin():
        return 'login_fail' if is_json else redirect(url_for('admin'))
    topic_id = request.args['topic_id']
    if is_json:
        return json.dumps(model.get_questions_for_topic(topic_id))
    else:
        topic_name = model.get_topic(topic_id)['name']
        return render_template('questions.html',
            topic_id = topic_id,
            topic_name = topic_name)

if __name__ == '__main__':
    app.run(debug = True)