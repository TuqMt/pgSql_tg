import time
from db import get_connection

def check_subscriptions():
    conn = get_connection()
    cur = conn.cursor()


    now = int(time.time())


    cur.execute("SELECT login, date FROM tg WHERE isbuy = TRUE")
    users = cur.fetchall()

    for login, timestamp in users:
        if now - timestamp > 86400:
            cur.execute("UPDATE tg SET isbuy = FALSE WHERE login = %s", (login,))
            print(f"Подписка у пользователя {login} завершена.")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_subscriptions()
