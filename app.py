from flask import *
from flask_socketio import SocketIO, send, emit
import socket
import json
import time
import random
import string
import psycopg2

app = Flask(__name__,
			static_url_path='',
			static_folder='static',
			template_folder='templates')

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# conn = psycopg2.connect("dbname=group_10 user=group_10 host=10.17.50.134 port=5432 password=815-685-329")
conn = psycopg2.connect("dbname=group_10 user=postgres host=localhost port=5433 password=postgres")


try:
	cur = conn.cursor()

	cur.execute("drop trigger RatingDelete on Ratings;")
	cur.execute("CREATE TRIGGER RatingDelete AFTER DELETE ON Ratings FOR EACH ROW EXECUTE FUNCTION delete();")
	cur.execute("""CREATE OR REPLACE FUNCTION delete()
	RETURNS TRIGGER AS $$
	BEGIN
		UPDATE Books
		SET ratings_count = ratings_count - 1, 
		ratings_1 = CASE WHEN OLD.rating = 1 THEN ratings_1 - 1 ELSE ratings_1 END,
		ratings_2 = CASE WHEN OLD.rating = 2 THEN ratings_2 - 1 ELSE ratings_2 END,
		ratings_3 = CASE WHEN OLD.rating = 3 THEN ratings_3 - 1 ELSE ratings_3 END,
		ratings_4 = CASE WHEN OLD.rating = 4 THEN ratings_4 - 1 ELSE ratings_4 END,
		ratings_5 = CASE WHEN OLD.rating = 5 THEN ratings_5 - 1 ELSE ratings_5 END,
		average_rating = (average_rating*(ratings_count + 1) - OLD.rating)/ratings_count
		WHERE book_id = OLD.book_id;

		RETURN NEW;
	END; $$ LANGUAGE 'plpgsql'; """)

	cur.execute("""CREATE OR REPLACE FUNCTION update()
	RETURNS TRIGGER AS $$
	BEGIN
		UPDATE Books
		SET ratings_1 = CASE WHEN NEW.rating = 1 THEN ratings_1 + 1 WHEN OLD.rating = 1 THEN ratings_1 - 1 ELSE ratings_1 END,
		ratings_2 = CASE WHEN NEW.rating = 2 THEN ratings_2 + 1 WHEN OLD.rating = 2 THEN ratings_2 - 1 ELSE ratings_2 END,
		ratings_3 = CASE WHEN NEW.rating = 3 THEN ratings_3 + 1 WHEN OLD.rating = 3 THEN ratings_3 - 1 ELSE ratings_3 END,
		ratings_4 = CASE WHEN NEW.rating = 4 THEN ratings_4 + 1 WHEN OLD.rating = 4 THEN ratings_4 - 1 ELSE ratings_4 END,
		ratings_5 = CASE WHEN NEW.rating = 5 THEN ratings_5 + 1 WHEN OLD.rating = 5 THEN ratings_5 - 1 ELSE ratings_5 END,
		average_rating = (average_rating*ratings_count - OLD.rating + NEW.rating)/ratings_count
		WHERE book_id = NEW.book_id;

		RETURN NEW;
	END; $$ LANGUAGE 'plpgsql';""")

	cur.execute("DROP MATERIALIZED VIEW Authors;")
	cur.execute("""CREATE MATERIALIZED VIEW Authors AS (select ath as author, sum(average_rating*ratings_count)/sum(ratings_count) as rating, 
					count(book_id) as num_books, sum(ratings_count) as review_count 
					from (select *, regexp_split_to_table(authors, ', ') as ath from books) as t1 group by ath) 
					order by review_count desc, rating desc;""")


	conn.commit();
except:
	conn.rollback()
	cur.close()

cur = conn.cursor()
cur.execute("select count(user_id) from users")
signup_user_id = cur.fetchall()[0][0] + 1
print(signup_user_id)

