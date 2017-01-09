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
        cur.execute("SELECT itemId,itemCode,itemName,itemDescription,COALESCE((Item.itemQuantity - (SELECT SUM(BorrowedItem.itemQuantity) FROM BorrowedItem WHERE Item.itemId = BorrowedItem.itemId AND requestId IN (SELECT BorrowedItem.requestId FROM BorrowedItem WHERE BorrowedItem.issueDate IS NOT NULL AND returnDate IS NULL AND Item.itemId = BorrowedItem.itemId))),Item.itemQuantity) as itemAvailable FROM Item WHERE itemAvailable > 0")

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
        cur.execute("SELECT Request.requestId, Request.idNumber, Request.name, Request.subject, Request.requestDate, itemId, itemCode, itemName, itemDescription, itemQuantity, itemAvailable, issueDate, returnDate FROM (SELECT BorrowedItem.itemId,itemCode,itemName,itemDescription,BorrowedItem.itemQuantity, COALESCE((Item.itemQuantity - (SELECT SUM(BorrowedItem.itemQuantity) FROM BorrowedItem WHERE Item.itemId = BorrowedItem.itemId AND requestId IN (SELECT BorrowedItem.requestId FROM BorrowedItem WHERE BorrowedItem.issueDate IS NOT NULL AND returnDate IS NULL AND Item.itemId = BorrowedItem.itemId))),Item.itemQuantity) as itemAvailable, BorrowedItem.issueDate,BorrowedItem.returnDate,BorrowedItem.requestId as request FROM BorrowedItem,Item WHERE BorrowedItem.itemId = Item.itemId) LEFT JOIN Request ON request = Request.requestId WHERE requestID IS NOT NULL AND returnDate IS NULL GROUP BY requestId")
        rows = cur.fetchall()

        return render_template('modules/request.html', req = rows)


    @app.route('/getReq', methods=['GET'])
    def getReq():
        requestId = request.args.get('getid')
        con = sqlite3.connect("ZeeSlipv2.sqlite")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM (SELECT Request.requestId, Request.idNumber, Request.name, Request.subject, Request.requestDate, borrowedItemId,itemId, itemCode, itemName, itemDescription, itemQuantity, itemAvailable, issueDate, returnDate FROM (SELECT BorrowedItem.borrowedItemId,BorrowedItem.itemId,itemCode,itemName,itemDescription,BorrowedItem.itemQuantity, COALESCE((Item.itemQuantity - (SELECT SUM(BorrowedItem.itemQuantity) FROM BorrowedItem WHERE Item.itemId = BorrowedItem.itemId AND requestId IN (SELECT BorrowedItem.requestId FROM BorrowedItem WHERE BorrowedItem.issueDate IS NOT NULL AND returnDate IS NULL AND Item.itemId = BorrowedItem.itemId))),Item.itemQuantity) as itemAvailable, BorrowedItem.issueDate,BorrowedItem.returnDate,BorrowedItem.requestId as request FROM BorrowedItem,Item WHERE BorrowedItem.itemId = Item.itemId) LEFT JOIN Request ON request = Request.requestId WHERE returnDate IS NULL ORDER BY requestId ASC) WHERE requestId = ?",[requestId])
        borrowedlist = cur.fetchall()
        res = []
        for r in borrowedlist:
            res.append({'reqID': r[0], 'id': r[1], 'iname': r[2], 'subject':r[3],'britemid':r[5], 'itemID': r[6], 'itemcode':r[7], 'itemname':r[8], 'itemquan': r[10], 'issDate': r[12]})
        return jsonify({'res': res, 'count': len(res)})

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
            idNumber =  request.form['rqisnumber']
            name = request.form['rqname']
            subject = request.form['rqsubject']
            borroweditems = [] #list of tuples sa borrowed items i.e. [(121,10), ..., ]
            if request.method == 'POST':
                with sqlite3.connect("ZeeSlipv2.sqlite") as con:
                    cur = con.cursor()
                    cur.execute("INSERT INTO Request (idNumber,name,subject,requestDate) VALUES (?,?,?,?)", (idNumber,name,subject,"datetime(CURRENT_TIMESTAMP,'localtime')"))
                    con.commit()
                    cur.executemany("INSERT INTO BorrowedItem(itemId,itemQuantity,requestId) VALUES (?,?,(SELECT requestId FROM Request ORDER BY requestID DESC LIMIT 1))", borroweditems)
                    con.commit()
                    con.close()
            return redirect('dashboard/barrow')

    @app.route('/deleteRequest', methods=['GET'])
    def deleteRequest():
        requestId =  request.args.get('delreqid')
        with sqlite3.connect("ZeeSlipv2.sqlite") as con:
            cur = con.cursor()
            cur.execute("DELETE FROM Request WHERE requestId = ? AND EXISTS(SELECT requestId FROM (SELECT requestId FROM Request) LEFT JOIN (SELECT requestId as issuedRequestId FROM BorrowedItem WHERE issueDate IS NOT NULL) WHERE requestId != issuedRequestId)",[requestId])
            con.commit()

        return "ok"

    @app.route('/issueItem', methods=['GET'])
    def issueItem():
        borrowedItemId = request.args.get('issid')
        con = sqlite3.connect("ZeeSlipv2.sqlite")
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("UPDATE BorrowedItem SET issueDate = datetime(CURRENT_TIMESTAMP,'localtime') WHERE borrowedItemId = ?", [borrowedItemId])
        con.commit()
        con.close()
        return "ok"

    @app.route('/returnItem', methods=['GET'])
    def returnItem():
        borrowedItemId = request.args.get('retid')
        con = sqlite3.connect("ZeeSlipv2.sqlite")
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("UPDATE BorrowedItem SET returnDate = datetime(CURRENT_TIMESTAMP,'localtime') WHERE borrowedItemId = ?",[borrowedItemId])
        con.commit()
        con.close()
        return "ok"

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
