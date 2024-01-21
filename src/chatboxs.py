from src.Database import Database
from time import time
import json
from flask import  jsonify
import arrow


db = Database.get_connection()
users = db.chats 

class chatboxer:

    @staticmethod
    def setChat(username,message,messId):
        _id = users.insert_one({
                "mesId":messId,
                "username": username,
                "message":message,
                "time": time()
                
            })
        return str(_id)
    
    @staticmethod
    def getChat():
        list1=[]
        a=users.find()

        for document in a:
            datetime_obj = arrow.get(document['time'])
            human_readable_time = datetime_obj.humanize()
            mesid=document['mesId']
            messge=document['message']
            timen=document['time']
            username=document['username']

            list1.append({
                "mesid":mesid,
                "message":messge,
                "time":human_readable_time,
                "username":username
            })

        
        return jsonify(list1)
