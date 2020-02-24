DROP DATABASE IF EXISTS goodbooks;
CREATE DATABASE goodbooks;
\c goodbooks;

CREATE TABLE Books (
    book_id int,
    goodreads_book_id int NOT NULL,
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

CREATE TABLE Tags (
    tag_id int,
    tag_name text UNIQUE NOT NULL,
    PRIMARY KEY (tag_id)
);

CREATE TABLE Ratings (
    user_id int,
    book_id int REFERENCES Books(book_id),
    rating smallint CHECK (rating >= 1 AND rating <= 5),
    PRIMARY KEY (user_id, book_id)
);

CREATE TABLE BookTags (
    goodreads_book_id int,
    tag_id int REFERENCES Tags(tag_id),
    count int CHECK(count = -1 OR count > 0),
    PRIMARY KEY (goodreads_book_id, tag_id)
);

CREATE TABLE ToRead (
    user_id int,
    book_id int,
    PRIMARY KEY (user_id, book_id)
);

\COPY Books FROM './goodbooks-10k/books.csv' DELIMITER ',' CSV HEADER;
\COPY Ratings FROM './goodbooks-10k/ratings.csv' DELIMITER ',' CSV HEADER;
\COPY Tags FROM './goodbooks-10k/tags.csv' DELIMITER ',' CSV HEADER;
\COPY BookTags FROM './goodbooks-10k/book_tags_.csv' DELIMITER ',' CSV HEADER;
\COPY ToRead FROM './goodbooks-10k/to_read.csv' DELIMITER ',' CSV HEADER;


-- DROP TABLE badges;
-- DROP TABLE comments;
-- DROP TABLE linktypes;
-- DROP TABLE postlinks;
-- DROP TABLE posts;
-- DROP TABLE posttypes;
-- DROP TABLE users;
-- DROP TABLE votes;