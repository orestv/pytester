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
	c.execute('SELECT firstname, lastname FROM student WHERE id = %s', (id))
	return c.fetchone()

def get_student_test_attempts(id):
	c = get_cursor()
	c.execute('''SELECT t.name, ta.start, ta.end
		FROM test_attempt ta
		INNER join test t ON ta.test_id = t.id
		WHERE ta.student_id = %s''', (id))
	return c.fetchall()