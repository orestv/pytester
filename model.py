# coding=utf-8
import MySQLdb
from DBUtils.PooledDB import PooledDB
import ConfigParser
import time
import chardet
import re
import random

config = ConfigParser.RawConfigParser()
config.read('app.cfg')
dbparams = {'host': config.get('Database', 'host'),
    'db': config.get('Database', 'db'),
    'user': config.get('Database', 'user'),
    'passwd': config.get('Database', 'passwd') }
db = PooledDB(MySQLdb, maxconnections=4,
        db=dbparams['db'],
        user=dbparams['user'],
        passwd=dbparams['passwd'],
        host=dbparams['host'],
        use_unicode=True,
        charset='utf8')

def get_cursor():
    conn = db.connection()
    return conn.cursor(MySQLdb.cursors.DictCursor)

def get_student_id(firstname, lastname):
    c = get_cursor()
    c.execute('SELECT id FROM student WHERE firstname = %s AND lastname = %s', (firstname, lastname))
    result = c.fetchone()
    if result:
        return int(result['id'])
    else:
        c.execute('INSERT INTO student (firstname, lastname) VALUES (%s, %s)',
            (firstname, lastname))
        return c.lastrowid

def get_students():
    c = get_cursor()
    c.execute('''SELECT id, firstname, lastname, hash FROM student ORDER BY lastname, firstname''')
    return c.fetchall()
def get_student_info(id):
    c = get_cursor()
    c.execute('SELECT id, firstname, lastname, hash FROM student WHERE id = %s', (id))
    return c.fetchone()
def get_student_test_attempts(student_id, test_id = None):
    c = get_cursor()
    c.execute('''SELECT t.id AS test_id, t.name,
        ta.id AS attempt_id, ta.start, ta.end, CAST(ta.result AS UNSIGNED) AS result,
        COUNT(DISTINCT a.question_id) AS answered, t.questionCount AS question_count
        FROM test_attempt ta
        INNER join test t ON ta.test_id = t.id
        LEFT OUTER JOIN student_answer sa ON sa.test_attempt_id = ta.id
        LEFT OUTER JOIN answer a ON a.id = sa.answer_id
        WHERE ta.student_id = %s
        GROUP BY t.id, t.name, ta.id, ta.start, ta.end, ta.result, t.questionCount
        ORDER BY ta.start DESC''', (student_id))
    result = c.fetchall()
    if test_id:
        result = filter(lambda row : row['test_id'] == test_id, result)
    return result
def get_student_available_tests(student_id):
    c = get_cursor()
    c.execute('''SELECT test.id, test.name AS name,
        ta.result AS result, ta.id AS attempt_id, test.questionCount AS question_count
        FROM test
        LEFT OUTER JOIN (
            SELECT id, ta_.test_id, ta_.student_id, ta_.result FROM test_attempt ta_
            INNER JOIN (
                SELECT test_id, student_id, MAX(result) AS result
                    FROM test_attempt
                    GROUP BY test_attempt.test_id, test_attempt.student_id
            ) tt ON ta_.test_id = tt.test_id
                AND ta_.student_id = tt.student_id
                AND ta_.result = tt.result
            GROUP BY ta_.test_id, ta_.student_id, ta_.result
        ) ta ON ta.test_id = test.id AND ta.student_id = %s''', (student_id))
    return c.fetchall()

def start_new_attempt(test_id, student_id):
    c = get_cursor()
    c.execute('''INSERT into test_attempt (test_id, student_id) values (%s, %s)''', (test_id, student_id))
    attempt_id = c.lastrowid
    test = get_test(test_id)
    question_count = test['questionCount']
    add_question_sequence(attempt_id, test_id, question_count)
    return attempt_id

def get_attempt(attempt_id):
    c = get_cursor()
    c.execute('''SELECT id, test_id, student_id, start, end, result FROM test_attempt WHERE id = %s''', (attempt_id))
    return c.fetchone()