def validate(username, passkey):
	query = "select count(user_id) from users where user_id = {} and password = '{}'".format(username, passkey)
	cur.execute(query)
	rows = cur.fetchall()
	if (rows[0][0] == 1):
		print("LOGIN SUCCESSFULL!")
		return (False, None)
	else:		
		print("INVALID CREDENTIALS!")
		return (True, None)

def randomString(stringLength=10):
	"""Generate a random string of fixed length """
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(stringLength))

@socketio.on('update_to_read')
def update_to_read (book_id, to_read):
	if (to_read == 0):
		query = "delete from ToRead where user_id = {} and book_id = {}".format(session['uid'], book_id)
	else:
		query = "insert into ToRead values({}, {})".format(session['uid'], book_id)
	cur.execute(query)
	conn.commit()

	socketio.emit('post_to_read_update')

@socketio.on('signup_request')
def signup_request ():
	global signup_user_id
	password = randomString()
	query = "insert into users values({}, '{}')".format(signup_user_id, password)
	cur.execute(query)
	conn.commit()
	l = []
	l.append(signup_user_id)
	l.append(password)
	socketio.emit('signed_up', l)
	signup_user_id += 1

@socketio.on('change_password_request')
def change_password_request (password):
	query = "update users set password = '{}' where user_id = {}".format(password, session['uid'])
	cur.execute(query)
	conn.commit()

	socketio.emit('password_updated')

@socketio.on('logout_request')
def logout_request ():
	socketio.emit('logged_out')

@socketio.on('update_rating')
def update_rating (book_id, rate, flag):
	if (flag == 2):
		query = "delete from ratings where user_id={} and book_id={}".format(session['uid'], book_id)
	elif (flag == 1):
		query = "insert into ratings values({}, {}, {})".format(session['uid'], book_id, rate)
	else:
		query = "update ratings set rating = {} where book_id = {} and user_id = {}".format(rate, book_id, session['uid'])

	cur.execute(query)
	conn.commit()
	socketio.emit('post_rating_update')


@socketio.on('book_page_request')
def book_page_request_handler(title):
	title = title.replace("'", "''")
	query = "select book_id from books where title='{}'".format(title)
	cur.execute(query)
	rows = cur.fetchall()
	socketio.emit('book_page_result', rows[0][0])

@socketio.on('author_page_request')
def author_page_request_handler(author):
	author = author.replace("'", "''")
	socketio.emit('author_page_result', author)

@socketio.on('title_search')
def handler (title):
	title = title.replace("'", "''")
	query = "select title from books where title = '{}'".format(title)
	cur.execute(query)
	rows = cur.fetchall()
	socketio.emit('title_search_result', rows)

@socketio.on('best_rated_books')
def best_rated_books ():
	query = "select title from books order by average_rating desc limit 30"
	cur.execute(query)
	rows = cur.fetchall()
	socketio.emit('best_rated_books_result', rows)

@socketio.on('best_rated_authors')
def best_rated_authors ():
	query = "select author from authors order by rating desc limit 30"
	cur.execute(query)
	rows = cur.fetchall()
	socketio.emit('best_rated_authors_result', rows)

@socketio.on('most_read_books')
def most_read_books ():
	query = "select title from books order by ratings_count desc limit 30"
	cur.execute(query)
	rows = cur.fetchall()
	socketio.emit('most_read_books_result', rows)

@socketio.on('most_popular_authors')
def most_popular_authors ():
	query = "select author from authors order by review_count desc limit 30"
	cur.execute(query)
	rows = cur.fetchall()
	socketio.emit('most_popular_authors_result', rows)

@socketio.on('most_active_users')
def most_active_users ():
	query = "select user_id from ratings group by user_id order by count(rating) desc limit 30"
	cur.execute(query)
	rows = cur.fetchall()
	socketio.emit('most_active_users_result', rows)

@socketio.on('most_recent_books')
def most_recent_books ():
	query = "select title from books where original_publication_year is not null order by original_publication_year desc, title limit 30"
	cur.execute(query)
	rows = cur.fetchall()
	socketio.emit('most_recent_books_result', rows)

