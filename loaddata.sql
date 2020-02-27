DROP DATABASE IF EXISTS group_10;
CREATE DATABASE group_10;
\c group_10;

CREATE TABLE Books (
    book_id int,
    goodreads_book_id int UNIQUE NOT NULL,
    best_book_id int NOT NULL,
    work_id int NOT NULL,
    books_count int NOT NULL CHECK (books_count >= 0),
    isbn varchar(20),
    isbn13 decimal,
    authors text NOT NULL,
    original_publication_year decimal CHECK (original_publication_year <= 2020),
    original_title text,
    title text NOT NULL,
    language_code text,
    average_rating decimal NOT NULL CHECK (average_rating >= 1 AND average_rating <= 5),
    ratings_count int NOT NULL CHECK (ratings_count >= 0),
    work_ratings_count int NOT NULL CHECK (ratings_count >= 0),
    work_text_reviews_count int NOT NULL CHECK (ratings_count >= 0),
    ratings_1 int NOT NULL CHECK (ratings_count >= 0),
    ratings_2 int NOT NULL CHECK (ratings_count >= 0),
    ratings_3 int NOT NULL CHECK (ratings_count >= 0),
    ratings_4 int NOT NULL CHECK (ratings_count >= 0),
    ratings_5 int NOT NULL CHECK (ratings_count >= 0),
    image_url text NOT NULL,
    small_image_url text NOT NULL,
    PRIMARY KEY (book_id)
);

CREATE TABLE Users (
    user_id int,
    password text NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE Tags (
    tag_id int,
    tag_name text UNIQUE NOT NULL,
    PRIMARY KEY (tag_id)
);

CREATE TABLE Ratings (
    user_id int REFERENCES Users(user_id),
    book_id int REFERENCES Books(book_id) ON DELETE CASCADE,
    rating smallint CHECK (rating >= 1 AND rating <= 5),
    PRIMARY KEY (user_id, book_id)

);

CREATE TABLE BookTags (
    goodreads_book_id int REFERENCES Books(goodreads_book_id) ON DELETE CASCADE,
    tag_id int REFERENCES Tags(tag_id),
    count int CHECK(count = -1 OR count > 0),
    PRIMARY KEY (goodreads_book_id, tag_id)
);

CREATE TABLE ToRead (
    user_id int REFERENCES Users(user_id),
    book_id int REFERENCES Books(book_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, book_id)
);

\COPY Books FROM './goodbooks-10k/books.csv' DELIMITER ',' CSV HEADER;
\COPY Users FROM './goodbooks-10k/users.csv' DELIMITER ',' CSV HEADER;
\COPY Ratings FROM './goodbooks-10k/ratings.csv' DELIMITER ',' CSV HEADER;
\COPY Tags FROM './goodbooks-10k/tags.csv' DELIMITER ',' CSV HEADER;
\COPY BookTags FROM './goodbooks-10k/book_tags.csv' DELIMITER ',' CSV HEADER;
\COPY ToRead FROM './goodbooks-10k/to_read.csv' DELIMITER ',' CSV HEADER;

CREATE INDEX Books_title_index ON Books(title);

CREATE MATERIALIZED VIEW Authors AS (select ath as author, sum(average_rating*ratings_count)/sum(ratings_count) as rating, count(book_id) as num_books, sum(ratings_count) as review_count from (select *, regexp_split_to_table(authors, ',') as ath from books) as t1 group by ath) order by review_count desc, rating desc;

CREATE OR REPLACE FUNCTION insert()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE Books
    SET ratings_count = ratings_count + 1, 
    ratings_1 = CASE WHEN NEW.rating = 1 THEN ratings_1 + 1 ELSE ratings_1 END,
    ratings_2 = CASE WHEN NEW.rating = 2 THEN ratings_2 + 1 ELSE ratings_2 END,
    ratings_3 = CASE WHEN NEW.rating = 3 THEN ratings_3 + 1 ELSE ratings_3 END,
    ratings_4 = CASE WHEN NEW.rating = 4 THEN ratings_4 + 1 ELSE ratings_4 END,
    ratings_5 = CASE WHEN NEW.rating = 5 THEN ratings_5 + 1 ELSE ratings_5 END,
    average_rating = (average_rating*(ratings_count - 1) + NEW.rating)/ratings_count
    WHERE book_id = NEW.book_id;

    RETURN NEW;
END; $$ LANGUAGE 'plpgsql';

CREATE TRIGGER RatingInsert
    AFTER INSERT ON Ratings
    FOR EACH ROW
    EXECUTE FUNCTION insert();

CREATE OR REPLACE FUNCTION delete()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE Books
    SET ratings_count = ratings_count - 1, 
    ratings_1 = CASE WHEN NEW.rating = 1 THEN ratings_1 - 1 ELSE ratings_1 END,
    ratings_2 = CASE WHEN NEW.rating = 2 THEN ratings_2 - 1 ELSE ratings_2 END,
    ratings_3 = CASE WHEN NEW.rating = 3 THEN ratings_3 - 1 ELSE ratings_3 END,
    ratings_4 = CASE WHEN NEW.rating = 4 THEN ratings_4 - 1 ELSE ratings_4 END,
    ratings_5 = CASE WHEN NEW.rating = 5 THEN ratings_5 - 1 ELSE ratings_5 END,
    average_rating = (average_rating*(ratings_count + 1) - OLD.rating)/ratings_count
    WHERE book_id = NEW.book_id;

    RETURN NEW;
END; $$ LANGUAGE 'plpgsql';

CREATE TRIGGER RatingDelete
    AFTER INSERT ON Ratings
    FOR EACH ROW
    EXECUTE FUNCTION delete();

CREATE OR REPLACE FUNCTION update()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE Books
    SET ratings_1 = CASE WHEN NEW.rating = 1 THEN ratings_1 + 1 WHEN OLD.rating = 1 THEN ratings_1 = ratings_1 - 1 ELSE ratings_1 END,
    ratings_2 = CASE WHEN NEW.rating = 2 THEN ratings_2 + 1 WHEN OLD.rating = 2 THEN ratings_2 = ratings_2 - 1 ELSE ratings_2 END,
    ratings_3 = CASE WHEN NEW.rating = 3 THEN ratings_3 + 1 WHEN OLD.rating = 3 THEN ratings_3 = ratings_3 - 1 ELSE ratings_3 END,
    ratings_4 = CASE WHEN NEW.rating = 4 THEN ratings_4 + 1 WHEN OLD.rating = 4 THEN ratings_4 = ratings_4 - 1 ELSE ratings_4 END,
    ratings_5 = CASE WHEN NEW.rating = 5 THEN ratings_5 + 1 WHEN OLD.rating = 5 THEN ratings_5 = ratings_5 - 1 ELSE ratings_5 END,
    average_rating = (average_rating*ratings_count - OLD.rating + NEW.rating)/ratings_count
    WHERE book_id = NEW.book_id;

    RETURN NEW;
END; $$ LANGUAGE 'plpgsql';

CREATE TRIGGER RatingUpdate
    AFTER UPDATE ON Ratings
    FOR EACH ROW
    EXECUTE FUNCTION update();