def get_test_report(test_id):
    c = get_cursor()
    c.execute('''SELECT s.id, firstname, lastname, ta.id AS attempt_id,
        ta.result, t.questionCount AS maxResult
        FROM student s
        INNER JOIN test t ON t.id = %s
        LEFT OUTER JOIN test_attempt ta ON ta.test_id = t.id AND ta.student_id = s.id
        ORDER BY lastname, firstname;''',
        (test_id))
    rows = c.fetchall()
    students = unique([(row['id'], row['firstname'], row['lastname'], row['maxResult']) for row in rows])
    result = []
    for student in students:
        id, firstname, lastname, max_result = student
        item = {'id': id, \
            'firstname': firstname, \
            'lastname': lastname, \
            'maxResult': max_result}
        attempts = filter(lambda row : row['id'] == id, rows)
        best_attempt = sorted(attempts, key=lambda a: a['result'], reverse=True)[0]
        item['attemptCount'] = len(filter(lambda a: a['attempt_id'], attempts))
        item['result'] = best_attempt['result']
        item['attempt_id'] = best_attempt['attempt_id']
        result.append(item)
    return result

def save_attempt(attempt_id):
    c = get_cursor()
    result = get_attempt_result(attempt_id)
    c.execute('''UPDATE test_attempt ta
        SET end = CURRENT_TIMESTAMP(),
            result = %s
        WHERE ta.id = %s''',
        (result, attempt_id))
def get_attempt_result(attempt_id):
    questions = get_questions_for_attempt(attempt_id)
    results = [get_question_result(attempt_id, q['id']) for q in questions]
    return sum(results)
def get_attempt_report(attempt_id):
    c = get_cursor()
    c.execute('''SELECT q.id AS id, q.text AS text, q.multiselect, q.comment,
            a.id AS ans_id, a.text AS ans_text,
            NOT ISNULL(sa.id) AS ans_selected, a.correct AS correct
        FROM question_sequence_questions qsq
        INNER join question q
            ON qsq.question_id = q.id
        INNER JOIN answer a
            ON a.question_id = q.id
        INNER JOIN test_attempt ta
            ON ta.id = qsq.attempt_id
        LEFT OUTER JOIN student_answer sa
            ON sa.test_attempt_id = ta.id AND sa.answer_id = a.id
        WHERE qsq.attempt_id = %s
        ORDER BY qsq.order ASC;''', (attempt_id))
    rows = c.fetchall()
    questions = merge_answers(rows, \
        {x:x for x in ['text', 'comment', 'multiselect']}, \
        {'id':'ans_id', 'text':'ans_text', 'correct':'correct', 'selected':'ans_selected'})
    return questions

def unique(ls):
    result = []
    seen = {}
    for item in ls:
        if item in seen:
            continue
        seen[item] = 1
        result.append(item)
    return result

def merge_answers(rows, question_captions, answer_captions):
    qids = unique([row['id'] for row in rows])
    questions = []
    for qid in qids:
        qs = filter(lambda row : row['id'] == qid, rows)
        question = {name: qs[0][key] for name, key in question_captions.iteritems()}
        question['id'] = qs[0]['id']
        answers = [{name: q[key] for name, key in answer_captions.iteritems()} for q in qs]
        question['answers'] = answers
        questions.append(question)
    return questions

def get_question_result(attempt_id, question_id):
    c = get_cursor()
    c.execute('''SELECT CASE WHEN EXISTS(
        SELECT q.id, a.id, a.text, a.correct, ta.id
        FROM question q
        INNER JOIN answer a ON q.id = a.question_id
        LEFT OUTER JOIN student_answer sa
            ON a.id = sa.answer_id AND sa.test_attempt_id = %s
        LEFT OUTER JOIN test_attempt ta
            ON ta.id = sa.test_attempt_id
        WHERE q.id = %s AND
            ((a.correct = 1 AND ISNULL(sa.id) = 1)
            OR (a.correct = 0 AND ISNULL(sa.id) = 0))
    ) THEN 0 ELSE 1 END AS correct''',
    (attempt_id, question_id))
    return int(c.fetchone()['correct'])
def get_question_answers(attempt_id, question_id):
    pass

def get_questions_for_attempt(attempt_id):
    c = get_cursor()
    c.execute('''SELECT qsq.question_id AS id
        FROM question_sequence_questions qsq
        INNER JOIN question q
            ON q.id = qsq.question_id
        INNER JOIN test_attempt ta
            ON qsq.attempt_id = ta.id
        WHERE ta.id = %s
        ORDER BY qsq.order ASC''',
        (attempt_id))
    return c.fetchall()
