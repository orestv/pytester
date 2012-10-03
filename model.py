import MySQLdb

def get_cursor():
	db = MySQLdb.connect(db='tests', user='root', passwd='sdntvFreud', charset='utf8', use_unicode=True)
	return db.cursor(MySQLdb.cursors.DictCursor)

def get_student_hash(firstname, lastname):
	c = get_cursor()
	c.execute('SELECT hash FROM student WHERE firstname = \'%s\' AND lastname = \'%s\''%(firstname, lastname))
	return c.fetchone()

def get_student_info(student_hash):
	c = get_cursor()
	c.execute('SELECT id, firstname, lastname FROM student WHERE hash = \'%s\'' % student_hash)
	return c.fetchone()