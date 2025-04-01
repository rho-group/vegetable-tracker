from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta

# 🔹 Yhteys PostgreSQL:ään Azurella
DB_HOST = "vegetable-db-server.postgres.database.azure.com"
DB_NAME = "postgres"
DB_USER = "rhoAdmin"
DB_PASSWORD = "Password"

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )

app = FastAPI()

@app.post("/add_food/")
def add_food(user_id: int, food_name: str):
    conn = get_db_connection()
    cur = conn.cursor()

    # Tarkista, onko ruoka jo tietokannassa
    cur.execute("SELECT id FROM foods WHERE name = %s", (food_name,))
    food = cur.fetchone()

    if not food:
        cur.execute("INSERT INTO foods (name) VALUES (%s) RETURNING id", (food_name,))
        food_id = cur.fetchone()["id"]
    else:
        food_id = food["id"]

    # Lisää käyttäjän syömä ruoka
    cur.execute("INSERT INTO user_foods (user_id, food_id) VALUES (%s, %s)", (user_id, food_id))
    conn.commit()
    conn.close()

    return {"message": f"{food_name} added!"}

@app.get("/recent_foods/")
def get_recent_foods(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()

    # Hae viimeisen 7 päivän aikana syödyt ruoka-aineet
    week_ago = datetime.now() - timedelta(days=7)
    cur.execute("""
        SELECT DISTINCT f.name FROM user_foods uf
        JOIN foods f ON uf.food_id = f.id
        WHERE uf.user_id = %s AND uf.eaten_at > %s
    """, (user_id, week_ago))

    foods = [row["name"] for row in cur.fetchall()]
    conn.close()

    return {"recent_foods": foods}
