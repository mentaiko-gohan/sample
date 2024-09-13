from flask import Flask, jsonify ,render_template
import mysql.connector

app = Flask(__name__)
app.json.ensure_ascii = False

@app.route('/')
def pgjson():

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

app.run(port=8900 ,debug=True)