from flask import Flask ,request ,render_template,session,redirect
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

# サインインの実施
@app.route("/login" ,methods=["GET" ,"POST"])
def signin():
    if request.method == "GET":
        # GETの場合はサインインページを表示
        return render_template("/login.html")
    
    # POST（フォームsignin.htmlからのポスト）の場合
    conn = mysql.connector.connect(host='localhost', user='funa', password='funa', database='merchandise')
    curs = conn.cursor(dictionary=True)
    # .execute＝データの登録
    curs.execute("select email ,uid,cast(aes_decrypt(password, 'funa') as char) pwd from user where email = \'" + request.form["email"] + "\'")
    ds = curs.fetchall() # .fetchall＝レコードの結果を全部持ってくる
    curs.close()
    conn.close()

    session["uid"]=ds[0]["uid"]

    if len(ds)>0 and request.form["password"]==ds[0]["pwd"]:
        login_user(User(request.form["email"]))

        conn = mysql.connector.connect(host='localhost', user='funa', password='funa', database='merchandise')
        curs = conn.cursor(dictionary=True)
        # Create cursor and close.
        curs.execute('select * from item where uid=%s',(session["uid"],))
        ds = curs.fetchall()
        curs.close()

        # Close connection.
        conn.close()

        return render_template("itemlist.html",dataset=ds)

    return render_template("/login.html",target_id="inputBox",errormessage="ログインに失敗しました")

@app.route("/runlist")
def list():
    conn = mysql.connector.connect(host='localhost', user='funa', password='funa', database='merchandise')
    curs = conn.cursor(dictionary=True)
    sql = "select * from item where item.uid = %s"
    uid = session["uid"]
    curs.execute(sql, (uid,))
    ds = curs.fetchall()
    curs.close()
    conn.close()

    return render_template("itemlist.html", dataset=ds)

#全件表示
@app.route("/all",methods=["GET","POST"])
def all():
    conn = mysql.connector.connect(host='localhost', user='funa', password='funa', database='merchandise')
    curs = conn.cursor(dictionary=True)
    curs.execute("select * from item")
    ds = curs.fetchall()
    curs.close()
    conn.close()

    return render_template("itemlist.html", dataset=ds)

#新規商品登録
@app.route("/reg",methods=["GET","POST"])
@login_required
def reg():
    if request.method == "GET":
        # GETの場合はサインインページを表示
        return render_template("/reg.html")
    
    # POST（フォームsignin.htmlからのポスト）の場合
    conn = mysql.connector.connect(host='localhost', user='funa', password='funa', database='merchandise')
    curs = conn.cursor(dictionary=True)

    #新規登録が出来た場合、登録完了画面へ遷移
    sql = "insert into item (name, description,uid) values (%s, %s,%s)"
    curs.execute(sql , (request.form["name"] ,request.form["description"],session["uid"]))
    conn.commit()

    curs.execute('select * from item where uid=%s',(session["uid"],))
    ds = curs.fetchall()

    curs.close()
    conn.close()
    
    return redirect("/runlist")

#商品の削除
@app.route("/delete/<path:iid>")
def delete(iid):
    conn = mysql.connector.connect(host='localhost', user='funa', password='funa', database='merchandise')
    curs = conn.cursor(dictionary=True)
    sql = "delete from item where iid = %s"
    curs.execute(sql, (format(iid) ,))

    conn.commit()
    ds = curs.fetchall()
    
    curs.close()
    conn.close()

    return redirect("/runlist")

#商品の編集
@app.route("/edit/<path:iid>", methods=["GET", "POST"])
def edit(iid):
    if request.method == "GET":
        conn = mysql.connector.connect(host='localhost', user='funa', password='funa', database='merchandise')
        curs = conn.cursor(dictionary=True)
        curs.execute("select * from item where item.iid = %s", (format(iid) ,))
        ds = curs.fetchall()
        curs.close()
        conn.close()
        
        return render_template("edit.html",dataset=ds)
    
    #変更が出来た場合、商品一覧画面へ遷移
    conn = mysql.connector.connect(host='localhost', user='funa', password='funa', database='merchandise')
    curs = conn.cursor(dictionary=True)
    sql = "update item set name=%s, description=%s where iid=%s"

    curs.execute(sql , (request.form["name"] ,request.form["description"],format(iid)))
    conn.commit()

    curs.close()
    conn.close()
    
    return redirect("/runlist")
    

# サインアップの実施
@app.route("/signup" ,methods=["GET" ,"POST"])
def signup():
    if request.method == "GET":
        # GETの場合はサインインページを表示
        return render_template("/signup.html")
    
    # POST（フォームsignin.htmlからのポスト）の場合
    conn = mysql.connector.connect(host='localhost', user='funa', password='funa', database='merchandise')
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
    
    return render_template("/login.html",finmessage="登録完了しました。ログインしてください。")

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
    app.run(host="0.0.0.0" ,port=8888 ,debug=True)