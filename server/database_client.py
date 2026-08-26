import psycopg

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
                cur.execute("SELECT id, username, color FROM users")
                rows = cur.fetchall()
                return [{"id": row[0], "username": row[1], "color": row[2]} for row in rows]

    def get_user(self, user_id: int):
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, username, color FROM users WHERE id = %s", (user_id,))
                row = cur.fetchone()
                if row:
                    return {"id": row[0], "username": row[1], "color": row[2]}
                else:
                    return None