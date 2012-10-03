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
    c.execute('''SELECT t.name, ta.start, ta.end
        FROM test_attempt ta
        INNER join test t ON ta.test_id = t.id
        WHERE ta.student_id = %s''', (id))
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

def get_questions_for_test(test_id, student_id):
    c = get_cursor()
    c.execute('''SELECT q.id AS id, q.text AS text FROM question_sequence qs
        INNER JOIN question_sequence_questions qsq
            ON qs.id = qsq.sequence_id
        INNER join question q
            ON qsq.question_id = q.id
        WHERE qs.test_id = %s AND (qs.student_id = %s OR ISNULL(qs.student_id) = 1)
        ORDER BY qsq.order ASC;''', (test_id, student_id))
    return c.fetchall()