def get_questions_for_test(attempt_id):
    c = get_cursor()
    c.execute('''SELECT q.id AS id, q.text AS text, q.multiselect, a.id AS ans_id,
            a.text AS ans_text, NOT ISNULL(sa.id) AS ans_selected, qsq.order AS `order`
        FROM question_sequence_questions qsq
        INNER join question q
            ON qsq.question_id = q.id
        INNER JOIN answer a
            ON a.question_id = q.id
        INNER JOIN test_attempt ta
            ON ta.id = qsq.attempt_id
        LEFT OUTER JOIN student_answer sa
            ON sa.test_attempt_id = ta.id AND sa.answer_id = a.id
        WHERE qsq.attempt_id = %s
        ORDER BY qsq.order ASC;''', (attempt_id))
    rows = c.fetchall()
    result = merge_answers(rows, \
        {x:x for x in ['text', 'multiselect']}, \
        {'id':'ans_id', 'text':'ans_text','selected':'ans_selected'})
    return result
def get_questions_for_topic(topic_id):
    c = get_cursor()
    c.execute('''SELECT q.id, q.text, q.multiselect, q.comment,
        a.id AS ans_id, a.text AS ans_text, correct
        FROM question q
        INNER JOIN answer a ON q.id = a.question_id
        WHERE q.topic_id = %s;''', (topic_id))
    rows = c.fetchall()
    questions = merge_answers(rows, \
        {x:x for x in ['text', 'multiselect', 'comment']}, \
        {'id': 'ans_id', 'text': 'ans_text', 'correct': 'correct'})
    return questions

def update_answers(student_id, attempt_id, question_id, answers):
    c = get_cursor()
    time.sleep(1)
    c.execute('''DELETE sa
        FROM student_answer sa
        INNER JOIN answer a ON sa.answer_id = a.id
        WHERE a.question_id = %s AND sa.student_id = %s
            AND sa.test_attempt_id = %s;''', (question_id, student_id, attempt_id))
    for ans in answers:
        c.execute('''INSERT INTO student_answer (student_id, test_attempt_id, answer_id)
            VALUES (%s, %s, %s)''', (student_id, attempt_id, ans))

def detect_linebreaks(input):
    linebreaks = ['\n', '\n\r', '\r\n']
    def cmp_(x, y):
        if cmp(x[0], y[0]):
            return -cmp(x[0], y[0])
        return -cmp(len(x[1]), len(y[1]))
    nl = map(lambda x : (input.count(x), x), linebreaks)
    nl.sort(cmp_)
    return nl[0][1]

def get_question(question_id):
    c = get_cursor()
    c.execute('''SELECT id, topic_id, text, comment, multiselect
        FROM question WHERE id = %s''', (question_id))
    return c.fetchone()
def question_exists(topic_id, question_text):
    c = get_cursor()
    c.execute('''SELECT CASE WHEN EXISTS
            (SELECT * FROM question WHERE topic_id = %s AND text = %s)
        THEN 1 ELSE 0 END AS question_exists;''', (topic_id, question_text))
    return bool(c.fetchone()['question_exists'])
def add_question(topic_id, text, comment, multiselect):
    c = get_cursor()
    c.execute('''INSERT INTO question (topic_id, text, comment, multiselect)
        VALUES (%s, %s, %s, %s);''', (topic_id, text, comment, multiselect))
    return c.lastrowid
def delete_question(question_id):
    c = get_cursor()
    c.execute('''DELETE q, a FROM question q
        INNER JOIN answer a ON q.id = a.question_id
        WHERE q.id = %s''', (question_id))
def add_answer(question_id, text, correct):
    c = get_cursor()
    c.execute('''INSERT INTO answer (question_id, text, correct)
            VALUES (%s, %s, %s);''', (question_id, text, correct))

