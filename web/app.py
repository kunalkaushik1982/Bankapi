from operator import truediv
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.BankAPI
users = db["Users"]

def UserExist(username):
    if users.find({"Username":username}).count() == 0:
        return False
    else:
        return True
    
class Register(Resource):
    def post(self):
        postedData = request.get_json()
        
        username = postedData["username"]
        password = postedData["password"]
        
        if UserExist(username):
            retJson = {
                "status":"301",
                "msg": "Invalid Username"
            }
        return jsonify(retJson)

        hashed_pw = bcrypt.hashpw(password.encode('utf8'),bcrypt.gensalt())
        
        users.insert({
            "Username":username,
            "Password":hashed_pw,
            "Own":0,
            "Debt":0
        })
        
        retJson ={
            "status":200,
            "msg":"You successfully signed up for the API"
        }
        
        return jsonify(retJson)

def verifypw(username,password):
    if not UserExist(username):
        return False
    
    hashed_pw = users.find({
        "Username":username
        })[0]["password"]
    
    if bcrypt.hashpw(password.encode('utf8'),hashed_pw)==hashed_pw:
        return True
    else:
        return False
    
def cashWithUser(username):
    cash = users.find({
        "Username":username
    })[0]["Own"]
    return cash

def debtWithuser(username):
    debt = users.find({
        "Username":username
    })[0]["Debt"]
    return debt

def generateReturnDictionary(status,msg):
    retJson = {
        "status":status,
        "msg":msg
    }
    return retJson
#Error Dictionary True/False
def verifyCredentials(username,password):
    if not UserExist(username):
        return generateReturnDictionary(301,"Invalid username"),True
    
    correct_pw = verifypw(username,password)
    
    if not correct_pw:
        return generateReturnDictionary(302,"Invalid password"), truediv
    
    return None, False

def updateAccount(username,balance):
    users.update({
        "Username":username
    },{
        "$set":{
            "Own":balance
        }
    })
    
def updateDebt(username,balance):
    users.update({
        "Username":username
    },{
        "$Set":{
            "Debt":balance
        }
    })
    
class Add(Resource):
    def post(self):
        postedData = request.get_json()
        
        username = postedData["username"]
        password = postedData["password"]
        money = postedData["Amount"]
        
        retJson,error = verifyCredentials(username,password)
        
        if error:
            return jsonify(retJson)
        
        if money <= 0:
            return jsonify(generateReturnDictionary(304, "The amount entered must be greate than zero."))
        
        cash = cashWithUser(username)
        money-=1
        bank_cash = cashWithUser("BANK")
        updateAccount("BANK",bank_cash+1)
        updateAccount(username,cash+money)
        
        return jsonify(generateReturnDictionary(200, "Amount added succesfully to account"))
        