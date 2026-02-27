import psycopg

conn = psycopg.connect(
    host="127.0.0.1",
    port=5433,
    user="admin",
    password="admin",
    dbname="users_db"
)

print("Conexion OK")
conn.close()