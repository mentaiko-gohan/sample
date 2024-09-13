#以下を確認しながら整備する
from flask import Flask ,request ,render_template,redirect
from flask_cors import CORS
from flask_login import LoginManager ,UserMixin ,login_user ,logout_user ,login_required
import mysql.connector

app = Flask(__name__)
CORS(app)

# セッション情報（クッキー）の暗号化キー設定
app.secret_key = "recore.aoc"
# FlaskLoginの初期化
login_manager = LoginManager()
login_manager.init_app(app)

# ユーザー管理用クラス
class User(UserMixin):
   def __init__(self,id):
      self.id = id

# セッション（クッキー）からのユーザー検証用ハンドラ
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

#プロフィール画面への遷移
@app.route("/profile")
def profile():
    return render_template("/profile.html")

#限定コンテンツ側からのhome画面への遷移
@app.route("/signin.sec2")
def signinsec2():
    return render_template("/home.html",target_id="section2")
@app.route("/signin.sec3")
def signinsec3():
    return render_template("/home.html",target_id="section3")

# サインインの実施
@app.route("/signin" ,methods=["GET" ,"POST"])
def signin():
    if request.method == "GET":
        # GETの場合はサインインページを表示
        return render_template("/home.html")
    
    # POST（フォームhome.htmlからのポスト）の場合
    conn = mysql.connector.connect(host='localhost', user='funa', password='funa', database='portfolio')
    curs = conn.cursor(dictionary=True)

    curs.execute("select email ,cast(aes_decrypt(password, 'funa') as char) pwd from user where email = %s",( request.form["email"], ))
    ds = curs.fetchall()
    curs.close()
    conn.close()

    if len(ds)>0 and request.form["password"]==ds[0]["pwd"]:
        login_user(User(request.form["email"]))

        # Create connection.
        conn = mysql.connector.connect(host='localhost', user='funa', password='funa', database='portfolio')
        curs = conn.cursor(dictionary=True)
        # Create cursor and close.
        curs.execute('select * from limited')
        ds = curs.fetchall()
        curs.close()

        # Close connection.
        conn.close()

        #return name
        #return jsonify({'status':'OK' ,'dataset':ds})
        return render_template('limited.html', title='限定コンテンツ', dataset=ds)

        #return render_template("/limited.html")

    return render_template("/home.html",target_id="inputBox",errormessage="ログインに失敗しました")

# サインアップの実施
@app.route("/signup" ,methods=["GET" ,"POST"])
def signup():
    if request.method == "GET":
        # GETの場合はサインインページを表示
        return render_template("/signup.html")
    
    # POST（フォームsignin.htmlからのポスト）の場合
    conn = mysql.connector.connect(host='localhost', user='funa', password='funa', database='portfolio')
    curs = conn.cursor(dictionary=True)

    #登録済みのメールアドレスを入力した場合、エラーメッセージを返す
    sql = "select * from user where email = %s"
    curs.execute(sql,(request.form["email"],))
    ds = curs.fetchall()
    if len(ds)==1:
        return render_template("/signup.html",errormessage2="既に登録済みのメールアドレスです。")

    #新規登録が出来た場合、登録完了画面へ遷移
    sql = "insert into user (email, password) values (%s, aes_encrypt(%s, 'funa'))"
    curs.execute(sql , (request.form["email"] ,request.form["password"]))
    conn.commit()
    curs.close()
    conn.close()

    login_user(User(request.form["email"]))
    
    return render_template("/fin.html")

# ログアウトの実施
@app.route("/signout")
def signout():
    logout_user()
    return "Signout完了"

# ログイン（認証）が必要なページの表示
@app.route("/issignin")
@login_required
def issignin():
    return "認証済です"

if __name__ == "__main__":
    app.run(host="0.0.0.0" ,port=8900 ,debug=True)
