from flask import Flask, request
import psycopg2
import os

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST"),
        database=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        port=5432
    )

@app.route("/")
def home():
    return "Welcome to our DevOps project!"

@app.route("/health")
def health():
    return {"status": "healthy"}

@app.route("/db-health")
def db_health():
    try:
        conn = get_db_connection()
        conn.close()
        return {"database": "connected"}
    except Exception as e:
        return {"database": "error", "message": str(e)}, 500

@app.route("/users", methods=["GET"])
def get_users():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name, email FROM users;")
    rows = cur.fetchall()

    users = []
    for row in rows:
        users.append({
            "id": row[0],
            "name": row[1],
            "email": row[2]
        })

    cur.close()
    conn.close()

    return users

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id;",
        (name, email)
    )

    user_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return {
        "message": "User created successfully",
        "id": user_id,
        "name": name,
        "email": email
    }, 201

@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET name = %s, email = %s WHERE id = %s RETURNING id;",
        (name, email, user_id)
    )

    updated_user = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    if updated_user is None:
        return {"message": "User not found"}, 404

    return {
        "message": "User updated successfully",
        "id": user_id,
        "name": name,
        "email": email
    }, 200


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM users WHERE id = %s RETURNING id, name;",
        (user_id,)
    )

    deleted_user = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    if deleted_user is None:
        return {"message": "User not found"}, 404

    return {
        "message": "User deleted successfully",
        "id": deleted_user[0],
        "name": deleted_user[1]
    }, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)