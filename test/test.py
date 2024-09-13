from flask import Flask ,request ,render_template
import mysql.connector

app = Flask(__name__)

# サインインの実施
from flask import Flask ,request ,render_template
import mysql.connector

app = Flask(__name__)

# サインインの実施
@app.route("/signin" ,methods=["GET" ,"POST"])
def signin():
    if request.method == "GET":
        # GETの場合はサインインページを表示
        return render_template("/signin1.html")
    
    # POST（フォームsignin.htmlからのポスト）の場合
    conn = mysql.connector.connect(host='localhost', user='funa', password='funa', database='test')
    curs = conn.cursor(dictionary=True)

    curs.execute("select email from user1 where email = %s" ,(request.form["email"],))
    ds = curs.fetchall()
    curs.close()
    conn.close()

    return "Signin失敗"

if __name__ == "__main__":
    app.run(host="0.0.0.0" ,port=8888 ,debug=True)