def upload_questions(topic_id, questions):
    detection = chardet.detect(questions)
    encoding = detection.get('encoding') or 'utf-8'
    questions = unicode(questions, encoding)
    lb = detect_linebreaks(questions)
    pattern = '{0}({0})+'.format(lb)
    questions = re.split(pattern, questions)
    for block in questions:
        block = block.strip()
        if not block:
            continue
        rows = block.split(lb)
        question_text = rows[0]
        if question_exists(topic_id, question_text):
            continue
        question_comment = None
        answers = rows[1:]  #all rows except first
        if rows[-1].startswith('//'):   #is last row comment?
            question_comment = rows[-1][2:] #last row without //
            answers = rows[1:-1]    #all rows except first and last
        multiselect = len(filter(lambda x : x.startswith('*'), answers)) > 1    #count correct answers
        question_id = add_question(topic_id, question_text, question_comment, multiselect)
        for answer_text in answers:
            if not answer_text.strip():
                continue
            correct = answer_text.startswith('*')
            if correct:
                answer_text = answer_text.lstrip('*')
            add_answer(question_id, answer_text, correct)

def get_tests():
    c = get_cursor()
    c.execute('''SELECT id, name, final, questionCount FROM test''')
    return c.fetchall()
def get_test(test_id):
    c = get_cursor()
    c.execute('''SELECT id, name, final, questionCount FROM test WHERE id = %s''',
        (test_id))
    return c.fetchone()
def delete_test(test_id):
    c = get_cursor()
    c.execute('''DELETE t, ta, qsq, sa
        FROM test t
        LEFT OUTER JOIN test_attempt ta ON t.id = ta.test_id
        LEFT OUTER JOIN student_answer sa ON t.id = sa.test_attempt_id
        LEFT OUTER JOIN question_sequence_questions qsq ON ta.id = qsq.attempt_id
        WHERE t.id = %s''',
        (test_id))
def rename_test(test_id, test_name):
    c = get_cursor()
    c.execute('''UPDATE test
        SET name = %s
        WHERE id = %s''', (test_name, test_id))
def add_test(name, topic_ids, question_count, final):
    final = 1 if final else 0
    c = get_cursor()
    c.execute('''INSERT INTO test (name, questionCount, final)
        VALUES (%s, %s, %s)''',
        (name, question_count, final))
    test_id = c.lastrowid
    for topic_id in topic_ids:     #fill test topics
        c.execute('''INSERT INTO test_topics (test_id, topic_id)
            VALUES (%s, %s)''',
            (test_id, topic_id))
    return test_id

def get_question_ids_for_test(test_id):
    c = get_cursor()
    c.execute('SELECT topic_id FROM test_topics WHERE test_id = %s', (test_id))
    topic_ids = [topic['topic_id'] for topic in c.fetchall()]
    topic_ids_string = ','.join(map(lambda x:str(x), topic_ids))
    c.execute('SELECT id FROM question WHERE topic_id IN (' + topic_ids_string + ')')
    question_ids = [q['id'] for q in c.fetchall()]
    return question_ids

def add_question_sequence(attempt_id, test_id, question_count):
    question_ids = get_question_ids_for_test(test_id)
    qids = list(question_ids)       #create a copy
    random.shuffle(qids)
    qids = qids[:question_count]
    c = get_cursor()
    for index, question_id in enumerate(qids):
        c.execute('''INSERT INTO question_sequence_questions
            (attempt_id, question_id, `order`)
            VALUES (%s, %s, %s);''',
            (attempt_id, question_id, index+1))

def get_topic(topic_id):
    c = get_cursor()
    c.execute('''SELECT id, name FROM topic WHERE id = %s''', (topic_id))
    return c.fetchone()
def get_topics():
    c = get_cursor()
    c.execute('''SELECT t.id, t.name, COUNT(q.id) AS question_count
        FROM topic t
        LEFT OUTER JOIN question q ON t.id = q.topic_id
        GROUP BY t.id, t.name
        ORDER BY name ASC;''')
    return c.fetchall()
def add_topic(topic_name):
    c = get_cursor()
    c.execute('INSERT INTO topic (name) VALUES (%s);', (topic_name))
    return c.lastrowid
def delete_topic(topic_id):
    c = get_cursor()
    c.execute('''DELETE t FROM topic t
        LEFT OUTER JOIN question q ON t.id = q.topic_id
        LEFT OUTER JOIN answer a ON q.id = a.question_id
        WHERE t.id = %s''', (topic_id))
def rename_topic(topic_id, topic_name):
    c = get_cursor()
    c.execute('''UPDATE topic SET name = %s WHERE id = %s''',
        (topic_name, topic_id))