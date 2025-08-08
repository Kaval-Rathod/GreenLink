import os
import psycopg2
conn = psycopg2.connect("host=localhost dbname=greenlink user=admin password=admin port=5432")
cur = conn.cursor()
cur.execute("SELECT 1;")
print(cur.fetchone())
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public';")
print(cur.fetchall())
cur.close()
conn.close()
