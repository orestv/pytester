import MySQLdb

def get_cursor():
    db = MySQLdb.connect(db='tests', user='root', passwd='sdntvFreud', charset='utf8', use_unicode=True)
    return db.cursor(MySQLdb.cursors.DictCursor)

def get_student(firstname, lastname):
    c = get_cursor()
    c.execute('SELECT id, hash FROM student WHERE firstname = %s AND lastname = %s', (firstname, lastname))
    return c.fetchone()
def get_students():
    c = get_cursor()
    c.execute('''SELECT id, firstname, lastname, hash FROM student''')
    return c.fetchall()
def get_student_info(id):
    c = get_cursor()
    c.execute('SELECT id, firstname, lastname, hash FROM student WHERE id = %s', (id))
    return c.fetchone()
def get_student_test_attempts(student_id):
    c = get_cursor()
    c.execute('''SELECT t.id AS test_id, t.name, 
        ta.id AS attempt_id, ta.start, ta.end
        FROM test_attempt ta
        INNER join test t ON ta.test_id = t.id
        WHERE ta.student_id = %s
        ORDER BY ta.start DESC''', (student_id))
    return c.fetchall()
def get_student_available_tests(student_id):
    c = get_cursor()
    c.execute('''SELECT DISTINCT (test.id), test.name AS name,
        MAX(ta.result) AS result, COUNT(DISTINCT qsq.question_id) AS maxresult FROM test
        LEFT OUTER JOIN test_attempt ta ON ta.test_id = test.id
            AND ta.student_id = %s
        INNER JOIN question_sequence qs
            ON qs.test_id = test.id AND (qs.student_id = %s OR qs.student_id IS NULL)
        INNER JOIN question_sequence_questions qsq
            ON qsq.sequence_id = qs.id
        GROUP BY test.id, qs.id''', (student_id, student_id))
    return c.fetchall()

def start_new_attempt(test_id, student_id):
    c = get_cursor()
    c.execute('''INSERT into test_attempt (test_id, student_id) values (%s, %s)''', (test_id, student_id))
    return c.lastrowid

def get_test_for_attempt(attempt_id):
    c = get_cursor()
    c.execute('''SELECT id FROM  test_attempt WHERE id = %s''', (attempt_id))
    return c.fetchone()

def get_questions_for_test(test_id, student_id, attempt_id):
    c = get_cursor()
    c.execute('''SELECT q.id AS id, q.text AS text, q.multiselect, a.id AS ans_id,
            a.text AS ans_text, NOT ISNULL(sa.id) AS ans_selected
        FROM question_sequence qs
        INNER JOIN question_sequence_questions qsq
            ON qs.id = qsq.sequence_id
        INNER join question q
            ON qsq.question_id = q.id
        INNER JOIN answer a
            ON a.question_id = q.id
        LEFT OUTER JOIN student_answer sa
            ON sa.student_id = %s AND sa.test_attempt_id = %s AND sa.answer_id = a.id
        WHERE qs.test_id = %s AND (qs.student_id = %s OR ISNULL(qs.student_id) = 1)
        ORDER BY qsq.order ASC;''', (student_id, attempt_id, test_id, student_id))
    rows = c.fetchall()
    result = {}
    for row in rows:
        id = row['id']
        answer = {'id': row['ans_id'],
                'text': row['ans_text'],
                'selected': row['ans_selected']}
        if id in result:
            result[id]['answers'].append(answer)
        else:
            result[id] = {'text': row['text'],
                        'multiselect': row['multiselect'],
                        'answers': [answer]}
    return result
def get_questions_for_topic(topic_id):
    c = get_cursor()
    c.execute('''SELECT q.id, q.text, q.multiselect, q.comment,
        a.id AS ans_id, a.text AS ans_text, correct
        FROM question q
        INNER JOIN answer a ON q.id = a.question_id
        WHERE q.topic_id = %s;''', (topic_id))
    rows = c.fetchall()
    result = {}
    for row in rows:
        id = row['id']
        answer = {'id': row['ans_id'],
                'text': row['ans_text'],
                'correct': row['correct']}
        if id in result:
            result[id]['answers'].append(answer)
        else:
            result[id] = {'text': row['text'],
                        'multiselect': row['multiselect'],
                        'comment': row['comment'],
                        'answers': [answer]}
    return result

def update_answers(student_id, attempt_id, question_id, answers):
    c = get_cursor()
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
    lb = detect_linebreaks(questions)
    questions = questions.split(lb+lb+lb)
    for block in questions:
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
        for answer in answers:
            correct = answer.startswith('*')
            if correct:
                answer_text = answer.lstrip('*')
            add_answer(question_id, answer_text, correct)

def get_tests():
    c = get_cursor()
    c.execute('''SELECT id, name, final, questionCount FROM test''')
    return c.fetchall()
def delete_test(test_id):
    c = get_cursor()
    c.execute('''DELETE t, ta, qs, qsq
        FROM test t
        LEFT OUTER JOIN test_attempt ta ON t.id = ta.test_id
        LEFT OUTER JOIN question_sequence qs ON t.id = qs.test_id
        LEFT OUTER JOIN question_sequence_questions qsq ON qs.id = qs.sequence_id
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
    if final:
        students = get_students()
        for student in students:
            add_question_sequence(student['id'], test_id, topic_ids, question_count)
    else:
        add_question_sequence(None, test_id, topic_ids, question_count)

def add_question_sequence(student_id, test_id, topic_ids, question_count):
    c = get_cursor()
    c.execute('''INSERT INTO question_sequence (student_id, test_id)
        VALUES (%s, %s)''', (student_id, test_id))
    sequence_id = c.lastrowid
    topic_ids_string = ','.join(map(lambda x:str(x), topic_ids))
    c.execute('''INSERT INTO question_sequence_questions
        (sequence_id, question_id, `order`)
        SELECT %s, id, @order := @order + 1 AS `order` FROM
            ( SELECT id FROM question
            WHERE topic_id IN (''' + topic_ids_string + ''') ORDER BY RAND() LIMIT %s)
        qs, (SELECT @order := 0) o''',
        (sequence_id, question_count))

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