@socketio.on('to_read')
def to_read ():
	query = "select title from books, toread where user_id={} and toread.book_id=books.book_id order by title".format(session['uid'])
	cur.execute(query)
	rows = cur.fetchall()
	socketio.emit('to_read_result', rows)

@socketio.on('rated_books')
def rated_books ():
	query = "select title from books, ratings where user_id={} and ratings.book_id=books.book_id order by rating desc, title".format(session['uid'])
	cur.execute(query)
	rows = cur.fetchall()
	socketio.emit('rated_books_result', rows)

@socketio.on('author_search')
def author_search (author):
	author = author.replace("'", "''")

	query = "select title from books, (select book_id, regexp_split_to_table(authors, ', ') as ath from books) as t1 where books.book_id = t1.book_id and t1.ath = '{}'".format(author)
	cur.execute(query)
	rows = cur.fetchall()
	socketio.emit('author_search_result', rows)

@socketio.on('year_search')
def year_search (year):
	query = "select title from books where original_publication_year = '{}' order by average_rating desc limit 100".format(year)
	cur.execute(query)
	rows = cur.fetchall()
	socketio.emit('year_search_result', rows)

@socketio.on('tag_search')
def tag_search (tag):
	query = "select title from books, BookTags, tags where tags.tag_name = '{}' and tags.tag_id = BookTags.tag_id and books.goodreads_book_id = booktags.goodreads_book_id order by average_rating desc limit 100".format(tag)
	cur.execute(query)
	rows = cur.fetchall()
	socketio.emit('tag_search_result', rows)

@socketio.on('isbn_search')
def isbn_search (isbn13):
	query = "select title from books where isbn13 = '{}'".format(isbn13)
	cur.execute(query)
	rows = cur.fetchall()
	socketio.emit('isbn_search_result', rows)

@socketio.on('advanced_search')
def advanced_search(q):
	title = q[0];
	author = q[1];
	years = q[2].split(',')
	year_1 = years[0];
	year_2 = years[1];
	rates = q[3].split(',')
	rate_1 = rates[0]
	rate_2 = rates[1]

	print(q)
	query = "select title from books where true"
	if (len(title) != 0):
		query += " and title like '%{}%'".format(title)

	if (len(author) != 0):
		query += " and authors like '%{}%'".format(author)

	if (len(year_1) != 0):
		year_1 = int(year_1)
		query += " and original_publication_year > {} ".format(year_1)

	if (len(year_2) != 0):
		year_2 = int(year_2)
		query += " and original_publication_year < {}".format(year_2)

	if (len(rate_1) != 0):
		rate_1 = float(rate_1)
		query += "and average_rating > {}".format(rate_1)

	if (len(rate_2) != 0):
		rate_2 = float(rate_2)
		query += "and average_rating < {}".format(rate_2)

	print(query)
	cur.execute(query)
	rows = cur.fetchall()
	socketio.emit('advanced_search_result', rows)

@socketio.on('get_book_details')
def book_details(id):
	query = "select title,authors,original_publication_year,isbn,language_code,average_rating,ratings_count,ratings_1,ratings_2,ratings_3,ratings_4,ratings_5,image_url, goodreads_book_id from books where book_id = {}".format(id)
	cur.execute(query)
	rows = cur.fetchall()
	rows = list(rows[0])
	rows[2] = int(rows[2])
	rows[5] = float(rows[5])
	
	query = "select tag_name from Tags, BookTags where goodreads_book_id = {} and BookTags.tag_id = Tags.tag_id order by count desc limit 15".format(rows[13])
	cur.execute(query)
	tags = cur.fetchall()
	rows.append(tags)

	query = "select rating from ratings where user_id={} and book_id={}".format(session['uid'], id)
	cur.execute(query)
	rate = cur.fetchall()
	if (cur.rowcount == 0):
		rows.append(-1)
	else:
		rows.append(rate[0][0])

	query = "select * from ToRead where user_id={} and book_id={}".format(session['uid'], id)
	cur.execute(query)
	rows.append(cur.rowcount)

	socketio.emit('book_details', rows)

