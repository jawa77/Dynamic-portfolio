from flask import Blueprint, render_template, redirect, url_for, request, session
from src.User import User
from src.Session import Session
from src.Database import Database
from src import get_config
import re
import sys
import psutil
import subprocess
bp = Blueprint("apiv1", __name__, url_prefix="/api/v1/")

db = Database.get_connection()

@bp.route("/register", methods=['POST'])
def register():
   if 'username' in request.form and 'password' in request.form and 'name' in request.form and 'email' in request.form:
      username = request.form['username']
      password = request.form['password']
      name = request.form['name']
      email = request.form['email']
      pattern = r'[~!#$%^&*()+{}\[\]_:,;"\'<>/\|\\]'
      username=re.sub(pattern, '', username)
      email=re.sub(pattern, '', email)
      name=re.sub(pattern, '', name)
      try:
         uid = User.register(username, password, password, name, email)
         
         data_param = {'data': email}
         return redirect(url_for('home.otpage',**data_param))
         # return {
         #    "message": "Successfully Registered",
         #    "user_id": uid
         # }, 200
      except Exception as e:
         return {
            "message": str(e),
         }, 400
   else:
      return {
         "message": "Not enough parameters",
      }, 400

@bp.route("/auth", methods=['POST'])
def authenticate():
   if session.get('authenticated'): #TODO: Need more validattion like login expiry
     
      sess = Session(session['sessid'])

      if sess.is_valid():
         return redirect(url_for('home.dashboard'))
         # return {
         #    "message": "Already Authenticated",
         #    "authenticated": True
         # }, 202
      else:
         session['authenticated'] = False
         sess.collection.active = False
         return {
            "message": "Session Expired",
            "authenticated": False
         }, 401
   else:
      if 'username' in request.form and 'password' in request.form:
         username = request.form['username']
         password = request.form['password']
         pattern = r'[~!#$%^&*()+{}\[\]_:,;"\'<>/\|\\]'
         username=re.sub(pattern, '', username)
         try:
            sessid = User.login(username, password)
            session['authenticated'] = True
            session['username'] = username
            session['sessid'] = sessid
            
            if 'redirect' in request.form and request.form['redirect'] == 'true':
               return redirect(url_for('home.dashboard'))
            else:
               return redirect(url_for('home.dashboard'))
               # return {
               #    "message": "Successfully Authenticated",
               #    "authenticated": True,
               #    # "session_id": sessid,
               #    "username": username
               # }, 200
               
            
         except Exception as e:
            return {
               "message": str(e),
               "authenticated": False
            }, 401
      else:
         return {
            "message": "Not enough parameters",
            "authenticated": False
         }, 400

@bp.route("/deauth")
def deauth():
   if session.get('authenticated'): #TODO: Need more validattion like login expiry
      #Remove / invalidate session from database
      session['authenticated'] = False
      session['secret']=False
      session['username']= " Pls Login"
      # return {
      #    "message": "Successfully Deauthed",
      #    "authenticated": False
      # }, 200
      return redirect(url_for('home.dashboard'))
   else:
      return {
         "message": "Not Authenticated",
         "authenticated": False
      }, 200

@bp.route("/otpverify",methods=['POST'])
def otpverify():
   if 'email' in request.form and 'otp' in request.form:
      email = request.form['email']
      otp = request.form['otp']
     
      a=User.otpVerify(email,otp)
      if a==True:
         return redirect(url_for('home.login'))
      elif a==444:
         return {
            "message": "Don't try to hack ",
            "look": "if you found any bugs report to me"
         }, 400
      else:
         return {
            "message": "Wrong Otp Go back and try again ",
            "otp check": False
         }, 400
   else:
         return {
            "message": "Not enough parameters",
            "authenticated": False
         }, 400


@bp.route("/secret",methods=['POST','GET'])
def secret():
   if 'text' in request.form and session.get('authenticated'):
      token=request.form['text']
      if token==get_config('secretPass'):
         session['secret']=True
         return redirect(url_for('home.secret'))
      else:
         return {
            "message": "wrong access key",
            "authenticated": False
         }, 400
   else:
      return redirect(url_for('home.login'))
   
@bp.route("/lincmds",methods=['POST','GET'])  
def execute_linux_command():
  
   
   if session.get('secret') and 'cmds' in request.form:
      command=request.form['cmds']
      print(command)
      try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
      
        return {
            "message": result.stdout.strip()
         }, 200
    
      except subprocess.CalledProcessError as e:
        return {
            "message": f"Error: {e}"
         }, 400
   else:
       return {
            "message": "you need access"
         }, 400



@bp.route("/cpuACTusr",methods=['POST','GET'])  
def cpuActusr():
   if session.get('secret'):
      users = db.users
      query = {"active": True}
      document_count = users.count_documents({}) 
      cpu_percentage = psutil.cpu_percent(interval=1)
      return{
         "cpu":cpu_percentage,
         "user":document_count
      }
      
      
@bp.route("/secLogout")
def seclogout():
   if session.get('authenticated'): 
      session['secret']=False
      return redirect(url_for('home.dashboard'))
   else:
      return {
         "message": "you are not secret",
         "authenticated": False
      }, 200
   
