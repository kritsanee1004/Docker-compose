from flask import Flask, render_template, request, jsonify, make_response, json, send_from_directory, redirect, url_for
import pika
import pymongo
import logging
import warnings
import bcrypt



# packages for swagger
from flasgger import Swagger
from flasgger import swag_from

# setup flask app
app = Flask(__name__)

# setup swagger online document
swagger = Swagger(app)

# setup logger
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
warnings.filterwarnings("ignore", category=DeprecationWarning)

#database connection
myclient = pymongo.MongoClient("mongodb://192.168.35.128:27017/")
mydb = myclient["mydatabase"]
users = mydb["key"]

def UserExist(username):
    if users.find({"Username":username}).count() == 0:
        return False
    else:
        return True

@app.route('/create_user', methods=['POST'])
@swag_from('apidocs/api_create_user.yml')
def create_user():
    postedData = request.get_json()

    #Get the data
    username = postedData["username"]
    password = postedData["password"] #"123xyz"

# push username and password
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.35.128', port=5672))
    channel = connection.channel()


    if UserExist(username):
        retJson = {
            'status':301,
            'msg': 'Invalid Username'
        }
        return jsonify(retJson)

    hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

    #Store username and pw into the database
    users.insert({
        "Username": username,
        "Password": hashed_pw,
        "Own":0,
        "Debt":0
    })

    retJson = {
        "status": 200,
        "msg": "You successfully signed up"
    }
    return jsonify(retJson)


def verifyPw(username, password):
    if not UserExist(username):
        return False

    hashed_pw = users.find({
        "Username":username
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def cashWithUser(username):
    cash = users.find({
        "Username":username
    })[0]["Own"]
    return cash

def debtWithUser(username):
    debt = users.find({
        "Username":username
    })[0]["Debt"]
    return debt

def generateReturnDictionary(status, msg):
    retJson = {
        "status": status,
        "msg": msg
    }
    return retJson

def verifyCredentials(username, password):
    if not UserExist(username):
        return generateReturnDictionary(301, "Invalid Username"), True

    correct_pw = verifyPw(username, password)

    if not correct_pw:
        return generateReturnDictionary(302, "Incorrect Password"), True

    return None, False

def updateAccount(username, balance):
    users.update({
        "Username": username
    },{
        "$set":{
            "Own": balance
        }
    })

def updateDebt(username, balance):
    users.update({
        "Username": username
    },{
        "$set":{
            "Debt": balance
        }
    })


@app.route('/balance', methods=['POST'])
@swag_from('apidocs/api_balance.yml')
def balance():
    postedData = request.get_json()

    username = postedData["username"]
    password = postedData["password"]

    retJson, error = verifyCredentials(username, password)
    if error:
        return jsonify(retJson)

    retJson = users.find({
        "Username": username
    },{
        "Password": 0, #projection
        "_id":0
    })[0]

    return jsonify(retJson)

@app.route('/take_loan', methods=['POST'])
@swag_from('apidocs/api_take_loan.yml')
def take_loan():
    postedData = request.get_json()

    username = postedData["username"]
    password = postedData["password"]
    money    = postedData["amount"]

    retJson, error = verifyCredentials(username, password)
    if error:
        return jsonify(retJson)

    cash = cashWithUser(username)
    debt = debtWithUser(username)
    updateAccount(username, cash+money)
    updateDebt(username, debt + money)

    return jsonify(generateReturnDictionary(200, "Loan Added to Your Account"))

@app.route('/pay_loan', methods=['POST'])
@swag_from('apidocs/api_pay_loan.yml')
def pay_loan():
    postedData = request.get_json()

    username = postedData["username"]
    password = postedData["password"]
    money    = postedData["amount"]

    retJson, error = verifyCredentials(username, password)
    if error:
        return jsonify(retJson)

    cash = cashWithUser(username)

    if cash < money:
        return jsonify(generateReturnDictionary(303, "Not Enough Cash in your account"))

    debt = debtWithUser(username)
    updateAccount(username, cash-money)
    updateDebt(username, debt - money)

    return jsonify(generateReturnDictionary(200, "Loan Paid"))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