@socketio.on('get_author_details')
def author_details(author_id):
	author_id = author_id.replace("%20", ' ');
	query = "select * from authors where author = '{}'".format(author_id)
	cur.execute(query)
	rows = cur.fetchall()
	print(query)
	rows = list(rows[0])
	rows[1] = float(rows[1])

	query = "select title, image_url, count(user_id) from toread, books, (select book_id, regexp_split_to_table(authors, ', ') as ath from books) as t1 where toread.book_id = books.book_id and books.book_id = t1.book_id and t1.ath = '{}' group by books.book_id, toread.book_id order by average_rating desc".format(author_id)
	cur.execute(query)
	books = cur.fetchall()

	rows.append(books)
	socketio.emit('author_details', rows)

@socketio.on('get_tag_names')
def get_tag_names():
	query = "select tag_name from tags, booktags where tags.tag_id = booktags.tag_id group by tags.tag_id, booktags.tag_id order by sum(booktags.count) desc limit 500"
	cur.execute(query)
	rows = cur.fetchall()
	socketio.emit('tag_names', rows)

@socketio.on('add_book_request')
def add_book_handler(q):
	print(q)
	flag = True
	cur.execute("select max(book_id) from books")
	book_id = cur.fetchall()[0][0] + 1   
	if(q['goodreads_book_id'] == '' or q['isbn']== '' or q['isbn13']== '' or q['authors']== '' or q['original_publication_year']== '' or q['title']== '' or q['language']== '' or q['image_url']== ''):
		flag = False
		print("Not adding book")
	if(flag):
		query = "insert into books values({}, {}, {}, 0, 1, '{}', {}, '{}', {}, '{}', '{}', '{}', 3, 1, 0, 0, 0, 0, 1, 0, 0, '{}', '{}')".format(
					book_id, int(q['goodreads_book_id']), int(q['goodreads_book_id']), q['isbn'], int(q['isbn13']), q['authors'], int(q['original_publication_year']), q['title'], q['title'], q['language'], q['image_url'], q['image_url'])
		print(query)
		cur.execute(query)
		conn.commit()
	socketio.emit('book_request_result', flag)

@socketio.on('add_tag_request')
def add_tag_handler(q):
	cur.execute("select tag_id from tags where tag_name='{}'".format(q['tag_name']))
	tag_id = cur.fetchall()[0][0]
	cur.execute("select * from booktags where tag_id={} and goodreads_book_id={}".format(tag_id,int(q['goodreads_book_id'])))
	if(cur.rowcount==0):
		query = "insert into booktags values({},{},1)".format(int(q['goodreads_book_id']),tag_id)
		cur.execute(query)
		conn.commit()
	print("executed")
	socketio.emit('tag_added')

@app.route("/author_page/<id>")
def author_page(id):
	return render_template('author_page.html', user=session['uid'], author_id=id)

@app.route("/book_page/<id>")
def book_page(id):
	return render_template('book_page.html', user=session['uid'], book_id=id)

@app.route("/book_page")
def default():
	return render_template('book_page.html')

@app.route("/admin_page")
def admin_page():
	if (session['uid'] == 'admin'):
		return render_template('admin_page.html', user=session['uid'])
	else:
		abort(404)

@app.route("/user_page")
def user_page():
	return render_template('user_page.html', user=session['uid'])

@app.route("/")
def main():
	return render_template('main.html')

@app.errorhandler(404)
def page_not_found(error):
	return render_template_string("INVALID URL REQUEST")


@app.route("/",methods=['POST'])
def main_form():
	if request.method == 'POST':
		username=request.form['username']
		password=request.form['password']
		if (username == 'admin' and password == 'admin'):
			socketio.emit('authorized_access')
			session['uid'] = username
			return redirect(url_for('admin_page'))
		(err,res) = validate(username,password)
		if(err):
			return render_template('main.html')
		else:
			socketio.emit('authorized_access')
			session['uid'] = username
			return redirect(url_for('user_page'))

if __name__ == "__main__":
	socketio.run(app)
