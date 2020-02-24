import csv
import psycopg2

try:
    conn = psycopg2.connect("dbname=postgres user=postgres host=localhost port=5433 password=postgres")
except:
    print ("Unable to connect to the database")

cur = conn.cursor()

cur.execute("")

rows = cur.fetchall()