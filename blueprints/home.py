from flask import Blueprint, render_template, redirect, url_for, request, session, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename, safe_join
from src.User import User
import blueprints.files as bf
import requests,json
from src.Session import Session
import urllib.parse
import os

bp = Blueprint("home", __name__, url_prefix="/")

@bp.route("/")
def home():
     return render_template('index.html', session=session)

@bp.route("/resume")
def resume():
   return render_template('resume.html', session=session)

@bp.route("/projects")
def projects():
   return render_template('projects.html', session=session)

@bp.route("/contact")
def contact():
   return render_template('contact.html', session=session)

@bp.route("/login")
def login():
   return render_template('login.html', session=session)

@bp.route("/secret")
def secret():
   return render_template('secret.html', session=session)

@bp.route("/otpage")
def otpage():
   data_param = request.args.get('data', 'Default Value')
   return render_template('otpPage.html', session=session,data=data_param)

@bp.route("/register")
def register():
   return render_template('register.html', session=session)


@bp.route("/cctv")
def cctv():
   return render_template('cctv.html', session=session)

@bp.route("/dashboard")
def dashboard():
   sesExpiry=False
   try:
      ses=session['sessid']
      s=Session(ses)
      sesExpiry=s.is_valid()
   except:
      pass
   
   # url = 'http://127.0.0.1:7000/files/getl'  # Replace with the API URL you want to access
   # response = requests.get(url).json()

   dat=bf.getll()
   getAlldata=json.loads(dat.data)
   
   
   return render_template('dashboard.html', session=session,data=getAlldata,data2=sesExpiry)


@bp.route("/chatbox")
def chat():
   chatdt=bf.fetchchat()
   getallchat=json.loads(chatdt.data)
   return render_template('chatbox.html', session=session ,data=getallchat)



