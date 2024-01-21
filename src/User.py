import pymongo
from src.Database import Database
from time import time
from src import get_config
from random import randint
import bcrypt
from src.Session import Session
from mongogettersetter import MongoGetterSetter
from flask import Blueprint, render_template, redirect, url_for, request, session
from uuid import uuid4
import yagmail
import re

db = Database.get_connection()
users = db.users # create a collection users if it doesn't exist

class UserCollection(metaclass=MongoGetterSetter):
    def __init__(self, username):
        self._collection = db.users
        self._filter_query = {
            "$or": [
                {"username": username}, 
                {"id": username}
            ]
        }
class User:
    def __init__(self, id):
        self.collection = UserCollection(id)
        self.id = self.collection.id
        self.username = self.collection.username        
    
    @staticmethod
    def login(username, password):
        result = users.find_one({
            "username": username
        })
        if result:
            if(result['active']):
             
                hashedpw = result['password']
                if bcrypt.checkpw(password.encode(), hashedpw):
                    # TODO: Register a session and return a session ID on successful login
                    sess = Session.register_session(username, request=request)
                    
                    return sess.id
                else:
                   raise Exception("Incorrect Password")
            else:
                raise Exception("verify otp")
        else:
            raise Exception("Incorrect Credentials")

    @staticmethod
    def register(username, password, confirm_password, name, email):
        uuid = str(uuid4())
        or_query = {
           '$or': [
            {'username': username},
            {'email': email}, ]}
        
        result = users.find_one(or_query)
       
        if result:
            raise Exception("username or email is already used")


        else:
            if password != confirm_password:
                raise Exception("Password and Confirm Password do not match")
        
            password = password.encode()
            salt = bcrypt.gensalt() # like a secret key that is embedded into the password for verification purposes while logging in
            password = bcrypt.hashpw(password, salt)
            activeToken=randint(100000, 999999)
            _id = users.insert_one({
                "username": username, # TODO: Make as unique index to avoid duplicate entries
                "password": password,
                "register_time": time(),
                "active": False,
                "activate_token": activeToken,
                "id": uuid,
                "name": name,
                "email": email
            })
            User.otpsend(email,str(activeToken))
            
            return uuid



    @staticmethod
    def otpVerify(email,otp):
        result = users.find_one({
            "email": email
        })
        pattern = r'[~!#$%@^&*()+{}\[\]_:,;"\'<>/\|\\]'
        otp=re.sub(pattern, '', otp)
        

        if(result==None):
             return 444
       
        else:
            if(result['activate_token']==int(otp)):
                filter_criteria = {"email": email}
                update_data = {"$set": {"active": True}}
                users.update_one(filter_criteria, update_data)
                return True
            else:
                return False
        
                 


    @staticmethod
    def otpsend(gmail,otp):
        tomail=gmail
        Frommailadress=get_config('mailforotp')
        password=get_config('mailPass') 
        yag = yagmail.SMTP(user=Frommailadress, password=password)
        yag.send(to=tomail, subject=' Make it Easy', contents="Activation Token =  "+otp+" ")
        print("--------->successfully mail send")
    
