from flask import Blueprint, render_template, redirect, url_for, make_response, request, session, Response, send_file, send_from_directory, jsonify
from src.User import User
from werkzeug.utils import secure_filename
from src.Database import Database
from src.chatboxs import chatboxer

import mimetypes
import arrow
import os,time
import uuid
import re
import mimetypes
import imghdr
from PIL import Image

bp = Blueprint("files", __name__, url_prefix="/files")


@bp.route('/uploader', methods = ['GET', 'POST'])
def upload_filelk():
   
   if request.method == 'POST' and 'file' in request.files and 'text' in request.form and session.get('authenticated'):
      pattern = r'[~!#$%^&*()+{}\[\]:;"\'<>/\|\\]'

      f = request.files['file']
      t= request.form['text']
      filterdTxt=re.sub(pattern, '', t)
     
     
      if is_image_file(f):
         db = Database.get_connection()
         file_ext = os.path.splitext(f.filename)[1]
         filename=str(uuid.uuid4())
         #  f.save(filename+file_ext)
         #   folder="/home/jawa/Desktop/del/"+filename+file_ext
         filenam=filename+file_ext
         postid=filename
         fullpath="/home/Jawahar.s/website_flask/del/"+filenam
         f.save(fullpath)
      
         collection = db.photobook
         

        


         result = collection.insert_one({
            "postId":postid,
            "text":filterdTxt,
            "likes":0,
            "time":time.time(),
            "imageurl":filenam,
            "owner":session.get('username'),
            "likers":[]
           })
         return redirect(url_for('home.dashboard'))
         
      else:
         return{
               "data":"this image type is not accepted",
               "status":401
                   }
      

def is_image_file(file):
    # Check if the file is an image based on its content
    image_type = imghdr.what(file)
    return image_type is not None

@bp.route('/open/<filename>', methods=['GET','POST'])
def openImag(filename):
    m= mimetypes.guess_type(filename)[0]

    
    # filename="30b8c6a8-77f7-4461-9d16-23e1eecf44c2.JPG"
    #   return send_from_directory("/home/jawa/Desktop/del/",
    #                            filename, as_attachment=False)
    response = make_response(send_file("/home/Jawahar.s/website_flask/del/"+filename))
    response.headers['Content-Type'] = m
    return response
      
          
@bp.route('/getl',methods=['GET','POST'])
def getll():
    db = Database.get_connection()
    collection = db.photobook
    a=collection.find().sort('_id', -1)
    imurl = []

    if session.get('authenticated'):
        for document in a:
           timeHum=document['time']
           datetime_obj = arrow.get(timeHum)
           human_readable_time = datetime_obj.humanize()
           likedornot=document['likers']
           likedNot="like"
           Cssclass="btn-outline-primary"
           if session.get('username') in likedornot:
               likedNot="liked"
               Cssclass="btn-primary"
       
           imurl.append({
              "id":document['imageurl'].split('.')[0],
              "text":document['text'],
              "likes":document['likes'],
              "time":human_readable_time,
              "imageurl":document['imageurl'],
              "owner":document['owner'],
              "like":likedNot,
              "cssclasss":Cssclass
               })
    
   
        return jsonify(imurl)
    else:
        for document in a:
           timeHum=document['time']
           datetime_obj = arrow.get(timeHum)
           human_readable_time = datetime_obj.humanize()
       
       
           imurl.append({
              "id":document['imageurl'].split('.')[0],
              "text":document['text'],
              "likes":document['likes'],
              "time":human_readable_time,
              "imageurl":document['imageurl'],
              "owner":document['owner']
               })
    
   
        return jsonify(imurl)
  

@bp.route('/delete', methods=['POST'])
def delimg():
    #img url to del
    if 'imageid' in request.form and session.get('authenticated'):
     
        imgid=request.form['imageid']
        db = Database.get_connection()
        collection = db.photobook
        filter = {"imageurl":imgid}
        res=collection.find_one(filter)
        if(res['owner']==session.get('username')):
             
             result=collection.delete_one(filter)
             if result.deleted_count == 1:
                return{
                   "data":"success",
                   "status":200
                   }
             else:
                  return{
                   "data":"error",
                   "status":401
                   }

    else:
         return{
                 "data":"error",
                "status":401
                   }
      
     

@bp.route('/like', methods=['POST','GET'])
def likeimg():
   if session.get('authenticated') and 'imageid' in request.form :
        liker=session.get('username')
        postid=request.form['imageid']
        # postid="d7f43d04-b705-4e8f-9d49-029dd1dfba66"
        db = Database.get_connection()
        collection = db.photobook
        filter = {"postId":postid}
        res=collection.find_one(filter)
        a=res['likers']
        list_length = collection.aggregate([
                {"$match": {"postId": postid}},
                {"$project": {"list_length": {"$size": "$likers"}}}]).next()["list_length"]
        
       
        if liker in a:
            
            
            collection.update_one({"postId": postid},{
               "$pull": {"likers": liker},
                   "$set": {"likes": list_length-1}  # Modify the new string value as needed
              })
            
            return{
                "data":"unlike",
                "status":200
            } 
        else:
           
            
            # collection.update_one({"postId": postid}, update_query)
            collection.update_one({"postId": postid},{
               "$push": {"likers": liker},
                   "$set": {"likes": list_length+1}  # Modify the new string value as needed
              })
            
            return{
                "data": "liked",
                "status":200
            }
   else:
         return{
               "data":"error",
               "status":401
                   }




@bp.route('/chatUpdate', methods=['GET','POST'])
def chatupdt():
    if session.get('authenticated') and 'message' in request.form:
        username=session.get('username')
        mesid=str(uuid.uuid4())
        mesage=request.form['message']
        chatboxer.setChat(username,mesage,mesid)
        return "success"
    

    
@bp.route('/fetchChat', methods=['GET','POST'])
def fetchchat():
    if session.get('authenticated'):
        chatdata=chatboxer.getChat()
        return chatdata
    else:
        return "need auth"
        
