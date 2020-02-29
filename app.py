from flask import *
from flask_socketio import SocketIO, send, emit
import socket
import json
import time
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

	conn.commit();
except:
	conn.rollback()
	cur.close()

cur = conn.cursor()

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

@socketio.on('update_to_read')
def update_to_read (book_id, to_read):
	if (to_read == 0):
		query = "delete from ToRead where user_id = {} and book_id = {}".format(session['uid'], book_id)
	else:
		query = "insert into ToRead values({}, {})".format(session['uid'], book_id)
	cur.execute(query)
	conn.commit()

	socketio.emit('post_to_read_update')

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
	query = "select book_id from books where title = '{}'".format(title)
	cur.execute(query)
	rows = cur.fetchall()
	socketio.emit('book_id_result', rows[0][0])

@socketio.on('title_search')
def handler (title):
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
def best_rated_books ():
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


@app.route("/book_page/<id>")
def book_page(id):
	return render_template('book_page.html', user=session['uid'], book_id=id)

@app.route("/book_page")
def default():
	return render_template('book_page.html')

@app.route("/user_page")
def user_page():
	return render_template('user_page.html', user=session['uid'])

@app.route("/")
def main():
	return render_template('main.html')

@app.route("/",methods=['POST'])
def main_form():
	if request.method == 'POST':
		username=request.form['username']
		password=request.form['password']
		if (username == 'admin' and password == 'admin'):
			socketio.emit('authorized_access')
			session['uid'] = username
			return redirect(url_for('user_page'))
		(err,res) = validate(username,password)
		if(err):
			return render_template('main.html')
		else:
			socketio.emit('authorized_access')
			session['uid'] = username
			return redirect(url_for('user_page'))


@app.route('/<path:path>')
def static_file(path):
	return app.send_static_file(path)

if __name__ == "__main__":
	socketio.run(app)
