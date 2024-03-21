from flask import Blueprint, render_template, redirect, url_for, request, session,jsonify
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
    # Check if all fields are present in the form data
    if all(field in request.form for field in ['username', 'password', 'name', 'email']):
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']

        # Simplistic check for username and password length
        if len(username) <= 5 or len(password) <= 8:
            return jsonify({"message": "Username or password too short"}), 400

        # Email format basic validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"message": "Invalid email address"}), 400

        try:
            # Directly pass the cleaned data to your User registration logic
            # This is a placeholder; replace with your actual User model registration logic
            uid = User.register(username, password,password, name, email)
            
            # Assuming the registration was successful, redirect or respond accordingly
            data_param = {'data': email}
            return redirect(url_for('home.otpage', **data_param))
        except Exception as e:
            # Handle any exceptions that arise during registration
            return jsonify({"message": str(e)}), 400
    else:
        # If any of the required fields are missing in the form data
        return jsonify({"message": "Not enough parameters"}), 400


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
         if not re.match(r'^[\w.@+-]+$', username):
               return jsonify({"message": "Invalid username", "authenticated": False}), 400
         try:
            sessid = User.login(username, password)
            session['authenticated'] = True
            session['username'] = username
            session['sessid'] = sessid
            
            if 'redirect' in request.form and request.form['redirect'] == 'true':
               return redirect(url_for('home.dashboard'))
            else:
               return redirect(url_for('home.dashboard'))
               
            
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
      elif a==244:
         return {
            "message": "OTP Already Sended",
            "look": "if you found any bugs report to me"
         }, 400

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

risky_commands = ['rm', 'shutdown','python', 'reboot','mv','apt','install','wget','curl','git','nc','&&','&','%','/']

@bp.route("/lincmds",methods=['POST','GET'])  
def execute_linux_command():
  
   if session.get('secret') and 'cmds' in request.form:
      command=request.form['cmds']
      # base_command = command.split()[0]

      if any(risky_cmd in command for risky_cmd in risky_commands):
         return {
            "message": "Ithu Not Allowed"
         }, 200
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
   
