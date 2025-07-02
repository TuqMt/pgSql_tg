from flask import Flask, request, render_template
from db import get_connection

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        login = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM website WHERE login = %s AND password = %s", (login, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            isbuy = user[2]
            if isbuy:
                message = "Подписка активна"
            else:
                message = "Подписка не активна"
        else:
            message = "Неверный логин или пароль"

    return render_template("log.html", message=message)

if __name__ == "__main__":
    app.run(debug=True)