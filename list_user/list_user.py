from flask import Flask, jsonify
from flask import request
import pymongo
import json
import sys
import database1

# database part
app = Flask(__name__)
db_add = "mongodb2://192.168.35.128:27018/"

@app.route('/list_user', methods=['GET'])
def list_user():
    data1 = database1.main(db_add)
    return jsonify(data1)

@app.route('/')
def index():
    return 'Web App with Python Flask!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
