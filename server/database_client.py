import psycopg
from data_types import User

class DatabaseClient:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connection = None

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def put_message(self, message: dict):
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO messages (content, user_id) VALUES (%s, %s)",
                    (message['content'], message['user_id'])
                )
                conn.commit()

    def get_messages(self):
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, content, user_id FROM messages")
                rows = cur.fetchall()
                return [{"id": row[0], "content": row[1], "user_id": row[2]} for row in rows]

    def put_user(self, user: dict):
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, color) VALUES (%s, %s)",
                    (user['username'], user['color'])
                )
                conn.commit()

    def get_users(self):
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, username, color, logged_in FROM users")
                rows = cur.fetchall()
                return [{"id": row[0], "username": row[1], "color": row[2], "logged_in": row[3]} for row in rows]

    def get_user(self, user_id: int):
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, username, color, logged_in FROM users WHERE id = %s", (user_id,))
                row = cur.fetchone()
                if row:
                    return User(id=row[0], username=row[1], color=row[2], logged_in=row[3])
                    # return {"id": row[0], "username": row[1], "color": row[2], "logged_in": row[3]}
                else:
                    return None

    def get_user_by_username(self, username: str):
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, username, color, logged_in FROM users WHERE username = %s", (username,))
                row = cur.fetchone()
                if row:
                    print(row)  # Debugging line to print the fetched row
                    return {"id": row[0], "username": row[1], "color": row[2], "logged_in": row[3]}
                else:
                    return None

    def login_user(self, user_id: int):
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET logged_in = TRUE WHERE id = %s", (user_id,))
                conn.commit()

    def logout_user(self, user_id: int):
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET logged_in = FALSE WHERE id = %s", (user_id,))
                conn.commit()