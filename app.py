import sys
sys.path.append('/home/Jawahar.s/website_flask')

from flask import Flask,send_from_directory
from flask import Flask, redirect, url_for, request, render_template, session
import os
import math
import base64
from src import get_config
from src.User import User
from blueprints import home,api,files

application = app = Flask(__name__, static_folder='assets', static_url_path="/")
app.secret_key = get_config("secret_key")
# app.register_blueprint()

#TODO: Automate importing blueprints from blueprints folder

app.register_blueprint(home.bp)
app.register_blueprint(api.bp)
app.register_blueprint(files.bp)
# app.register_blueprint(motion.bp)

@app.after_request
def add_cache_control(response):
    response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache the response for 1 hour
    return response



if __name__ == '__main__':
   app.run(host='0.0.0.0', port=7000, debug=True)
