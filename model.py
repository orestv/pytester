import MySQLdb

def get_cursor():
    db = MySQLdb.connect(db='tests', user='root', passwd='sdntvFreud', charset='utf8', use_unicode=True)
    return db.cursor(MySQLdb.cursors.DictCursor)

def get_student(firstname, lastname):
    c = get_cursor()
    c.execute('SELECT id, hash FROM student WHERE firstname = %s AND lastname = %s', (firstname, lastname))
    return c.fetchone()

def get_student_info(id):
    c = get_cursor()
    c.execute('SELECT id, firstname, lastname, hash FROM student WHERE id = %s', (id))
    return c.fetchone()

def get_student_test_attempts(id):
    c = get_cursor()
    c.execute('''SELECT t.id, t.name, ta.start, ta.end
        FROM test_attempt ta
        INNER join test t ON ta.test_id = t.id
        WHERE ta.student_id = %s
        ORDER BY ta.start DESC''', (id))
    return c.fetchall()

def get_student_available_tests(id):
    c = get_cursor()
    c.execute('''SELECT DISTINCT (test.id), test.name AS name,
        MAX(ta.result) AS result, COUNT(DISTINCT qsq.question_id) AS maxresult FROM test
        LEFT OUTER JOIN test_attempt ta ON ta.test_id = test.id
            AND ta.student_id = %s
        INNER JOIN question_sequence qs
            ON qs.test_id = test.id AND (qs.student_id = %s OR qs.student_id IS NULL)
        INNER JOIN question_sequence_questions qsq
            ON qsq.sequence_id = qs.id
        GROUP BY test.id, qs.id''', (id, id))
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

def get_topics():
    c = get_cursor()
    c.execute('''SELECT id, name FROM topic''')
    return c.fetchall()