from flask import Flask, render_template, request, redirect, url_for, jsonify
from model import DBConn
import  sqlite3


app = Flask(__name__)
app.static_folder = 'static'
app.jinja_env


@app.route('/db', methods=['GET'])
def list():
   con = sqlite3.connect("ZeeSlip.sqlite")
   con.row_factory = sqlite3.Row

   cur = con.cursor()
   cur.execute("select * from Person")

   rows = cur.fetchall();

   recs = []
   for r in rows:
       recs.append({'Pid': r[0], 'idNum': r[1], 'fname': r[2], 'lname': r[3] })
   return jsonify({'list': recs})

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def auth():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect("ZeeSlipv2.sqlite") as con:
            cur = con.cursor()
            cur.execute("SELECT username,password FROM Account WHERE username = ? AND password = ?",(username,password))

            if cur.fetchone() is None:
                error = 'Invalid Credentials. Please try again.'
            else:
                return redirect(url_for('request'))

    return render_template('login.html', error = error)

@app.route('/logout')
def logout():
    return redirect(url_for('login'))




class zeebuks(Flask):
    @app.route('/borrow')
    def barrow():
        con = sqlite3.connect("ZeeSlipv2.sqlite")
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("SELECT itemId,itemCode,itemName,itemDescription,(Item.itemQuantity - (SELECT SUM(BorrowedItem.itemQuantity) FROM BorrowedItem WHERE Item.itemId = BorrowedItem.itemId AND requestId IN (SELECT requestId FROM Request WHERE releaseDate IS NOT NULL AND returnDate IS NULL))) as available FROM Item WHERE available > 0")

        rows = cur.fetchall();

        return render_template('requestor.html' , list = rows)
    @app.route('/dashboard')
    def index():
        return render_template('try.html')
    @app.route('/dashboard/request')
    def request():
        con = sqlite3.connect("ZeeSlipv2.sqlite")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT Request.requestId, Request.idNumber, Request.name, Request.subject, Request.requestDate, itemId, itemCode, itemName, itemDescription, itemQuantity, itemAvailable, issueDate, returnDate FROM (SELECT BorrowedItem.itemId,itemCode,itemName,itemDescription,BorrowedItem.itemQuantity, COALESCE((Item.itemQuantity - (SELECT SUM(BorrowedItem.itemQuantity) FROM BorrowedItem WHERE Item.itemId = BorrowedItem.itemId AND requestId IN (SELECT BorrowedItem.requestId FROM BorrowedItem WHERE BorrowedItem.issueDate IS NOT NULL AND returnDate IS NULL AND Item.itemId = BorrowedItem.itemId))),Item.itemQuantity) as itemAvailable, BorrowedItem.issueDate,BorrowedItem.returnDate,BorrowedItem.requestId as request FROM BorrowedItem,Item WHERE BorrowedItem.itemId = Item.itemId) LEFT JOIN Request ON request = Request.requestId WHERE returnDate IS NULL ORDER BY requestId ASC")
        rows = cur.fetchall()

        return render_template('modules/request.html', req = rows)


    @app.route('/getReq', methods=['GET'])
    def getReq():
        id = request.args.get('getid')
        con = sqlite3.connect("ZeeSlipv2.sqlite")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT  BorrowedItem.itemQuantity , itemName FROM Item, BorrowedItem, Request, Borrower WHERE Borrower.borrowerIdNumber = ? AND BorrowedItem.requestId = Borrower.requestId AND BorrowedItem.itemId = Item.itemId ", [id])
        borrowedlist = cur.fetchall()
        res = []
        for r in borrowedlist:
            res.append({'iq': r[0], 'iname': r[1]})
        return jsonify({'res': res})

    @app.route('/dashboard/items')
    def items():
        con = sqlite3.connect("ZeeSlipv2.sqlite")
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("SELECT itemId,itemCode,itemName,itemDescription,itemQuantity FROM Item")

        rows = cur.fetchall();

        return render_template('modules/items.html' , recs = rows)

    @app.route('/dashboard/account')
    def account():
        con = sqlite3.connect("ZeeSlipv2.sqlite")
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("SELECT username, lastname FROM Account")

        rows = cur.fetchall();
        return render_template('modules/account.html' ,  recs = rows)

    @app.route('/dashboard/logs')
    def logs():
        con = sqlite3.connect("ZeeSlipv2.sqlite")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT Request.requestId, Request.idNumber, Request.name, Request.subject, Request.requestDate, itemId, itemCode, itemName, itemDescription, itemQuantity, issueDate, returnDate FROM (SELECT BorrowedItem.itemId,itemCode,itemName,itemDescription,BorrowedItem.itemQuantity,BorrowedItem.issueDate,BorrowedItem.returnDate,BorrowedItem.requestId as request FROM BorrowedItem,Item WHERE BorrowedItem.itemId = Item.itemId) LEFT JOIN Request ON request = Request.requestId WHERE issueDate IS NOT NULL ORDER BY issueDate DESC")
        rows = cur.fetchall()
        return render_template('modules/logs.html', logs = rows)

    @app.route('/addItem', methods=['POST'])
    def addItem():
        code = request.form['parcode']
        name = request.form['parname']
        quan = request.form['parquan']
        dis = request.form['pardis']
        if request.method == 'POST':
            with sqlite3.connect("ZeeSlipv2.sqlite") as con:
                cur = con.cursor()
                cur.execute('INSERT INTO Item (itemCode,itemName,itemdescription,itemQuantity) VALUES (?,?,?,?)',(code,name,dis,quan))
                con.commit()
            return redirect('dashboard/items')

    @app.route('/deleteItem', methods=['GET'])
    def deleteItem():
        ids = request.args.get('delid')

        id = int(ids)

        with sqlite3.connect("ZeeSlipv2.sqlite") as con:
            cur = con.cursor()
            cur.execute('DELETE FROM Item WHERE itemId = ?', [ids])
            con.commit()
            #con.close()

        return "ok"

    @app.route('/updateItem', methods=['GET'])
    def updateItem():

        #id = request.form['updateid']
        #code = request.form['parcode']
        #name = request.form['parname']
        #quan = request.form['parquan']
        #dis = request.form['pardis']

        id = request.args.get('upid')
        code = request.args.get('upcode')
        name = request.args.get('upname')
        quan = request.args.get('upquan')
        dis = request.args.get('updis')


        with sqlite3.connect("ZeeSlipv2.sqlite") as con:
                cur = con.cursor()
                cur.execute('UPDATE Item SET itemCode = ?,itemName = ?,itemDescription = ?, itemQuantity = ? WHERE itemId = ?', (code, name, dis, quan, id))
                con.commit()

        return "ok"

    @app.route('/submitRequest', methods=['POST'])
    def submitRequest():
            borrower = [] #list of tuples sa borrower i.e. [(EE131,Sir Rogs), (EE171,Maam Lambino)... , (EC170, Sir Z)]
            borroweditems = [] #list of tuples sa borrowed items i.e. [(121,10), ..., ]
            if request.method == 'POST':
                with sqlite3.connect("ZeeSlipv2.sqlite") as con:
                    cur = con.cursor()
                    cur.execute("INSERT INTO Request (subject,instructor) VALUES (?,?)", (subject, instructor))
                    con.commit()
                    cur.executemany("INSERT INTO Borrower(borrowerIdNumber,borrowerName,requestId) VALUES (?,?,(SELECT requestId FROM Request ORDER BY requestID DESC LIMIT 1))", borrower)
                    con.commit()
                    cur.executemany("INSERT INTO BorrowedItem(itemId,itemQuantity,requestId) VALUES (?,?,(SELECT requestId FROM Request ORDER BY requestID DESC LIMIT 1))", borroweditems)
                    con.commit()
                    con.close()
            return redirect('dashboard/barrow')

    @app.route('/releaseItems', methods=['POST'])
    def releaseItems():
        id = None #request id sa items na i release
        borroweditems = []  # list of tuples sa borrowed items i.e. [(121,10), ..., ]
        if request.method == 'POST':
            with sqlite3.connect("ZeeSlipv2.sqlite") as con:
                cur = con.cursor()
                cur.execute("DELETE FROM BorrowedItem WHERE requestId = ?", id)
                con.commit()
                #ireplace daun sa final list sa items na hulamon
                cur.execute("INSERT INTO BorrowedItem(itemId,itemQuantity,requestId) VALUES (?,?,?)", borroweditems.append(id))
                con.commit()
                #iupdate daun ang request
                cur.execute("UPDATE Request SET releaseDate = CURRENT_TIMESTAMP WHERE requestId = ?", id)
                con.commit()
                con.close()
        return redirect('dashboard/request')

    @app.route('/returnItems', methods=['POST'])
    def returnItems():
        id = None #request id sa items na i uli
        if request.method == 'POST':
            with sqlite3.connect("ZeeSlipv2.sqlite") as con:
                cur = con.cursor()
                cur.execute("UPDATE Request SET releaseDate = CURRENT_TIMESTAMP WHERE returnId = ?", id)
                con.commit()
                con.close()
        return redirect('dashboard/request')


    @app.route('/addAccount', methods=['POST'])
    def addAcc():
        fname = request.form['newFname']
        lname = request.form['newLname']
        username = request.form['newusername']
        password = request.form['newpassword']
        repass = request.form['rnewpassword']

        error = None

        if (repass != password):
            error = 'Password didnt Match'
        else:
            if request.method == 'POST':
                with sqlite3.connect("ZeeSlipv2.sqlite") as con:
                    cur = con.cursor()
                    cur.execute('INSERT INTO Account (username,password,firstName,lastName) VALUES (?,?,?,?)',(username,password,fname,lname))
                    con.commit()
        return render_template('modules/account.html' ,  error = error)
    @app.route('/getmanAccount', methods=['POST'])
    def manAcc1():
        return jsonify({})

    @app.route('/manAccount', methods=['POST'])
    def manAcc():
        fname = request.form['newFname']
        lname = request.form['newLname']
        username = request.form['newusername']
        password = request.form['newpassword']
        repass = request.form['rnewpassword']

        error = None

        if (repass != password):
            error = 'Password didnt Match'
        else:
            if request.method == 'POST':
                with sqlite3.connect("ZeeSlipv2.sqlite") as con:
                    cur = con.cursor()
                    cur.execute('INSERT INTO Account (username,password,firstName,lastName) VALUES (?,?,?,?)',(username,password,fname,lname))
                    con.commit()
        return render_template('modules/account.html' ,  error = error)

if __name__ == '__main__':
    app.run()
    #app.run(host='192.168.30.1', port='80')
    #app.run(host='192.168.1.109', port='5000')
